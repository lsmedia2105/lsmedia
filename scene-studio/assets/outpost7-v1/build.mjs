import * as T from 'three';
import {mergeGeometries} from '../../vendor/BufferGeometryUtils.js';
export const cameraPose={position:[27,10,46],target:[0,5,-5],lens:32};
export function createOutpost(){
 const root=new T.Group();root.name='TERRAN RESEARCH OUTPOST-7 · V1';
 let seed=72817;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
 const mat=(color,metalness=.25,roughness=.7)=>new T.MeshStandardMaterial({color,metalness,roughness});
 const sand=mat('#b77748',0,1),stone=mat('#9e5832',0,1),cream=mat('#b9a28a'),panel=mat('#806d5a'),dark=mat('#3a3835'),metal=mat('#a8967d',.65,.5),rubber=mat('#302e2a',0,1),glass=mat('#718e8b',.4,.3),leaves=mat('#586f39',0,1),wood=mat('#514333',0,1);
 const blue=new T.MeshStandardMaterial({color:'#9bdaff',emissive:'#49b9ff',emissiveIntensity:2,roughness:.4});
 const boxG=new T.BoxGeometry(1,1,1),cylG=new T.CylinderGeometry(1,1,1,12),sphereG=new T.SphereGeometry(1,16,10),rockG=new T.IcosahedronGeometry(1,1);
 function group(name,x=0,y=0,z=0){const g=new T.Group();g.name=name;g.position.set(x,y,z);g.userData.source='Outpost7 V1 · dựng riêng theo ảnh';root.add(g);return g;}
 function mesh(g,geo,m,x,y,z,sx,sy,sz){const n=new T.Mesh(geo,m);n.position.set(x,y,z);n.scale.set(sx,sy,sz);g.add(n);return n;}
 const box=(g,m,x,y,z,w,h,d)=>mesh(g,boxG,m,x,y,z,w,h,d);
 const cyl=(g,m,x,y,z,r,h)=>mesh(g,cylG,m,x,y,z,r,h,r);
 const ball=(g,m,x,y,z,rx,ry,rz)=>mesh(g,sphereG,m,x,y,z,rx,ry,rz);
 function link(g,m,a,b,r=.045){const p=new T.Vector3(...a),q=new T.Vector3(...b),n=mesh(g,cylG,m,...p.clone().add(q).multiplyScalar(.5).toArray(),r,p.distanceTo(q),r);n.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),q.sub(p).normalize());return n;}
 function merge(g){g.updateMatrixWorld(true);const buckets=new Map();for(const n of g.children){if(!n.isMesh)continue;const geom=n.geometry.clone();geom.applyMatrix4(n.matrix);const list=buckets.get(n.material)||[];list.push(geom);buckets.set(n.material,list);}g.clear();for(const [m,list]of buckets){const geo=mergeGeometries(list,false);list.forEach(n=>n.dispose());const n=new T.Mesh(geo,m);g.add(n);}return g;}
 function module(name,x,z,w,d,h=3.5,rot=0){const g=group(name,x,0,z);g.rotation.y=rot;
  box(g,dark,0,.4,0,w+.3,.8,d+.3);box(g,cream,0,h/2+.5,0,w,h,d);box(g,panel,0,h+.6,0,w+.1,.3,d+.1);
  for(let a=-w/2+.6;a<w/2;a+=1.7){for(const side of [-1,1]){box(g,metal,a,h/2+.5,side*(d/2+.04),.16,h+.2,.17);box(g,dark,a+.5,h*.58,side*(d/2+.1),.7,1.05,.07);box(g,glass,a+.5,h*.58,side*(d/2+.15),.53,.8,.04);box(g,blue,a+.45,h+.15,side*(d/2+.1),.65,.06,.05);}}
  for(let i=-1;i<=1;i++)box(g,metal,w/2+.06,h/2+.3,i*d*.26,.13,h*.7,.2);
  for(let i=0;i<4;i++)box(g,metal,-w*.35+i*w*.23,h+.85,0,.7,.24,d*.65);
  return merge(g);
 }
 const terrain=group('01 · Địa hình cát đỏ');const ground=new T.PlaneGeometry(130,115,120,100);ground.rotateX(-Math.PI/2);const p=ground.attributes.position;
 for(let i=0;i<p.count;i++){let x=p.getX(i),z=p.getZ(i);p.setY(i,.14*Math.sin(x*.55)*Math.cos(z*.37)+.08*Math.sin(x*1.7+z*.9));}ground.computeVertexNormals();terrain.add(new T.Mesh(ground,sand));
 // Layered canyon escarpments rather than cones.
 for(let i=0;i<10;i++){const h=12+rand()*14,w=4+rand()*4,d=5+rand()*6;const g=group('02 · Vách đá trái '+(i+1),-37+rand()*3,0,-37+i*5);const geo=new T.BoxGeometry(w,h,d,2,8,2);const a=geo.attributes.position;for(let j=0;j<a.count;j++){const y=a.getY(j);a.setX(j,a.getX(j)+(Math.sin(y*2.1+i)*.25+Math.sin(y*.4)*.5));a.setZ(j,a.getZ(j)+Math.sin(y*1.9+i)*.3);}geo.computeVertexNormals();const n=new T.Mesh(geo,mat(new T.Color('#ae6338').multiplyScalar(.85+rand()*.3),0,1));n.position.y=h/2;g.add(n);}
 for(let i=0;i<9;i++){const x=-24+i*8,z=-42-rand()*10,h=5+rand()*9;const g=group('03 · Núi xa '+(i+1),x,0,z);mesh(g,rockG,stone,0,h*.25,0,7+rand()*4,h,5+rand()*5);}
 // Tall central laboratory and structural fins.
 const tower=group('04 · Tháp nghiên cứu trung tâm',-3,0,-15);
 cyl(tower,dark,0,1.2,0,6,2.4);cyl(tower,cream,0,3.5,0,4.7,4.5);cyl(tower,panel,0,6.2,0,3.6,1);
 cyl(tower,cream,0,11,0,2.4,9);cyl(tower,dark,0,15.6,0,2.5,.4);cyl(tower,panel,0,18,0,1.6,4.5);cyl(tower,metal,0,21.7,0,.7,3);
 for(let i=0;i<8;i++){const a=i*Math.PI/4,x=Math.cos(a),z=Math.sin(a);box(tower,metal,x*2.4,10.8,z*2.4,.38,9,.38);link(tower,dark,[x*5,1,z*5],[x*2,7,z*2],.22);if(i%2===0)box(tower,blue,x*2.51,11,z*2.51,.12,3,.12);}
 for(let i=0;i<5;i++)cyl(tower,metal,0,7.5+i*1.9,0,2.47,.12);
 link(tower,dark,[.8,17,.5],[.8,27,.5],.045);link(tower,metal,[-.6,20,-.6],[-.6,25,-.6],.06);merge(tower);
 module('05 · Phòng nghiên cứu trái',-18,-6,15,7,4.3);module('06 · Hành lang trung tâm',-5,-6,10,4,2.7);module('07 · Khối nhà kính chính',6,-3,17,9,3.3);module('08 · Nhà trạm phải',23,-10,12,6,3.6);module('09 · Phòng kỹ thuật phía sau',13,-18,9,6,3.1);
 function dome(name,x,z,r){const g=group(name,x,0,z);const base=3.8;cyl(g,panel,0,base-.3,0,r+.3,.5);cyl(g,metal,0,base,0,r+.45,.16);
  const windowMat=new T.MeshStandardMaterial({color:'#83a5a0',metalness:.1,roughness:.35,transparent:true,opacity:.2,depthWrite:false,side:T.DoubleSide});
  const shell=new T.Mesh(new T.SphereGeometry(r,32,16,0,Math.PI*2,0,Math.PI/2),windowMat);shell.position.y=base;g.add(shell);
  for(let j=0;j<16;j++){const a=j*Math.PI/8;for(let i=0;i<10;i++){const t1=i*Math.PI/20,t2=(i+1)*Math.PI/20;link(g,metal,[r*Math.sin(t1)*Math.cos(a),base+r*Math.cos(t1),r*Math.sin(t1)*Math.sin(a)],[r*Math.sin(t2)*Math.cos(a),base+r*Math.cos(t2),r*Math.sin(t2)*Math.sin(a)],.045);}}
  for(let j=1;j<=6;j++){const t=j*Math.PI/12,rr=r*Math.sin(t),y=base+r*Math.cos(t);for(let i=0;i<32;i++){const a=i*Math.PI/16,b=(i+1)*Math.PI/16;link(g,metal,[rr*Math.cos(a),y,rr*Math.sin(a)],[rr*Math.cos(b),y,rr*Math.sin(b)],.04);}}
  for(let i=0;i<9;i++){const a=i*2.4,rr=rand()*(r-1);const xx=Math.cos(a)*rr,zz=Math.sin(a)*rr;box(g,panel,xx,base+.15,zz,1.2,.3,1.2);cyl(g,wood,xx,base+.8,zz,.08,1.2);ball(g,leaves,xx,base+1.8,zz,.6,1,.6);}
  merge(g);return g;
 }
 dome('10 · Nhà kính lớn + khung vòm + cây',6,-5,7.4);dome('11 · Nhà kính phụ',20,-17,4.1);
 // Large tilted, concave dish with support ribs.
 const dish=group('12 · Chảo vệ tinh lớn',-23,0,-14);cyl(dish,dark,0,.8,0,3.5,1.6);cyl(dish,cream,0,2,0,2.7,1);box(dish,panel,0,4,0,1.8,4,1.8);
 const bowl=new T.Group();bowl.position.set(0,6,0);bowl.rotation.z=-.55;dish.add(bowl);const rr=5.2,depth=1.7;const verts=[],faces=[];for(let j=0;j<=12;j++)for(let i=0;i<=48;i++){const r=rr*j/12,a=i*Math.PI/24;verts.push(r*Math.cos(a),depth*(r/rr)**2,r*Math.sin(a));}for(let j=0;j<12;j++)for(let i=0;i<48;i++){const a=j*49+i;faces.push(a,a+49,a+1,a+1,a+49,a+50);}const bg=new T.BufferGeometry();bg.setAttribute('position',new T.Float32BufferAttribute(verts,3));bg.setIndex(faces);bg.computeVertexNormals();bowl.add(new T.Mesh(bg,new T.MeshStandardMaterial({color:'#9f8b72',metalness:.6,roughness:.6,side:T.DoubleSide})));
 for(let j=0;j<16;j++){const a=j*Math.PI/8;for(let i=0;i<12;i++){const r1=rr*i/12,r2=rr*(i+1)/12;link(bowl,dark,[r1*Math.cos(a),depth*(r1/rr)**2+.025,r1*Math.sin(a)],[r2*Math.cos(a),depth*(r2/rr)**2+.025,r2*Math.sin(a)],.035);}if(j%4===0)link(bowl,metal,[rr*.8*Math.cos(a),depth*.64,rr*.8*Math.sin(a)],[0,4,0],.055);}
 ball(bowl,dark,0,4,0,.18,.23,.18);merge(bowl); // bake dish separately, preserving its tilt.
 // Secondary antenna mast with open lattice.
 const mast=group('13 · Cột ăng ten phải',26,0,-23);for(const x of [-.45,.45])for(const z of [-.45,.45])link(mast,dark,[x,0,z],[x,13,z],.07);for(let y=1;y<13;y++){link(mast,metal,[-.45,y,-.45],[.45,y+1,-.45],.04);link(mast,metal,[.45,y,.45],[-.45,y+1,.45],.04);}cyl(mast,metal,0,13,0,.05,4);box(mast,blue,0,14.3,0,.08,.14,.08);merge(mast);
 // Airlock and stepped entrance.
 const airlock=group('14 · Cửa khí + cầu thang',7,0,2);box(airlock,panel,0,1.8,0,2.8,3.6,1);box(airlock,dark,0,1.8,.56,1.8,2.7,.12);box(airlock,glass,0,1.8,.65,1.5,2.4,.08);box(airlock,blue,0,3.4,.6,1,.09,.08);for(let i=0;i<5;i++)box(airlock,metal,0,.2+i*.2,2.4-i*.35,2.5,.4,.45);merge(airlock);
 const pad=group('15 · Bãi đáp vòng tròn',5,0,10);cyl(pad,dark,0,.13,0,6.4,.26);cyl(pad,panel,0,.3,0,5.9,.15);const ring=new T.Mesh(new T.TorusGeometry(5.4,.06,6,64),cream);ring.rotation.x=Math.PI/2;ring.position.y=.4;pad.add(ring);for(let i=0;i<8;i++){let a=i*Math.PI/4;box(pad,blue,Math.cos(a)*5.9,.42,Math.sin(a)*5.9,.35,.06,.14);}merge(pad);
 // Six-wheel rover with suspension, fenders, cockpit and equipment racks.
 const rover=group('16 · Xe thám hiểm sáu bánh',23,0,13);rover.rotation.y=-.25;
 box(rover,dark,0,1.1,0,6,1,2.7);box(rover,cream,0,2,0,6.6,1.3,3);box(rover,cream,-1.3,2.9,0,3.8,.8,2.5);box(rover,glass,-2.9,2.6,0,.08,.65,2.15);for(const s of [-1,1]){box(rover,glass,-1.8,2.8,s*1.27,1.5,.6,.06);box(rover,glass,-.1,2.8,s*1.27,1.25,.6,.06);for(let i=0;i<3;i++){const xx=-2.25+i*2.25;const tire=mesh(rover,cylG,rubber,xx,.9,s*1.62,.85,.55,.85);tire.rotation.x=Math.PI/2;const hub=mesh(rover,cylG,metal,xx,.9,s*1.95,.42,.1,.42);hub.rotation.x=Math.PI/2;for(let k=0;k<12;k++){let a=k*Math.PI/6;const tread=box(rover,dark,xx+Math.sin(a)*.84,.9+Math.cos(a)*.84,s*1.62,.3,.16,.63);tread.rotation.z=-a;}box(rover,panel,xx,1.75,s*1.5,1.6,.2,.45);link(rover,metal,[xx-.5,1.1,s],[xx,.9,s*1.8],.09);}}
 box(rover,metal,.8,2.8,0,1.5,.1,2.3);for(let i=0;i<3;i++)box(rover,dark,.3+i*.5,3.1,0,.35,.4,1.8);link(rover,dark,[2.7,2.6,-.7],[2.7,5,-.7],.04);box(rover,blue,-3.35,2,.85,.05,.16,.3);box(rover,blue,-3.35,2,-.85,.05,.16,.3);merge(rover);
 // Cargo crates, pressure tanks and pipes.
 for(let i=0;i<5;i++){const x=-13+i*2,z=8+rand()*5,g=group('17 · Kiện hàng '+(i+1),x,0,z);box(g,panel,0,.65,0,1.7,1.3,1.3);for(const s of [-1,1]){box(g,metal,s*.64,.65,0,.12,1.4,1.4);box(g,dark,0,.65,s*.67,1.2,.5,.05);}merge(g);}
 for(let i=0;i<4;i++){const g=group('18 · Bình áp suất '+(i+1),-20+i*1.3,0,0);cyl(g,panel,0,.9,0,.45,1.8);ball(g,cream,0,1.8,0,.45,.15,.45);cyl(g,dark,0,1.98,0,.08,.15);merge(g);}
 for(let i=0;i<55;i++){const x=(rand()-.5)*90,z=(rand()-.5)*80;if(Math.abs(x)<28&&z>-28&&z<17)continue;const r=.3+rand()*1.3,g=group('19 · Đá rải '+(i+1),x,0,z);mesh(g,rockG,stone,0,r*.4,0,r,r*.6,r*.8).rotation.y=rand()*6;}
 const foreground=group('20 · Tảng đá tiền cảnh trái',-22,0,21);for(let i=0;i<6;i++)mesh(foreground,rockG,stone,(rand()-.5)*9,rand()*2,(rand()-.5)*5,3+rand()*2,2+rand()*2,3+rand()*2);merge(foreground);
 // Background planets have real volume and deterministic surface colors.
 for(const [name,x,y,z,r]of [['21 · Hành tinh lớn',-8,36,-140,35],['22 · Mặt trăng nhỏ',28,48,-140,5]]){const g=group(name,x,y,z);const geo=new T.SphereGeometry(r,48,32),pos=geo.attributes.position,colors=[];const c=new T.Color();for(let i=0;i<pos.count;i++){const v=Math.sin(pos.getX(i)*.8+Math.sin(pos.getY(i)*.6)*4)+Math.cos(pos.getZ(i)*.6+pos.getY(i));c.set('#b78766').multiplyScalar(.82+.12*v);colors.push(c.r,c.g,c.b);}geo.setAttribute('color',new T.Float32BufferAttribute(colors,3));g.add(new T.Mesh(geo,new T.MeshStandardMaterial({vertexColors:true,roughness:1,metalness:0,emissive:'#513422',emissiveIntensity:.25})));}
 return root;
}
