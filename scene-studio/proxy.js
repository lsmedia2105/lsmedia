import * as THREE from 'three';
import {avatar,avatarTypes} from './avatars.js';
const kinds=new Set(['terrain','mountain','building','tower','dome','dish','vehicle','spacecraft','person','tree','river','wall','column','platform','planet','rock',...avatarTypes]);
export function buildProxy(item){
 if(!kinds.has(item.type)||!Array.isArray(item.size)||item.size.length!==3||!item.size.every(n=>Number.isFinite(n)&&n>0&&n<=1000)||!Array.isArray(item.position)||item.position.length!==3||!item.position.every(n=>Number.isFinite(n)&&Math.abs(n)<=500)||!/^#[0-9a-f]{6}$/i.test(item.color))throw Error('Thành phần bố cục không hợp lệ');
 const root=new THREE.Group();root.name=String(item.name||item.type).slice(0,100);root.userData={source:'Bố cục ảnh · model đại diện',proxyType:item.type};
 const main=new THREE.MeshStandardMaterial({color:item.color,roughness:.85,side:THREE.DoubleSide}),dark=new THREE.MeshStandardMaterial({color:0x364350,roughness:.8}),glass=new THREE.MeshStandardMaterial({color:0x91b8c5,metalness:.2,roughness:.3});
 const mesh=(g,x,y,z,m=main)=>{const n=new THREE.Mesh(g,m);n.position.set(x,y,z);root.add(n);return n;};
 const box=(x,y,z,w,h,d,m=main)=>mesh(new THREE.BoxGeometry(w,h,d),x,y,z,m);
 const cyl=(x,y,z,r,h,m=main)=>mesh(new THREE.CylinderGeometry(r,r,h,16),x,y,z,m);
 switch(item.type){
 case 'terrain':{box(0,-.05,0,1,.1,1);const g=new THREE.PlaneGeometry(1,1,40,40);g.rotateX(-Math.PI/2);const p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i);p.setY(i,.09*Math.sin(x*17)*Math.cos(z*13)+.04*Math.sin((x+z)*31));}g.computeVertexNormals();mesh(g,0,0,0);break;}
 case 'mountain':mesh(new THREE.ConeGeometry(.5,1,9,3),0,.5,0);break;
 case 'rock':mesh(new THREE.IcosahedronGeometry(.5,1),0,.5,0);break;
 case 'planet':mesh(new THREE.SphereGeometry(.5,32,20),0,.5,0);break;
 case 'dome':mesh(new THREE.SphereGeometry(.5,24,12,0,Math.PI*2,0,Math.PI/2),0,.1,0,glass).scale.y=1.8;cyl(0,.05,0,.5,.1);break;
 case 'tower':cyl(0,.45,0,.16,.9);box(0,.5,0,.25,1,.2);cyl(0,.05,0,.42,.1);mesh(new THREE.TorusGeometry(.44,.025,6,32),0,.65,0,dark).rotation.x=Math.PI/2;mesh(new THREE.ConeGeometry(.12,.16,8),0,.98,0);break;
 case 'dish':cyl(0,.25,0,.07,.5,dark);mesh(new THREE.SphereGeometry(.47,24,12,0,Math.PI*2,Math.PI/2,Math.PI/2),0,.96,0).scale.y=1.1;box(0,.04,0,.5,.08,.5,dark);break;
 case 'vehicle':box(0,.4,0,.8,.35,.8);box(0,.7,-.1,.6,.3,.45,glass);for(const x of [-.4,.4])for(const z of [-.3,.3]){const wheel=cyl(x,.2,z,.2,.12,dark);wheel.rotation.z=Math.PI/2;}break;
 case 'spacecraft':{const body=mesh(new THREE.OctahedronGeometry(.5),0,.35,0);body.scale.set(1,.5,1);box(0,.2,0,1,.08,.45,dark);mesh(new THREE.SphereGeometry(.17,12,8),0,.5,-.05,glass);for(const x of [-.3,.3])box(x,.07,.2,.07,.14,.12,dark);break;}
 case 'person':case 'chibi':case 'chick':case 'hippo':case 'cow':case 'gorilla':{root.add(avatar(item.type,item.color));root.userData.rig=true;break;}
 case 'tree':cyl(0,.3,0,.06,.6,dark);mesh(new THREE.ConeGeometry(.5,.6,9),0,.7,0);break;
 case 'river':box(0,.01,0,1,.02,1,glass);break;
 case 'wall':box(0,.5,0,1,1,1);break;
 case 'column':cyl(0,.5,0,.32,1);cyl(0,.04,0,.5,.08);cyl(0,.96,0,.5,.08);break;
 case 'platform':cyl(0,.04,0,.5,.08);break;
 default:box(0,.4,0,1,.8,1);box(0,.9,0,.8,.2,.8,dark);
 }
 root.position.fromArray(item.position);root.scale.fromArray(item.size);root.rotation.y=THREE.MathUtils.degToRad(Number.isFinite(item.rotationY)?item.rotationY:0);return root;
}
