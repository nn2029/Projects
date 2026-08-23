const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));
let selected = [];
let currentSessionId = null;
let currentData = null;
let currentSpec = null;
let latestPrompt = '';

function humanBytes(n){const u=['B','KB','MB','GB'];let i=0,v=n;while(v>=1024&&i<u.length-1){v/=1024;i++}return `${v.toFixed(i?1:0)} ${u[i]}`}
function esc(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}
function setMessage(text,error=false){$('#workspaceMessage').textContent=text||'';$('#workspaceMessage').className=`status wide ${error?'error':''}`}
function setStatus(text,error=false){$('#status').textContent=text||'';$('#status').className=`status ${error?'error':''}`}

async function api(path, options={}){
  const res = await fetch(path, options);
  let data={};try{data=await res.json()}catch{}
  if(!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

async function loadProvider(){
  try{const data=await api('/api/providers');const p=data.openai;$('#providerBadge').textContent=p.configured?`AI ready · ${p.model}`:'Manual mode · no AI key';$('#providerBadge').classList.toggle('ready',p.configured)}catch{$('#providerBadge').textContent='Provider status unavailable'}
}
async function loadSessions(){
  try{const data=await api('/api/sessions');renderSessionList(data.sessions||[])}catch(err){$('#sessionList').innerHTML=`<p class="status error">${esc(err.message)}</p>`}
}
function renderSessionList(sessions){
  if(!sessions.length){$('#sessionList').innerHTML='<div class="empty-mini">No labs yet.<br>Create your first one.</div>';return}
  $('#sessionList').innerHTML=sessions.map(s=>`<button class="session-item ${s.id===currentSessionId?'active':''}" data-session="${s.id}"><span class="session-status">${esc((s.status||'new').toUpperCase())}</span><strong>${esc(s.topic)}</strong><small>${esc(s.target_level||'')} · ${s.media_count} media</small></button>`).join('');
  $$('.session-item').forEach(btn=>btn.addEventListener('click',()=>openSession(btn.dataset.session)));
}
async function openSession(id){
  try{setMessage('Loading lab…');const data=await api(`/api/sessions/${id}`);currentSessionId=id;currentData=data;currentSpec=data.compiled_spec||data.generated_spec||data.starter_spec;showWorkspace(data);loadSessions();setMessage('')}catch(err){setMessage(err.message,true)}
}

const dropzone=$('#dropzone'), fileInput=$('#files');
function renderFiles(){$('#fileList').innerHTML=selected.map((f,i)=>`<div class="file-row"><div><span class="file-kind">${f.type.startsWith('video')?'VIDEO':'IMAGE'}</span> ${esc(f.name)}</div><div>${humanBytes(f.size)} <button class="secondary remove" data-i="${i}">Remove</button></div></div>`).join('');$$('.remove').forEach(b=>b.onclick=e=>{e.stopPropagation();selected.splice(Number(b.dataset.i),1);renderFiles()})}
function addFiles(files){for(const f of files){if(!(f.type.startsWith('image/')||f.type.startsWith('video/')))continue;if(!selected.some(x=>x.name===f.name&&x.size===f.size))selected.push(f)}renderFiles()}
dropzone.onclick=()=>fileInput.click();dropzone.onkeydown=e=>{if(e.key==='Enter'||e.key===' ')fileInput.click()};fileInput.onchange=()=>addFiles(fileInput.files);['dragenter','dragover'].forEach(ev=>dropzone.addEventListener(ev,e=>{e.preventDefault();dropzone.classList.add('dragging')}));['dragleave','drop'].forEach(ev=>dropzone.addEventListener(ev,e=>{e.preventDefault();dropzone.classList.remove('dragging')}));dropzone.addEventListener('drop',e=>addFiles(e.dataTransfer.files));

$('#prepare').onclick=async()=>{
  const topic=$('#topic').value.trim();if(!topic&&!selected.length){setStatus('Add a topic or upload media.',true);return}
  const fd=new FormData();fd.append('topic',topic);fd.append('target_level',$('#level').value);fd.append('learning_outcome',$('#outcome').value.trim());selected.forEach(f=>fd.append('files',f));
  $('#prepare').disabled=true;setStatus('Preparing media evidence…');
  try{const data=await api('/api/sessions',{method:'POST',body:fd});currentSessionId=data.session.id;currentData=data;currentSpec=data.starter_spec;showWorkspace(data);await loadSessions();setStatus('Lab created.')}catch(err){setStatus(err.message,true)}finally{$('#prepare').disabled=false}
};

function showWorkspace(data){
  $('#welcome').classList.add('hidden');$('#composer').classList.add('hidden');$('#workspace').classList.remove('hidden');
  const s=data.session,bp=data.blueprint;$('#workspaceStatus').textContent=(s.status||'prepared').toUpperCase();$('#workspaceTitle').textContent=s.topic||currentSpec?.title||'Untitled lab';$('#workspaceOutcome').textContent=s.learning_outcome||currentSpec?.objective||'';
  $('#summaryChip').textContent=`${bp.input_summary.image_count} IMG · ${bp.input_summary.video_count} VIDEO · ${bp.input_summary.representative_video_frames} FRAMES`;
  renderMedia(s);$('#pipeline').innerHTML=bp.pipeline.map(x=>`<div class="pipe">${esc(x)}</div>`).join('');
  latestPrompt=data.agent_prompt||latestPrompt||'';$('#prompt').textContent=latestPrompt;
  currentSpec=data.compiled_spec||data.generated_spec||data.starter_spec||currentSpec;renderAuthor(currentSpec);
  const compiled=!!data.compiled_spec||s.status==='compiled';setCompiledState(compiled);
  activateTab('evidence');
}
function renderMedia(s){
  const root=`/api/sessions/${s.id}/files/`;
  $('#mediaGrid').innerHTML=(s.media||[]).map(m=>{
    if(m.kind==='image'){
      const ocr=m.ocr?.text?`<details><summary>OCR text</summary><pre class="mini-pre">${esc(m.ocr.text)}</pre></details>`:'';
      return `<div class="media-card"><img src="${root}uploads/${m.stored_name}" alt="${esc(m.original_name)}"><div class="meta"><h3>${esc(m.original_name)}</h3><p>${m.width} × ${m.height} · provenance ${m.id}</p>${ocr}</div></div>`;
    }
    const frames=(m.keyframes||[]).map(f=>`<div class="frame"><img src="${root}${f.relative_path}" alt="Frame at ${f.timestamp}"><span>${f.timestamp}</span></div>`).join('');
    const transcript=m.transcript?.text?`<details><summary>Transcript</summary><pre class="mini-pre">${esc(m.transcript.text)}</pre></details>`:'';
    return `<div class="media-card"><div class="frames">${frames}</div><div class="meta"><h3>${esc(m.original_name)}</h3><p>${Number(m.duration_seconds||0).toFixed(1)} sec · ${(m.keyframes||[]).length} frames · provenance ${m.id}</p>${transcript}</div></div>`;
  }).join('')||'<div class="empty-state">Topic-only lab. No uploaded media.</div>';
}

function activateTab(name){$$('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===name));$$('.tab-panel').forEach(x=>x.classList.toggle('active',x.id===`tab-${name}`))}
$$('.tab').forEach(btn=>btn.onclick=()=>activateTab(btn.dataset.tab));

$('#enrich').onclick=async()=>{
  if(!currentSessionId)return;$('#enrich').disabled=true;setMessage('Running OCR and transcript enrichment…');
  try{const data=await api(`/api/sessions/${currentSessionId}/enrich`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ocr:true,transcribe:true})});currentData.session=data.session;latestPrompt=data.agent_prompt;$('#prompt').textContent=latestPrompt;renderMedia(data.session);$('#workspaceStatus').textContent='ENRICHED';setMessage('Evidence enriched.')}catch(err){setMessage(err.message,true)}finally{$('#enrich').disabled=false}
};
$('#generate').onclick=async()=>{
  if(!currentSessionId)return;$('#generate').disabled=true;setMessage('Generating the mechanism and simulation spec…');
  try{const data=await api(`/api/sessions/${currentSessionId}/generate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider:'openai'})});currentSpec=data.spec;renderAuthor(currentSpec);$('#workspaceStatus').textContent='GENERATED';activateTab('author');setMessage('AI-generated spec is ready for review.')}catch(err){setMessage(`${err.message} You can still use the agent prompt or author manually.`,true)}finally{$('#generate').disabled=false}
};

function renderAuthor(spec){
  if(!spec)return;$('#authorTitle').value=spec.title||'';$('#authorObjective').value=spec.objective||'';$('#authorGrammar').value=spec.visual_grammar||'state-machine';$('#specEditor').value=JSON.stringify(spec,null,2);
  $('#entityEditor').innerHTML=(spec.entities||[]).map((e,i)=>entityRow(e,i)).join('');
  $('#stageEditor').innerHTML=(spec.stages||[]).map((s,i)=>stageRow(s,i)).join('');bindEditorButtons();
}
function entityRow(e,i){return `<div class="editor-card entity-row" data-index="${i}"><div class="field"><label>Label</label><input data-field="label" value="${esc(e.label||'')}"></div><div class="field"><label>Kind</label><input data-field="kind" value="${esc(e.kind||'entity')}"></div><div class="field wide"><label>Detail</label><input data-field="detail" value="${esc(e.detail||'')}"></div><input type="hidden" data-field="id" value="${esc(e.id||`entity_${i+1}`)}"><button class="danger-link remove-entity">Remove</button></div>`}
function stageRow(s,i){const q=(s.questions||[])[0]||{};return `<div class="editor-card stage-row" data-index="${i}"><div class="stage-number">${String(i+1).padStart(2,'0')}</div><div class="field"><label>Stage label</label><input data-field="label" value="${esc(s.label||'')}"></div><div class="field"><label>Focus entities</label><input data-field="focus" value="${esc((s.focus_entities||[]).join(', '))}"></div><div class="field wide"><label>Summary</label><textarea data-field="summary" rows="2">${esc(s.summary||'')}</textarea></div><div class="field"><label>State patch JSON</label><textarea data-field="state_patch" rows="3">${esc(JSON.stringify(s.state_patch||{},null,2))}</textarea></div><div class="field"><label>Retrieval prompt</label><textarea data-field="question" rows="3">${esc(q.prompt||'')}</textarea></div><input type="hidden" data-field="id" value="${esc(s.id||`stage_${i+1}`)}"><button class="danger-link remove-stage">Remove</button></div>`}
function bindEditorButtons(){$$('.remove-entity').forEach(b=>b.onclick=()=>{b.closest('.entity-row').remove()});$$('.remove-stage').forEach(b=>b.onclick=()=>{b.closest('.stage-row').remove();renumberStages()})}
function renumberStages(){$$('.stage-row').forEach((row,i)=>row.querySelector('.stage-number').textContent=String(i+1).padStart(2,'0'))}
$('#addEntity').onclick=()=>{$('#entityEditor').insertAdjacentHTML('beforeend',entityRow({id:`entity_${Date.now()}`,label:'New entity',kind:'entity',detail:''},$$('.entity-row').length));bindEditorButtons()};
$('#addStage').onclick=()=>{$('#stageEditor').insertAdjacentHTML('beforeend',stageRow({id:`stage_${Date.now()}`,label:'New stage',summary:'Describe the real state transition.',focus_entities:[],state_patch:{},questions:[],provenance:[]},$$('.stage-row').length));bindEditorButtons();renumberStages()};
function collectAuthorSpec(){
  const spec=structuredClone(currentSpec||{});spec.title=$('#authorTitle').value.trim()||'Untitled simulation';spec.objective=$('#authorObjective').value.trim();spec.visual_grammar=$('#authorGrammar').value;
  spec.entities=$$('.entity-row').map((row,i)=>({id:row.querySelector('[data-field="id"]').value||`entity_${i+1}`,label:row.querySelector('[data-field="label"]').value.trim()||`Entity ${i+1}`,kind:row.querySelector('[data-field="kind"]').value.trim()||'entity',detail:row.querySelector('[data-field="detail"]').value.trim()}));
  spec.stages=$$('.stage-row').map((row,i)=>{
    let patch={};try{patch=JSON.parse(row.querySelector('[data-field="state_patch"]').value||'{}')}catch{throw new Error(`Stage ${i+1} state patch is not valid JSON.`)}
    const question=row.querySelector('[data-field="question"]').value.trim();const old=(currentSpec?.stages||[])[i]||{};const questions=question?[{...(old.questions?.[0]||{}),type:old.questions?.[0]?.type||'checkpoint',prompt:question,answer_text:old.questions?.[0]?.answer_text||'Explain the causal reason.',explanation:old.questions?.[0]?.explanation||''}]:[];
    return {id:row.querySelector('[data-field="id"]').value||`stage_${i+1}`,label:row.querySelector('[data-field="label"]').value.trim()||`Stage ${i+1}`,summary:row.querySelector('[data-field="summary"]').value.trim()||'Describe this transition.',focus_entities:row.querySelector('[data-field="focus"]').value.split(',').map(x=>x.trim()).filter(Boolean),state_patch:patch,questions,provenance:old.provenance||[]};
  });
  spec.fidelity_ledger=spec.fidelity_ledger?.length?spec.fidelity_ledger:[{element:'Author-created model',classification:'ASSUMED',detail:'Review and replace with source-grounded fidelity entries.',confidence:.5}];return spec;
}
$('#saveAuthor').onclick=async()=>{if(!currentSessionId)return;try{const spec=collectAuthorSpec();const data=await api(`/api/sessions/${currentSessionId}/spec`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({spec})});currentSpec=data.spec;renderAuthor(currentSpec);setMessage('Author changes saved.')}catch(err){setMessage(err.message,true)}};
$('#formatSpec').onclick=()=>{try{const obj=JSON.parse($('#specEditor').value);$('#specEditor').value=JSON.stringify(obj,null,2);currentSpec=obj;renderAuthor(currentSpec);setMessage('JSON formatted and loaded into the visual editor.')}catch(err){setMessage('The JSON editor contains invalid JSON.',true)}};
$('#specEditor').addEventListener('change',()=>{try{currentSpec=JSON.parse($('#specEditor').value);renderAuthor(currentSpec)}catch{}});

$('#compile').onclick=async()=>{
  if(!currentSessionId)return;$('#compile').disabled=true;setMessage('Validating and compiling runtime…');
  try{currentSpec=collectAuthorSpec();const data=await api(`/api/sessions/${currentSessionId}/compile`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({spec:currentSpec})});currentSpec=data.spec;setCompiledState(true);activateTab('preview');loadPreview();$('#workspaceStatus').textContent='COMPILED';setMessage('Simulation compiled successfully.')}catch(err){setMessage(err.message,true)}finally{$('#compile').disabled=false}
};
function setCompiledState(compiled){const preview=$('#previewLink'),exp=$('#exportLink');if(compiled){preview.href=`/runtime/${currentSessionId}`;exp.href=`/api/sessions/${currentSessionId}/export`;preview.classList.remove('disabled');exp.classList.remove('disabled');$('#previewEmpty').classList.add('hidden')}else{preview.removeAttribute('href');exp.removeAttribute('href');preview.classList.add('disabled');exp.classList.add('disabled');$('#previewEmpty').classList.remove('hidden');$('#previewFrame').classList.add('hidden')}}
function loadPreview(){if(!currentSessionId)return;const f=$('#previewFrame');f.src=`/runtime/${currentSessionId}?t=${Date.now()}`;f.classList.remove('hidden');$('#previewEmpty').classList.add('hidden')}
$('#reloadPreview').onclick=loadPreview;
$('#copyPrompt').onclick=async()=>{if(latestPrompt)await navigator.clipboard.writeText(latestPrompt);$('#copyPrompt').textContent='Copied';setTimeout(()=>$('#copyPrompt').textContent='Copy prompt',1000)};

$('#newLab').onclick=()=>{currentSessionId=null;currentData=null;currentSpec=null;selected=[];renderFiles();$('#workspace').classList.add('hidden');$('#welcome').classList.remove('hidden');$('#composer').classList.remove('hidden');$('#topic').focus();loadSessions()};
$('#refreshLabs').onclick=loadSessions;

loadProvider();loadSessions();
