import * as T from 'three';
import {applyPose,posePresets} from './avatars.js';
export function boxPerson(type='normal'){
 const root=new T.Group();root.name={normal:'Người hộp',tall:'Người hộp cao gầy',stocky:'Người hộp đậm',child:'Người hộp nhỏ',seated:'Người hộp ngồi'}[type];root.userData={rig:true,source:'Preset người hộp',pose:{}};
 const material=new T.MeshStandardMaterial({color:'#b7bebd',roughness:.9}),headMat=new T.MeshStandardMaterial({color:'#8e929e',roughness:.9}),joint=(name,parent,x,y,z)=>{const g=new T.Group();g.name=name;g.position.set(x,y,z);parent.add(g);return g;};
 function cube(parent,w,h,d,x,y,z,mat=material){const m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);}
 const body=joint('pose-body',root,0,.9,0);cube(body,.46,.63,.27,0,.3,0);const head=joint('pose-head',body,0,.88,0);cube(head,.32,.36,.32,0,0,0,headMat);cube(head,.17,.045,.025,0,.015,.17,new T.MeshStandardMaterial({color:'#3e5460'}));
 for(const side of [-1,1]){const arm=joint('pose-arm-'+side,body,side*.32,.56,0);cube(arm,.16,.34,.19,0,-.17,0);const elbow=joint('pose-elbow-'+side,arm,0,-.34,0);cube(elbow,.14,.31,.17,0,-.155,0);const leg=joint('pose-thigh-'+side,root,side*.135,.9,0);cube(leg,.2,.44,.23,0,-.22,0);const knee=joint('pose-knee-'+side,leg,0,-.44,0);cube(knee,.18,.4,.21,0,-.2,0);cube(knee,.2,.12,.34,0,-.4,.055,headMat);}
 if(type==='tall')root.scale.set(.8,1.16,.9);if(type==='stocky')root.scale.set(1.35,.96,1.2);if(type==='child')root.scale.set(.72,.7,.72);applyPose(root,{...posePresets[type==='seated'?'sit':'stand']});return root;
}
