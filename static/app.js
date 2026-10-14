'use strict';
const $ = id => document.getElementById(id);
const names = {omnivoice:'OmniVoice',piper:'Piper',coqui:'Coqui XTTS',chatterbox:'Chatterbox'};
const icons = {omnivoice:'▥',piper:'◌',coqui:'▦',chatterbox:'▥'};
let engine='omnivoice', config, sampleFile, sampleURL, busy=false, pollTimer;
const languageChoices={};
$('language').onchange=()=>{languageChoices[engine]=$('language').value;};

async function api(path, options={}) {
  const response=await fetch(path, options);
  if(!response.ok){let message=`HTTP ${response.status}`;try{const data=await response.json();message=typeof data.detail==='string'?data.detail:message;}catch{}throw Error(message);}
  return response.json();
}
function message(text,error=false){$('status').textContent=text;$('status').classList.toggle('error',error);}
function setBusy(value){busy=value;$('busy').hidden=!value;$('generate').disabled=value;document.querySelectorAll('.engine').forEach(b=>b.disabled=value);$('unload').disabled=value;}
async function refreshStatus(){
  config=await api('api/status');$('connection').textContent=config.loaded_engine?`${names[config.loaded_engine]} · Model đang giữ`:'Server đã kết nối';$('connection').classList.remove('offline');
  renderEngines();renderSettings();
  if(config.active&&!busy){setBusy(true);poll(config.active);}
}
function renderEngines(){
  $('engines').replaceChildren();
  for(const [key, spec] of Object.entries(config.engines)){
    const button=document.createElement('button');button.type='button';button.className='engine'+(engine===key?' selected':'');button.disabled=busy;button.setAttribute('aria-pressed',String(engine===key));
    const icon=document.createElement('span');icon.className='engine-icon';icon.textContent=icons[key];
    const text=document.createElement('span');const name=document.createElement('strong');name.textContent=spec.name;const note=document.createElement('small');note.textContent=spec.note;
    text.append(name,note);button.append(icon,text);button.onclick=()=>{engine=key;renderEngines();renderSettings();};$('engines').append(button);
  }
}
function renderSettings(){
  const spec=config.engines[engine];const clone=spec.clone;
  $('mode').textContent=clone?'Clone giọng':'Giọng có sẵn';$('engineNote').textContent=engine==='omnivoice'?'Nhập lời mẫu để tiết kiệm GPU':spec.note;
  $('sampleFields').hidden=!clone;$('piperInfo').hidden=clone;$('sampleHeading').textContent=clone?'1. Mẫu giọng':'1. Giọng đọc';
  $('transcriptField').hidden=engine!=='omnivoice';$('stepField').hidden=engine!=='omnivoice';$('emotionField').hidden=engine!=='chatterbox';$('licenseField').hidden=engine!=='coqui';
  $('sampleHint').textContent=`WAV / FLAC · ${engine==='omnivoice'?'3–10':'3–30'} giây · tối đa 20 MB`;
  $('speed').disabled=engine==='chatterbox';$('speedHint').hidden=engine!=='chatterbox';if(engine==='chatterbox'){$('speed').value=1;updateSliders();}
  const previous=languageChoices[engine];$('language').replaceChildren();
  const languages=engine==='piper'?[config.piper_language]:spec.languages;
  for(const code of languages){const option=document.createElement('option');option.value=code;option.textContent=config.languages[code]||code;$('language').append(option);}
  $('language').value=languages.includes(previous)?previous:(languages.includes('vi')?'vi':languages[0]);
  $('piperModelInfo').textContent=`Ngôn ngữ model: ${config.languages[config.piper_language]||config.piper_language}`;
  const oldSpeaker=$('speaker').value;$('speaker').replaceChildren();
  for(const [id,name] of Object.entries(config.piper_speakers||{'0':'Giọng mặc định'})){const option=document.createElement('option');option.value=id;option.textContent=`Giọng ${id} · ${name}`;$('speaker').append(option);}
  if([...$('speaker').options].some(option=>option.value===oldSpeaker))$('speaker').value=oldSpeaker;
  const notice=$('setupNotice');notice.replaceChildren();notice.hidden=spec.configured;
  if(!spec.installed){const text=document.createElement('span');text.textContent=`Chưa cài ${spec.name}. Trên máy chạy server, chạy: `;const code=document.createElement('code');code.textContent=`python install_engine.py ${engine}`;notice.append(text,code);}
  else if(!spec.configured){notice.textContent='Piper đã cài nhưng thiếu model giọng. Cấu hình PIPER_MODEL rồi khởi động lại server; xem README.';}
}
function updateSliders(){for(const [id,suffix] of [['speed','×'],['pitch',' semitone'],['gain',' dB'],['emotion','']]){$(id+'Value').textContent=Number($(id).value).toFixed(id==='speed'?2:1)+suffix;}}
['speed','pitch','gain','emotion'].forEach(id=>$(id).addEventListener('input',updateSliders));
$('text').oninput=()=>{$('counter').textContent=`${$('text').value.length} / 2000`;};$('text').oninput();
function chooseSample(file){
  if(!file)return;if(!/\.(wav|flac)$/i.test(file.name))return message('Chọn file WAV hoặc FLAC.',true);
  if(file.size>20*1024*1024)return message('Mẫu tối đa 20 MB.',true);
  sampleFile=file;if(sampleURL)URL.revokeObjectURL(sampleURL);sampleURL=URL.createObjectURL(file);$('samplePlayer').src=sampleURL;$('filename').textContent=file.name;$('samplePreview').hidden=false;$('sampleDuration').textContent='';
}
$('sample').onchange=()=>chooseSample($('sample').files[0]);
$('samplePlayer').onloadedmetadata=()=>{$('sampleDuration').textContent=`Mẫu dài ${$('samplePlayer').duration.toFixed(1)} giây`;};
$('removeSample').onclick=()=>{sampleFile=null;$('sample').value='';$('samplePreview').hidden=true;$('samplePlayer').removeAttribute('src');if(sampleURL)URL.revokeObjectURL(sampleURL);sampleURL=null;};
['dragenter','dragover'].forEach(event=>$('drop').addEventListener(event,e=>{e.preventDefault();$('drop').classList.add('drag');}));
['dragleave','drop'].forEach(event=>$('drop').addEventListener(event,e=>{e.preventDefault();$('drop').classList.remove('drag');if(event==='drop')chooseSample(e.dataTransfer.files[0]);}));
$('generateForm').onsubmit=async e=>{
  e.preventDefault();if(busy)return;
  try{
    if(!config)throw Error('Server chưa kết nối.');
    if(config.engines[engine].clone){if(!sampleFile)throw Error('Chọn mẫu giọng trước.');if(!$('consent').checked)throw Error('Xác nhận quyền sử dụng giọng trước.');}
    const form=new FormData($('generateForm'));form.set('engine',engine);form.set('speed',$('speed').value);form.set('consent',String($('consent').checked));form.set('license_consent',String($('license_consent').checked));
    form.delete('sample');if(sampleFile)form.set('sample',sampleFile,sampleFile.name);
    setBusy(true);message('Đang gửi yêu cầu…');$('result').hidden=true;$('resultMeta').textContent='';
    const job=await api('api/generate',{method:'POST',body:form});poll(job.id);
  }catch(error){setBusy(false);message(error.message,true);}
};
async function poll(id){
  clearTimeout(pollTimer);
  try{
    const job=await api(`api/jobs/${id}`);message(job.message,job.status==='error');
    if(job.status==='done'){
      $('resultPlayer').src=job.url.slice(1);$('download').href=job.url.slice(1);$('download').download=`${job.engine}-${id.slice(0,8)}.wav`;$('result').hidden=false;
      $('resultMeta').textContent=`${names[job.engine]} · ${job.duration}s âm thanh · ${job.elapsed}s xử lý`;setBusy(false);await refreshStatus();
    }else if(job.status==='error'){setBusy(false);await refreshStatus();}
    else pollTimer=setTimeout(()=>poll(id),1500);
  }catch(error){setBusy(false);message(`Mất kết nối: ${error.message}. Tải lại trang để kiểm tra tác vụ.`,true);}
}
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'&&!busy){e.preventDefault();$('generateForm').requestSubmit();}});
$('unload').onclick=async()=>{try{await api('api/unload',{method:'POST'});await refreshStatus();message('Đã giải phóng model. Lần tạo tiếp theo sẽ tải lại vào bộ nhớ.');}catch(e){message(e.message,true);}};
function view(name){document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===name));['studio','voices','history'].forEach(id=>$(id).hidden=id!==name);$('heading').textContent={studio:'Tạo âm thanh',voices:'Giọng đã lưu',history:'Lịch sử'}[name];if(name==='history')renderHistory();if(name==='voices')renderVoices();}
document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>view(b.dataset.view));
$('help').onclick=()=>$('helpDialog').showModal();$('closeHelp').onclick=()=>$('helpDialog').close();
async function renderHistory(){
  const list=$('historyList');list.replaceChildren();
  try{const jobs=await api('api/jobs');if(!jobs.length){list.textContent='Chưa có kết quả trong phiên này.';return;}
    for(const job of jobs){const row=document.createElement('div');row.className='list-item';const info=document.createElement('div');const title=document.createElement('strong');title.textContent=names[job.engine];const detail=document.createElement('p');detail.textContent=job.text;const state=document.createElement('p');state.textContent=job.message;info.append(title,detail,state);row.append(info);if(job.status==='done'){const link=document.createElement('a');link.className='secondary';link.textContent='Tải WAV';link.href=job.url.slice(1);link.download='voice.wav';row.append(link);}list.append(row);}
  }catch(error){list.textContent=error.message;}
}
$('refreshHistory').onclick=renderHistory;
function database(){return new Promise((resolve,reject)=>{const r=indexedDB.open('voice-studio',1);r.onupgradeneeded=()=>r.result.createObjectStore('voices',{keyPath:'id'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(Error('Không mở được kho lưu trình duyệt.'));});}
async function dbAction(mode,action){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction('voices',mode);const r=action(tx.objectStore('voices'));let result;r.onsuccess=()=>result=r.result;tx.oncomplete=()=>{db.close();resolve(result);};tx.onerror=()=>{db.close();reject(Error('Không lưu được mẫu. Kiểm tra dung lượng trình duyệt.'));};});}
$('saveVoice').onclick=async()=>{try{if(!sampleFile)throw Error('Chọn mẫu trước khi lưu.');if(!$('consent').checked)throw Error('Xác nhận quyền sử dụng giọng trước.');const name=prompt('Tên mẫu giọng:',sampleFile.name);if(!name)return;await dbAction('readwrite',s=>s.put({id:crypto.randomUUID(),name:name.slice(0,80),file:sampleFile,transcript:$('transcript').value}));message('Đã lưu mẫu trong trình duyệt. Mở “Giọng đã lưu” để dùng lại.');}catch(e){message(e.message,true);}};
async function renderVoices(){const list=$('voiceList');list.replaceChildren();try{const voices=await dbAction('readonly',s=>s.getAll());if(!voices.length){list.textContent='Chưa lưu mẫu. Chọn mẫu trong màn hình Tạo âm thanh rồi bấm Lưu.';return;}for(const voice of voices){const row=document.createElement('div');row.className='list-item';const info=document.createElement('div');const name=document.createElement('strong');name.textContent=voice.name;const text=document.createElement('p');text.textContent=voice.transcript||'Chưa có lời mẫu';info.append(name,text);const actions=document.createElement('div');actions.className='list-actions';const use=document.createElement('button');use.className='secondary';use.textContent='Dùng mẫu';use.onclick=()=>{chooseSample(voice.file);$('transcript').value=voice.transcript;$('consent').checked=false;view('studio');};const remove=document.createElement('button');remove.className='quiet';remove.textContent='Xóa';remove.onclick=async()=>{await dbAction('readwrite',s=>s.delete(voice.id));renderVoices();};actions.append(use,remove);row.append(info,actions);list.append(row);}}catch(e){list.textContent=e.message;}}
refreshStatus().catch(error=>{$('connection').textContent='Server chưa kết nối';$('connection').classList.add('offline');message('Hãy chạy python server.py rồi mở giao diện qua server. '+error.message,true);});
