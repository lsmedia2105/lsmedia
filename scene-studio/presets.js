// Persistent, origin-local preset storage. No image/model is uploaded.
const DB='ls-pixel-studio-presets',STORE='presets';
let connection;
export function openLibrary(){if(!connection)connection=new Promise((resolve,reject)=>{const req=indexedDB.open(DB,1);req.onupgradeneeded=()=>req.result.createObjectStore(STORE,{keyPath:'id'});req.onsuccess=()=>resolve(req.result);req.onerror=()=>{connection=null;reject(req.error);};req.onblocked=()=>{connection=null;reject(Error('Thư viện đang bị khóa ở tab khác. Đóng tab studio khác rồi thử lại.'));};});return connection;}
async function transaction(mode,work){const db=await openLibrary();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,mode),request=work(tx.objectStore(STORE));let result;request.onsuccess=()=>{result=request.result;};tx.oncomplete=()=>resolve(result);tx.onabort=tx.onerror=()=>reject(tx.error||request.error||Error('Không lưu được thư viện'));});}
export const listPresets=async()=>{const rows=await transaction('readonly',store=>store.getAll());return rows.sort((a,b)=>b.updated-a.updated);};
export const getPreset=id=>transaction('readonly',store=>store.get(id));
export const removePreset=id=>transaction('readwrite',store=>store.delete(id));
export function validatePreset(record){if(record?.format!=='LS-STUDIO-PRESET'||record.version!==1||!['character','scene','object'].includes(record.kind)||typeof record.name!=='string'||!record.name.trim()||record.name.length>120||!record.object?.object||!['Group','Mesh','Scene'].includes(record.object.object.type))throw Error('File preset không hợp lệ. Dùng .lspreset, không dùng GLB hoặc .ls3d ở nút này.');return record;}
export async function putPreset(record){validatePreset(record);await transaction('readwrite',store=>store.put(record));return record;}
