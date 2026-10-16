import * as T from 'three';
import {mergeGeometries,mergeVertices} from '../../vendor/BufferGeometryUtils.js';
export function createRabbit(){
 const root=new T.Group();root.name='Thỏ cảnh sát · theo ảnh · V1';root.userData={rig:true,pose:{body:0,thigh:0,knee:0,arm:0,elbow:0},source:'Rabbit Officer V1 · model dựng riêng theo ảnh',englishName:'Grey rabbit police officer with long ears, violet eyes and blue uniform'};
 const mat=(color,roughness=.8,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness});
 const fur=mat('#a5a09a'),cheek=mat('#b8b0a4'),muzzle=mat('#ded6c7'),inner=mat('#bc8e89'),blue=mat('#6188b3'),pants=mat('#344f78'),armor=mat('#263d5a'),edge=mat('#172b44'),glove=mat('#20334b'),silver=mat('#a2adb7',.45,.45),gold=mat('#c9b165',.4,.55),black=mat('#191d29'),white=mat('#efebdf',.4),iris=mat('#79518d',.35),nose=mat('#b87d78'),brown=mat('#695952'),mouth=mat('#603a34');
 const sphere=new T.SphereGeometry(1,28,20),cylinder=new T.CylinderGeometry(1,1,1,20),boxgeo=new T.BoxGeometry(1,1,1);
 const ball=(g,m,x,y,z,sx,sy,sz)=>{const n=new T.Mesh(sphere,m);n.position.set(x,y,z);n.scale.set(sx,sy,sz);g.add(n);return n;};
 const box=(g,m,x,y,z,w,h,d)=>{const n=new T.Mesh(boxgeo,m);n.position.set(x,y,z);n.scale.set(w,h,d);g.add(n);return n;};
 const cyl=(g,m,x,y,z,r,h,rz=r)=>{const n=new T.Mesh(cylinder,m);n.position.set(x,y,z);n.scale.set(r,h,rz);g.add(n);return n;};
 function joint(name,x,y,z,parent=root){const n=new T.Group();n.name=name;n.position.set(x,y,z);parent.add(n);return n;}
 function tube(g,m,points,r=.008){const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));const n=new T.Mesh(new T.TubeGeometry(curve,24,r,6,false),m);g.add(n);return n;}
 function polygon(g,m,coords,z,depth=.025,bevel=.015){const shape=new T.Shape();coords.forEach((p,i)=>i?shape.lineTo(...p):shape.moveTo(...p));shape.closePath();const geo=new T.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:bevel,bevelThickness:bevel});const n=new T.Mesh(geo,m);n.position.z=z;g.add(n);return n;}
 const body=joint('pose-body',0,1,0);
 ball(body,blue,0,.25,0,.225,.34,.145);ball(body,pants,0,-.025,-.005,.235,.18,.155);
 // Collar and neck.
 cyl(body,fur,0,.62,0,.09,.14,.085);
 for(const s of [-1,1]){const collar=polygon(body,blue,[[s*.02,.59],[s*.15,.67],[s*.18,.56],[s*.07,.49]],.115,.025,.008);}
 // Shaped ballistic vest with front panel, side straps and seam piping.
 const vestOutline=[[-.23,.53],[-.17,.62],[-.07,.56],[.07,.56],[.17,.62],[.23,.53],[.2,.3],[.13,.27],[-.13,.27],[-.2,.3]];
 polygon(body,armor,vestOutline,.105,.045,.018);polygon(body,armor,vestOutline,-.165,.035,.018);
 tube(body,silver,[[-.205,.3,.16],[-.12,.28,.17],[0,.3,.18],[.12,.28,.17],[.205,.3,.16]],.004);
 for(const s of [-1,1]){box(body,edge,s*.225,.3,0,.035,.2,.15);box(body,armor,s*.19,.57,0,.055,.07,.26);}
 // Gold shield badge and inset.
 polygon(body,gold,[[.065,.47],[.14,.5],[.18,.45],[.165,.38],[.12,.35],[.065,.38]],.17,.012,.005);
 polygon(body,edge,[[.085,.45],[.14,.475],[.157,.445],[.143,.395],[.12,.38],[.086,.4]],.188,.004,.002);
 ball(body,gold,.12,.425,.2,.017,.023,.007);
 // Duty belt, buckle, pouches and holster.
 cyl(body,edge,0,-.025,0,.25,.09,.166);box(body,silver,0,-.025,.176,.09,.065,.02);box(body,edge,0,-.025,.189,.05,.035,.007);
 for(const s of [-1,1]){const pouch=joint('Utility pouch '+s,s*.2,-.06,.07,body);pouch.rotation.z=-s*.15;box(pouch,brown,0,0,0,.105,.15,.095);box(pouch,edge,0,.045,.053,.11,.045,.017);ball(pouch,silver,0,.04,.066,.009,.009,.004);box(body,edge,s*.1,-.02,-.155,.08,.1,.045);}
 const tail=joint('Đuôi',0,.98,-.17);ball(tail,muzzle,0,0,-.025,.12,.12,.12);ball(tail,fur,.045,.03,-.08,.065,.07,.06);
 // Head silhouette with broad cheek tufts and tapered lower jaw.
 const head=joint('pose-head',0,.77,0,body);
 ball(head,fur,0,.065,0,.275,.295,.235);ball(head,cheek,0,-.105,.055,.235,.155,.205);
 for(const s of [-1,1]){const cheekBall=ball(head,cheek,s*.205,-.075,.075,.12,.11,.15);cheekBall.rotation.z=s*.2;
  for(let i=0;i<3;i++){const tuft=new T.Mesh(new T.ConeGeometry(.038,.1,5),cheek);tuft.position.set(s*(.26+i*.012),-.04-i*.025,.08);tuft.rotation.z=-s*(1.3+i*.12);head.add(tuft);}}
 // Long ears, front pink lining and contrasting soft rims.
 for(const s of [-1,1]){const ear=joint('Tai '+s,s*.14,.265,-.04,head);ear.rotation.z=-s*.1;ear.rotation.x=s*.045;
  ball(ear,fur,0,.36,0,.1,.415,.064);ball(ear,cheek,0,.365,.035,.087,.39,.035);ball(ear,inner,0,.375,.063,.062,.335,.014);
  const tip=ball(ear,brown,0,.686,-.008,.074,.065,.045);tip.scale.y*=.7;
 }
 // Eye sockets, white sclera, violet irises, pupil, and white highlights.
 for(const s of [-1,1]){ball(head,fur,s*.126,.065,.191,.128,.15,.071);ball(head,white,s*.127,.07,.218,.113,.126,.064);
  const x=s*.112;ball(head,iris,x,.067,.276,.062,.079,.021);ball(head,black,x,.063,.293,.034,.053,.012);ball(head,white,x-.018,.095,.306,.017,.021,.006);ball(head,white,x+.017,.04,.306,.007,.009,.004);
  tube(head,fur,[[s*.03,.12,.25],[s*.06,.195,.229],[s*.14,.211,.203],[s*.22,.16,.198]],.014);
  tube(head,brown,[[s*.04,.235,.165],[s*.09,.267,.173],[s*.16,.268,.145],[s*.215,.245,.115]],.016);
 }
 // Muzzle, nose, smile and incisors.
 for(const s of [-1,1])ball(head,muzzle,s*.075,-.09,.236,.112,.075,.085);
 polygon(head,nose,[[-.047,-.046],[.047,-.046],[.024,-.073],[0,-.09],[-.024,-.073]],.313,.014,.008);
 tube(head,mouth,[[-.14,-.12,.259],[-.09,-.163,.274],[0,-.185,.283],[.09,-.163,.274],[.14,-.12,.259]],.012);
 polygon(head,white,[[-.055,-.162],[.055,-.162],[.044,-.202],[-.04,-.202]],.288,.014,.004);tube(head,brown,[[0,-.17,.31],[0,-.199,.31]],.0025);
 // Arms in a hands-on-hips rest pose; X axes remain available to V2 controls.
 for(const s of [-1,1]){const arm=joint('pose-arm-'+s,s*.235,.52,0,body);arm.rotation.z=s*.63;
  ball(arm,blue,0,-.115,0,.084,.18,.086);ball(arm,blue,0,-.27,0,.074,.075,.075);
  const forearm=joint('pose-elbow-'+s,0,-.28,0,arm);forearm.rotation.z=-s*1.35;
  ball(forearm,blue,0,-.105,0,.066,.135,.071);cyl(forearm,glove,0,-.195,0,.071,.12,.077);cyl(forearm,silver,0,-.17,0,.073,.025,.078);cyl(forearm,edge,0,-.23,0,.073,.025,.078);
  ball(forearm,glove,0,-.285,.015,.065,.078,.052);for(let j=0;j<3;j++)ball(forearm,glove,(j-1)*.028,-.33,.035,.021,.035,.023);ball(forearm,glove,-s*.06,-.275,.045,.025,.045,.025);
  // Legs, knee pads, boots and visible furry toes.
  const thigh=joint('pose-thigh-'+s,s*.135,1,0);thigh.rotation.z=s*.105;
  ball(thigh,pants,0,-.17,0,.124,.25,.13);const shin=joint('pose-knee-'+s,0,-.39,.005,thigh);
  ball(shin,pants,0,-.16,0,.086,.22,.094);ball(shin,silver,0,.005,.108,.087,.113,.027);for(const x of [-.045,.045])ball(shin,edge,x,.04,.132,.008,.009,.005);
  cyl(shin,edge,0,-.28,0,.09,.2,.098);cyl(shin,armor,0,-.18,0,.096,.045,.102);
  ball(shin,armor,0,-.385,.075,.105,.095,.19);ball(shin,fur,0,-.4,.22,.109,.073,.089);
  for(let j=0;j<3;j++)ball(shin,cheek,(j-1)*.058,-.405,.267,.035,.056,.052);
  for(let k=0;k<2;k++){const strap=box(shin,edge,0,-.345,.12+k*.065,.205,.045,.04);strap.rotation.x=-.1;}
 }
 // Merge only meshes directly below each articulation, preserving all joint groups.
 function optimize(g){for(const child of [...g.children])if(child.isGroup)optimize(child);g.updateMatrix();const buckets=new Map();for(const n of [...g.children])if(n.isMesh){n.updateMatrix();const geo=n.geometry.index?n.geometry.toNonIndexed():n.geometry.clone();geo.applyMatrix4(n.matrix);const list=buckets.get(n.material)||[];list.push(geo);buckets.set(n.material,list);g.remove(n);}for(const [m,list]of buckets){const merged=mergeGeometries(list,false);list.forEach(a=>a.dispose());const compact=mergeVertices(merged,1e-5);merged.dispose();g.add(new T.Mesh(compact,m));}}
 optimize(root);root.updateMatrixWorld(true);const bounds=new T.Box3().setFromObject(root);root.position.y=-bounds.min.y;
 return root;
}
