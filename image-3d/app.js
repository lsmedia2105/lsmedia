import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {GLTFExporter} from './vendor/GLTFExporter.js';
import {STLExporter} from './vendor/STLExporter.js';
const $=id=>document.getElementById(id), view=$('viewport');
let renderer;
try { renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); }
catch { $('status').textContent='Trình duyệt cần bật WebGL để xem mô hình 3D.'; throw new Error('WebGL unavailable'); }
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0x000000,0);view.prepend(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,1,.1,2000);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x526079,2.5));const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(-60,100,120);scene.add(light);
const grid=new THREE.GridHelper(300,30,0x425363,0x293743);grid.position.y=-72;scene.add(grid);
let mesh=null,image=null,texture=null,fileName='image-3d',busy=false;
function reset(){camera.position.set(105,65,180);controls.target.set(0,0,0);controls.update();}reset();
new ResizeObserver(()=>{const w=view.clientWidth,h=view.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(view);
renderer.setAnimationLoop(()=>{controls.autoRotate=$('rotate').checked;controls.update();renderer.render(scene,camera);});
$('reset').onclick=reset;$('choose').onclick=()=>$('file').click();
function message(t){$('status').textContent=t;}
function rebuild(){
 if(!image)return;
 const segments=+$('quality').value, aspect=image.width/image.height,w=aspect>=1?100:100*aspect,h=aspect>=1?100/aspect:100;
 const nx=Math.max(2,Math.round(segments*w/100)),ny=Math.max(2,Math.round(segments*h/100));
 const canvas=document.createElement('canvas');canvas.width=nx+1;canvas.height=ny+1;const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(image,0,0,canvas.width,canvas.height);const pixels=ctx.getImageData(0,0,canvas.width,canvas.height).data;
 const positions=[],uv=[],indices=[],row=nx+1,count=(nx+1)*(ny+1),base=+$('base').value,depth=+$('depth').value;
 for(let layer=0;layer<2;layer++)for(let y=0;y<=ny;y++)for(let x=0;x<=nx;x++){
  const i=(y*row+x)*4;let lum=(.2126*pixels[i]+.7152*pixels[i+1]+.0722*pixels[i+2])/255; if($('invert').checked)lum=1-lum;
  positions.push((x/nx-.5)*w,(.5-y/ny)*h,layer===0?base+lum*depth:0);uv.push(x/nx,1-y/ny);
 }
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){const a=y*row+x,b=a+1,c=a+row,d=c+1;indices.push(a,c,b,b,c,d,a+count,b+count,c+count,b+count,d+count,c+count);}
 const perimeter=[];for(let x=0;x<=nx;x++)perimeter.push(x);for(let y=1;y<=ny;y++)perimeter.push(y*row+nx);for(let x=nx-1;x>=0;x--)perimeter.push(ny*row+x);for(let y=ny-1;y>0;y--)perimeter.push(y*row);
 for(let i=0;i<perimeter.length;i++){const a=perimeter[i],b=perimeter[(i+1)%perimeter.length];indices.push(a,b,a+count,b,b+count,a+count);}
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.setIndex(indices);geometry.computeVertexNormals();geometry.translate(0,0,-(base+depth)/2);
 const material=new THREE.MeshStandardMaterial({map:$('texture').checked?texture:null,color:$('texture').checked?0xffffff:0xc9ddb5,roughness:.8,metalness:0,wireframe:$('wire').checked});
 if(mesh){scene.remove(mesh);mesh.geometry.dispose();mesh.material.dispose();}mesh=new THREE.Mesh(geometry,material);mesh.name='Image relief';scene.add(mesh);
 $('stats').textContent=`${(count*2).toLocaleString('vi')} ĐỈNH · ${(indices.length/3).toLocaleString('vi')} TAM GIÁC`;
 $('empty').hidden=true;$('glb').disabled=false;$('stl').disabled=false;message('Mô hình đã sẵn sàng · Kéo để xoay xem');
}
async function load(file){
 if(!file)return;if(!['image/png','image/jpeg','image/webp'].includes(file.type)){message('Hãy chọn ảnh PNG, JPG hoặc WEBP.');return;}if(file.size>15*1024*1024){message('Ảnh vượt quá 15 MB. Hãy chọn ảnh nhỏ hơn.');return;}
 const url=URL.createObjectURL(file);message('Đang đọc ảnh…');
 try{const next=new Image();next.src=url;await next.decode();if(next.width*next.height>40000000)throw new Error('Ảnh quá lớn: tối đa 40 triệu điểm ảnh.');image=next;fileName=file.name.replace(/\.[^.]+$/,'')||'image-3d';if(texture)texture.dispose();texture=new THREE.Texture(image);texture.colorSpace=THREE.SRGBColorSpace;texture.needsUpdate=true;$('thumbnail').src=next.src;$('thumbnail').hidden=false;rebuild();reset();}
 catch(e){message('Không thể đọc ảnh. '+e.message);}finally{URL.revokeObjectURL(url);}
}
$('file').onchange=e=>load(e.target.files[0]);
for(const event of ['dragenter','dragover'])$('drop').addEventListener(event,e=>{e.preventDefault();$('drop').classList.add('over');});
$('drop').addEventListener('dragleave',()=>$('drop').classList.remove('over'));
$('drop').addEventListener('drop',e=>{e.preventDefault();$('drop').classList.remove('over');load(e.dataTransfer.files[0]);});
for(const id of ['depth','base','quality','invert','texture','wire'])$(id).addEventListener('input',()=>{$('depthValue').textContent=$('depth').value;$('baseValue').textContent=$('base').value;rebuild();});
function download(data,type,ext){const url=URL.createObjectURL(new Blob([data],{type}));const a=document.createElement('a');a.href=url;a.download=fileName+'.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),3000);}
async function exportModel(kind){if(!mesh||busy)return;busy=true;$('glb').disabled=$('stl').disabled=true;message('Đang xuất '+kind.toUpperCase()+'…');try{const copy=new THREE.Mesh(mesh.geometry,mesh.material.clone());copy.material.wireframe=false;if(kind==='glb'){const buffer=await new GLTFExporter().parseAsync(copy,{binary:true});download(buffer,'model/gltf-binary','glb');}else{const data=new STLExporter().parse(copy,{binary:true});download(data,'application/octet-stream','stl');}copy.material.dispose();message('Đã xuất '+kind.toUpperCase()+'. Kiểm tra thư mục tải xuống.');}catch(e){message('Xuất file thất bại: '+e.message);}finally{busy=false;$('glb').disabled=$('stl').disabled=false;}}
$('glb').onclick=()=>exportModel('glb');$('stl').onclick=()=>exportModel('stl');
$('demo').onclick=()=>{const c=document.createElement('canvas');c.width=c.height=512;const x=c.getContext('2d');const g=x.createRadialGradient(256,240,5,256,256,310);g.addColorStop(0,'#f1f9d7');g.addColorStop(.6,'#829c63');g.addColorStop(1,'#1b3439');x.fillStyle=g;x.fillRect(0,0,512,512);x.fillStyle='#f1f9d7';x.font='bold 180px sans-serif';x.textAlign='center';x.fillText('LS',256,310);c.toBlob(b=>load(new File([b],'LS-demo.png',{type:'image/png'})));};
