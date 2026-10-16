"""Single-photo scene approximation: learned depth + instance segmentation + TripoSR.
Visible background is a depth mesh, NOT a completed hidden room. Instance models
are independently editable; relative placement/scale are estimates, not measurements.
"""
import gc
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
import torch
import trimesh


def depth_mesh(rgb, depth, removed):
    height,width=depth.shape
    focal=.8*width
    yy,xx=np.mgrid[:height,:width]
    vertices=np.stack(((xx-width/2)*depth/focal,(height/2-yy)*depth/focal,-depth),axis=-1).reshape(-1,3)
    valid=~removed
    faces=[]
    for y in range(height-1):
        for x in range(width-1):
            a=y*width+x;b=a+1;c=a+width;d=c+1
            for tri in [(a,c,b),(b,c,d)]:
                points=np.array(tri)
                if valid.reshape(-1)[points].all() and np.ptp(depth.reshape(-1)[points])<.6:faces.append(tri)
    if not faces:raise ValueError('Không tạo được bề mặt nền từ độ sâu.')
    mesh=trimesh.Trimesh(vertices=vertices,faces=np.array(faces),vertex_colors=rgb.reshape(-1,3),process=False)
    mesh.remove_unreferenced_vertices()
    return mesh


def reconstruct(folder, profile, engine):
    from transformers import pipeline, AutoImageProcessor, Mask2FormerForUniversalSegmentation
    folder=Path(folder)
    with Image.open(folder/'input.png') as source:
        if source.width*source.height>40_000_000:raise ValueError('Ảnh tối đa 40 triệu pixel')
        image=ImageOps.exif_transpose(source).convert('RGB')
    image.thumbnail((1024,1024))
    print('Ước lượng độ sâu bằng Depth Anything Small…',flush=True)
    estimator=pipeline('depth-estimation',model='LiheYoung/depth-anything-small-hf',device=-1)
    with torch.inference_mode():prediction=estimator(image)['predicted_depth']
    size=(160, max(32,round(160*image.height/image.width)))
    if size[1]>192:size=(max(32,round(192*image.width/image.height)),192)
    inverse=np.array(Image.fromarray(prediction.squeeze().float().numpy()).resize(size,Image.Resampling.BILINEAR))
    lo,hi=np.percentile(inverse,[2,98]);normalized=np.clip((inverse-lo)/max(float(hi-lo),1e-6),0,1)
    depth=2+6*(1-normalized)
    del estimator,prediction;gc.collect()
    print('Tách các vật thể trong ảnh bằng Mask2Former…',flush=True)
    processor=AutoImageProcessor.from_pretrained('facebook/mask2former-swin-small-coco-instance')
    segmenter=Mask2FormerForUniversalSegmentation.from_pretrained('facebook/mask2former-swin-small-coco-instance').eval()
    with torch.inference_mode():
        inputs=processor(images=image,return_tensors='pt')
        output=segmenter(**inputs)
        result=processor.post_process_instance_segmentation(output,target_sizes=[(image.height,image.width)],threshold=.65)[0]
    segmentation=result['segmentation'].cpu().numpy()
    regions=[]
    for segment in result['segments_info']:
        mask=segmentation==segment['id'];ys,xs=np.where(mask)
        if len(xs)<image.width*image.height*.008:continue
        box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
        if min(box[2]-box[0],box[3]-box[1])<12:continue
        regions.append((int(mask.sum()),mask,box,segmenter.config.id2label[segment['label_id']]))
    regions.sort(key=lambda r:r[0],reverse=True)
    limit=3 if profile=='low' else 6
    skipped=max(0,len(regions)-limit);regions=regions[:limit]
    del segmenter,processor,output,inputs,result;gc.collect()
    # Only remove successfully reconstructed instances; failed crops stay in background.
    removed=np.zeros((size[1],size[0]),dtype=bool)
    scene=trimesh.Scene();warnings=[];built=0
    for index,(_,mask,box,label) in enumerate(regions):
        print(f'Dựng vật {index+1}/{len(regions)}: {label}',flush=True)
        rgba=np.array(image.convert('RGBA'));rgba[:,:,3]=mask.astype(np.uint8)*255
        crop_path=folder/f'object-{index}.png';Image.fromarray(rgba).crop(box).save(crop_path)
        try:
            generated=engine.generate(str(crop_path),'Tiết kiệm RAM / VRAM','Tự động',False,lambda *a,**k:None)
            mesh=trimesh.load(generated[1],force='mesh')
            extent=mesh.extents
            if not np.isfinite(extent).all() or extent[1]<=0:raise ValueError('Mesh rỗng')
            small_mask=np.array(Image.fromarray(mask).resize(size,Image.Resampling.NEAREST)).astype(bool)
            distance=float(np.median(depth[small_mask])) if small_mask.any() else 4
            focal=.8*image.width
            center=np.array([((box[0]+box[2])/2-image.width/2)*distance/focal,(image.height/2-(box[1]+box[3])/2)*distance/focal,-distance])
            scale=(box[3]-box[1])*distance/focal/extent[1]
            mesh.apply_translation(-mesh.bounds.mean(axis=0));mesh.apply_scale(scale);mesh.apply_translation(center)
            scene.add_geometry(mesh,node_name=f'{label} · AI {index+1}',geom_name=f'object-{index}')
            removed|=small_mask;built+=1
        except Exception as exc:warnings.append(f'{label}: {type(exc).__name__}: {str(exc)[:180]}')
    rgb=np.array(image.resize(size,Image.Resampling.LANCZOS))
    background=depth_mesh(rgb,depth,removed)
    scene.add_geometry(background,node_name='Nền nhìn thấy · depth mesh (phần khuất chưa dựng)',geom_name='background')
    offset=-scene.bounds[0,1]
    scene.apply_translation([0,offset,0])
    scene.export(folder/'model.glb')
    report={'objects':built,'skipped':skipped,'warnings':warnings,'note':'Bố cục và kích thước ước lượng. Nền là bề mặt theo độ sâu ảnh, không có phần khuất. COCO chỉ nhận một số loại vật; vật không nhận ra còn trên nền.'}
    (folder/'report.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
