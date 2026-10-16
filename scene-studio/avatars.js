import * as THREE from 'three';
export const avatarTypes=['person','chibi','chick','hippo','cow','gorilla'];
export function avatar(type,color){
 const root=new THREE.Group();root.userData.rig=true;
 const mat=c=>new THREE.MeshStandardMaterial({color:c,roughness:.85,flatShading:true});const body=mat(color),white=mat('#ebe8d5'),black=mat('#172029'),gold=mat('#dfa93f');
 const ball=(parent,x,y,z,sx,sy,sz,m)=>{const mesh=new THREE.Mesh(new THREE.SphereGeometry(1,12,8),m);mesh.position.set(x,y,z);mesh.scale.set(sx,sy,sz);parent.add(mesh);return mesh;};
 const joint=(name,x,y,z,parent=root)=>{const group=new THREE.Group();group.name=name;group.position.set(x,y,z);parent.add(group);return group;};
 const torso=joint('pose-body',0,.48,0);
 ball(torso,0,.1,0,type==='gorilla'?.29:.23,.27,.17,body);
 const head=joint('pose-head',0,.39,0,torso);ball(head,0,0,0,.24,.22,.2,body);
 const bird=type==='chick',animal=['hippo','cow','gorilla'].includes(type);
 if(animal){ball(head,0,-.06,.19,.2,.12,.14,type==='gorilla'?black:body);for(const x of [-.2,.2])ball(head,x,.12,0,.07,.08,.06,body);for(const x of [-.07,.07])ball(head,x,-.06,.315,.022,.027,.012,black);}
 if(bird){const beak=new THREE.Mesh(new THREE.ConeGeometry(.09,.18,4),gold);beak.rotation.x=Math.PI/2;beak.position.set(0,-.05,.25);head.add(beak);}
 if(type==='cow'){for(const x of [-.15,.15]){const horn=new THREE.Mesh(new THREE.ConeGeometry(.045,.17,6),gold);horn.position.set(x,.23,0);head.add(horn);}ball(torso,.12,.17,.155,.06,.09,.025,black);}
 if(type==='hippo'){const hat=new THREE.Mesh(new THREE.ConeGeometry(.26,.25,12),gold);hat.position.y=.28;head.add(hat);for(let i=0;i<3;i++){const band=new THREE.Mesh(new THREE.TorusGeometry(.23-i*.035,.02,4,16),mat('#315873'));band.rotation.x=Math.PI/2;band.position.y=.18+i*.06;head.add(band);}}
 if(type==='chibi'||type==='person'){const hat=new THREE.Mesh(new THREE.CylinderGeometry(.24,.24,.09,12),mat('#654469'));hat.position.y=.2;head.add(hat);}
 for(const x of [-.095,.095]){ball(head,x,.035,.18,.075,.08,.05,white);ball(head,x,.03,.228,.029,.035,.015,black);}
 for(const side of [-1,1]){
  const arm=joint('pose-arm-'+side,side*.28,.2,0,torso);ball(arm,0,-.12,0,type==='gorilla'?.11:.07,.14,.075,body);
  const forearm=joint('pose-elbow-'+side,0,-.25,0,arm);ball(forearm,0,-.1,0,.065,.12,.065,body);ball(forearm,0,-.23,0,.075,.07,.07,bird?gold:body);
  const thigh=joint('pose-thigh-'+side,side*.12,.48,0);ball(thigh,0,-.115,0,.08,.14,.085,body);
  const shin=joint('pose-knee-'+side,0,-.22,0,thigh);ball(shin,0,-.1,0,.065,.115,.07,body);ball(shin,0,-.2,.06,.08,.045,.12,bird?gold:black);
 }
 root.userData.pose={body:0,thigh:0,knee:0,arm:0,elbow:0};return root;
}
export function applyPose(root,values){root.userData.pose={...values};const angle=v=>THREE.MathUtils.degToRad(Number.isFinite(v)?v:0);root.traverse(n=>{if(n.name==='pose-body')n.rotation.x=angle(values.body);if(n.name==='pose-head'){n.rotation.y=angle(values.headYaw);n.rotation.x=angle(values.headPitch);}for(const side of [-1,1]){const prefix=side===-1?'left':'right';if(n.name==='pose-thigh-'+side)n.rotation.x=angle(values[prefix+'Thigh']??values.thigh);if(n.name==='pose-knee-'+side)n.rotation.x=angle(values[prefix+'Knee']??values.knee);if(n.name==='pose-arm-'+side)n.rotation.x=angle(values[prefix+'Arm']??values.arm);if(n.name==='pose-elbow-'+side)n.rotation.x=angle(values[prefix+'Elbow']??values.elbow);}});}
export const posePresets={
 stand:{body:0,thigh:0,knee:0,arm:0,elbow:0},
 sit:{body:0,thigh:-90,knee:90,arm:0,elbow:0},
 crouch:{body:30,thigh:-80,knee:120,arm:-45,elbow:-30},
 wave:{body:0,thigh:0,knee:0,arm:0,elbow:0,rightArm:-155,rightElbow:-20,headYaw:12},
 point:{body:0,thigh:0,knee:0,arm:0,elbow:0,rightArm:-90,rightElbow:0,headYaw:20},
 handsup:{body:0,thigh:0,knee:0,arm:-160,elbow:-10},
 walk:{body:6,thigh:0,knee:0,arm:0,elbow:-12,leftThigh:-30,rightThigh:25,leftKnee:5,rightKnee:35,leftArm:25,rightArm:-30},
 kneel:{body:0,thigh:0,knee:0,arm:-25,elbow:-30,leftThigh:-85,leftKnee:80,rightThigh:15,rightKnee:120}
};
