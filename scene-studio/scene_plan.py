"""Read a reference image with a local vision model; return data, never code."""
import base64
import json
import math
import os
import urllib.error
import urllib.request

TYPES=['terrain','mountain','building','tower','dome','dish','vehicle','spacecraft','person','tree','river','wall','column','platform','planet','rock','chibi','chick','hippo','cow','gorilla']
SCHEMA={'type':'object','properties':{'name':{'type':'string'},'objects':{'type':'array','items':{'type':'object','properties':{'name':{'type':'string'},'type':{'type':'string','enum':TYPES},'position':{'type':'array','items':{'type':'number'},'minItems':3,'maxItems':3},'size':{'type':'array','items':{'type':'number'},'minItems':3,'maxItems':3},'rotationY':{'type':'number'},'color':{'type':'string'}},'required':['name','type','position','size','rotationY','color']}},'camera':{'type':'object','properties':{'position':{'type':'array','items':{'type':'number'}},'target':{'type':'array','items':{'type':'number'}}},'required':['position','target']}},'required':['name','objects','camera']}
PROMPT='''Describe this image as an editable LOW-POLY 3D PREVIZ set, not a single object. Return JSON matching the schema. Include visible environment, terrain, structures, vehicles, props and people. Use allowed template types. A template is an approximate representative, not an exact reconstruction. Preserve the image's relative layout and landmarks. Coordinate convention: X right, Y up, Z toward viewer; ground Y=0. position is center of footprint at ground level, size is width,height,depth in approximate scene units. Typical human height=1.8. Put distant structures at negative Z, foreground objects at positive Z. A planet is a large sphere well behind the set. Terrain may be wide and shallow; heights for buildings are positive. Use 5 to 35 meaningful objects. Camera position and target should reproduce the reference composition. Do not return code, filenames, instructions or API calls. Do not embed image pixels. Colors must be six-digit hex strings. Describe only visible evidence; unseen geometry uses simple closed templates.'''


def vector(value, minimum, maximum):
    if not isinstance(value,list) or len(value)!=3 or any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or not minimum<=x<=maximum for x in value):
        raise ValueError('Tọa độ/kích thước do model trả về không hợp lệ')
    return value


def validate(plan):
    if not isinstance(plan,dict) or not isinstance(plan.get('objects'),list) or not 1<=len(plan['objects'])<=100:raise ValueError('Bố cục phải có 1–100 vật thể')
    clean={'name':str(plan.get('name','Bối cảnh theo ảnh'))[:100],'objects':[]}
    for item in plan['objects']:
        if not isinstance(item,dict) or item.get('type') not in TYPES:raise ValueError('Loại khối không hỗ trợ')
        color=item.get('color','#b8afa0')
        if not isinstance(color,str) or len(color)!=7 or color[0]!='#' or any(c not in '0123456789abcdefABCDEF' for c in color[1:]):raise ValueError('Màu không hợp lệ')
        rotation=item.get('rotationY',0)
        if isinstance(rotation,bool) or not isinstance(rotation,(int,float)) or not math.isfinite(rotation) or abs(rotation)>360:raise ValueError('Góc xoay không hợp lệ')
        clean['objects'].append({'name':str(item.get('name',item['type']))[:100],'type':item['type'],'position':vector(item.get('position'),-500,500),'size':vector(item.get('size'),.01,1000),'rotationY':rotation,'color':color})
    camera=plan.get('camera',{})
    clean['camera']={'position':vector(camera.get('position'),-1000,1000),'target':vector(camera.get('target'),-1000,1000)}
    return clean


def from_image(path, character=False):
    model=os.environ.get('LS_VISION_MODEL','qwen2.5vl:3b')
    image=base64.b64encode(path.read_bytes()).decode('ascii')
    body=json.dumps({'model':model,'stream':False,'format':SCHEMA,'messages':[{'role':'user','content':PROMPT + (' This is a CHARACTER reference. Return exactly one representative rigged template from person/chibi/chick/hippo/cow/gorilla. Choose the closest silhouette and dominant body color, size roughly [1,2,1], position [0,0,0]. Do not claim exact face/clothes. Camera [3,2,5], target [0,1,0].' if character else ''),'images':[image]}],'options':{'temperature':0,'num_ctx':8192}}).encode()
    request=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=body,headers={'Content-Type':'application/json'})
    # Ollama is a local service; do not send the private photo through an HTTP proxy.
    local=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with local.open(request,timeout=900) as response:result=json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'Ollama báo HTTP {exc.code}. Kiểm tra đã tải model: ollama pull {model}') from exc
    except urllib.error.URLError as exc:
        raise RuntimeError('Chưa kết nối được Ollama local. Cài Ollama, mở Ollama rồi chạy: ollama pull '+model) from exc
    return validate(json.loads(result['message']['content']))
