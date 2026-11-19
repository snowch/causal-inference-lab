import katex from './vendor/katex.mjs';
import {renderRich} from './rich-text.mjs';
// Copyright © 2026 Christopher Snow
import {attachEditor} from './editor.mjs';

// Prepare after the first paint, only on visible runnable lessons.
function schedulePreparation(start){
 const connection=navigator.connection;
 if(connection?.saveData||/^(slow-)?[23]g$/.test(connection?.effectiveType||'')||
    (connection?.downlink>0&&connection.downlink<1.5)||navigator.deviceMemory<=2)return ()=>{};
 let cancelled=false,scheduled=false,frame,task;
 const useIdle=typeof requestIdleCallback==='function';
 function cancel(){
  cancelled=true;
  document.removeEventListener('visibilitychange',schedule);
  cancelAnimationFrame(frame);
  if(useIdle)cancelIdleCallback(task);else clearTimeout(task);
 }
 function schedule(){
  if(cancelled||scheduled||document.visibilityState!=='visible')return;
  scheduled=true;
  frame=requestAnimationFrame(()=>{
   frame=requestAnimationFrame(()=>{
    const prepare=()=>{
     scheduled=false;
     if(cancelled||document.visibilityState!=='visible')return;
     cancel();
     start();
    };
    task=useIdle?requestIdleCallback(prepare,{timeout:2000}):setTimeout(prepare,500);
   });
  });
 }
 document.addEventListener('visibilitychange',schedule);
 schedule();
 return cancel;
}
const root=new URL('.',import.meta.url);
const $=id=>document.getElementById(id);
const prefix='cil:v1:';
const rich=text=>renderRich(text,tex=>katex.renderToString(tex,{displayMode:false,throwOnError:false,trust:false,strict:'warn'}));
let storageAvailable=true;
function get(key,fallback=''){
 try{return localStorage.getItem(prefix+key)??fallback}catch{storageAvailable=false;return fallback}
}
function put(key,value,onFailure=()=>showStorageError('This browser could not save your latest changes. They are still open on this page.')){
 try{localStorage.setItem(prefix+key,String(value));return true}catch{
  storageAvailable=false;
  onFailure();
  return false;
 }
}
function showStorageError(message){
 const target=$('storage-error');
 if(!target)return;
 target.hidden=false;
 if(target.textContent!==message)target.textContent=message;
}
function download(name,body,type='application/json'){
 const url=URL.createObjectURL(new Blob([body],{type}));
 const anchor=document.createElement('a');anchor.href=url;anchor.download=name;anchor.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function updateReadMarks(){
 document.querySelectorAll('[data-read]').forEach(el=>el.textContent=get('read:'+el.dataset.read)==='true'?'✓ Read':'');
}
$('theme')?.addEventListener('click',()=>{
 const theme=document.documentElement.dataset.theme==='dark'?'light':'dark';
 document.documentElement.dataset.theme=theme;
 try{localStorage.setItem('cil:theme',theme)}catch{}
 setThemeLabel();
});
function setThemeLabel(){const dark=document.documentElement.dataset.theme==='dark';$('theme')?.setAttribute('aria-label',`Switch to ${dark?'light':'dark'} theme`)}
setThemeLabel();
const menu=$('course-menu-toggle'),sidebar=$('course-sidebar');
if(menu&&sidebar){
 const close=()=>{sidebar.classList.remove('is-open');menu.setAttribute('aria-expanded','false')};
 menu.addEventListener('click',()=>{const open=sidebar.classList.toggle('is-open');menu.setAttribute('aria-expanded',String(open))});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&sidebar.classList.contains('is-open')){close();menu.focus()}});
 matchMedia('(min-width: 961px)').addEventListener('change',event=>{if(event.matches)close()});
}
const course=await fetch(new URL('course.json',root),{cache:'no-cache'}).then(response=>{if(!response.ok)throw new Error('Course data could not load.');return response.json()}).catch(()=>{
 const target=$('status')||$('progress-status');if(target)target.textContent=$('status')?'The lab could not load its controls. Reload the page or open Published example output.':'Course controls could not load. Reload this page or use the lesson links.';return null;
});
if(course){
 updateReadMarks();
 if($('search'))initializeOverview(course);
 const lesson=course.lessons.find(l=>l.slug===document.querySelector('[data-slug]')?.dataset.slug);
 if(lesson)initializeLesson(lesson);
 document.documentElement.dataset.ready='true';
}
function initializeOverview({lessons}){
 function progress(){
  const read=lessons.filter(l=>get('read:'+l.slug)==='true').length;
  $('progress-count').textContent=`${read} / ${lessons.length} read`;
  $('course-progress').value=read;
  const next=lessons.find(l=>get('read:'+l.slug)!=='true');
  $('start-course').href=next?'lessons/'+next.slug+'.html':'#course';
  $('start-label').textContent=read?(next?'Continue to the next unread lesson':'Review course contents'):'Start lesson 1';
  updateReadMarks();
 }
 progress();
 if(!storageAvailable)$('progress-status').textContent='This browser blocked access to saved progress.';
 const modules=[...document.querySelectorAll('.module')];
 const savedOpen=new Map();let searching=false;
 const revealModule=()=>{const id=location.hash.slice(1);const module=document.getElementById(id);if(module?.classList.contains('module'))module.open=true};
 revealModule();window.addEventListener('hashchange',revealModule);
 $('search').addEventListener('input',()=>{
  const words=$('search').value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  if(words.length&&!searching){for(const module of modules)savedOpen.set(module,module.open);searching=true}
  let count=0;
  document.querySelectorAll('.lesson-row').forEach(row=>{const match=words.every(word=>row.dataset.search.includes(word));row.hidden=!match;if(match)count++});
  for(const module of modules){
   module.hidden=![...module.querySelectorAll('.lesson-row')].some(row=>!row.hidden);
   if(words.length)module.open=!module.hidden;
   else if(searching)module.open=savedOpen.get(module)??false;
  }
  if(!words.length){searching=false;savedOpen.clear()}
  $('search-count').textContent=`${count} investigation${count===1?'':'s'}`;
  $('search-empty').hidden=count!==0;
 });
 $('export-progress').addEventListener('click',()=>{
  const data={};
  try{
   for(let i=0;i<localStorage.length;i++){
    const key=localStorage.key(i);
    if(key?.startsWith(prefix))data[key.slice(prefix.length)]=localStorage.getItem(key);
   }
  }catch{
   $('progress-status').textContent='Progress was not exported because this browser blocked access to saved work.';
   return;
  }
  download('causal-inference-lab-progress.json',JSON.stringify({course:'causal-inference-lab',schema:1,exported_at:new Date().toISOString(),data},null,2));
  $('progress-status').textContent='Downloaded the records saved in this browser. Download run results separately from the lesson.';
 });
 $('import-progress').addEventListener('change',async()=>{
  const file=$('import-progress').files[0];if(!file)return;
  try{
   if(file.size>1_000_000)throw new Error('Progress file must be smaller than 1 MB.');
   const record=JSON.parse(await file.text());
   if(record.course!=='causal-inference-lab'||record.schema!==1||!record.data||typeof record.data!=='object'||Array.isArray(record.data))throw new Error('Not a version 1 Causal Inference Lab progress file.');
   const slugs=new Set(lessons.map(l=>l.slug));
   const fields=new Set(['code','restore-backup','prediction','notes','quiz','report-question','report-plan','report-source','report-finding','report-limits']);
   const entries=Object.entries(record.data);
   for(const[key,value]of entries){
    const [type,slug,field,...extra]=key.split(':');
    if(extra.length||!slugs.has(slug)||typeof value!=='string'||value.length>300_000||!((type==='read'&&!field&&(value==='true'||value==='false'))||(type==='draft'&&fields.has(field))))throw new Error('Progress file contains an invalid record. Nothing has been imported.');
   }
   let saved=0;for(const[key,value]of entries)if(put(key,value))saved++;
   progress();$('progress-status').textContent=saved===entries.length?`Imported ${saved} saved records. Matching records in this browser were replaced.`:`Saved ${saved} of ${entries.length} imported records. The remaining records are still in your import file.`;
  }catch(error){$('progress-status').textContent=error.message}
  $('import-progress').value='';
 });
}
function initializeLesson(lesson){
 const slug=lesson.slug;
 const initialCode=$('code').value;
 let worker=null,timer=null,busy=false,lastSuccessfulRun=null,csv=null,csvName=null,revision=0;
 let plotUrls=[];
 function clearPlots(){for(const url of plotUrls)URL.revokeObjectURL(url);plotUrls=[];$('plots').replaceChildren()}
 function svgUrl(base64){const bytes=Uint8Array.from(atob(base64),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([bytes],{type:'image/svg+xml'}));plotUrls.push(url);return url}
 const initialQuiz=get(`draft:${slug}:quiz`);
 const draftKey=id=>`draft:${slug}:${id}`;
 $('code').readOnly=false;
 $('code').value=get(draftKey('code'),initialCode);
 let recoverableDraft=get(draftKey('restore-backup'),null);
 $('saved-draft').hidden=$('code').value===initialCode;
 const refreshEditor=attachEditor($('code'));
 document.querySelectorAll('[data-save]').forEach(el=>{
  el.value=get(draftKey(el.dataset.save));
  if(el.value&&el.closest('details')&&el.id!=='code')el.closest('details').open=true;
  if(el.id==='notes'&&el.value&&storageAvailable)showNoteStatus(true);
  el.addEventListener('input',()=>{
   const saved=put(draftKey(el.dataset.save),el.value);
   if(el.id==='notes')showNoteStatus(saved);
  });
 });
 function showNoteStatus(saved){
  const note=$('save-note');
  note.hidden=false;
  const message=saved?'Notes saved in this browser.':'Latest notes are open on this page only.';
  if(note.textContent!==message)note.textContent=message;
 }
 const read=$('mark-read');
 read.checked=get('read:'+slug)==='true';
 if(!storageAvailable)showStorageError('This browser blocked access to saved work.');
 read.addEventListener('change',()=>{
  const readStatus=$('read-status');
  const failed=()=>{readStatus.textContent='This browser could not save the reading mark.'};
  if(put('read:'+slug,read.checked,failed)){
   readStatus.textContent='';
   updateReadMarks();
  }else read.checked=!read.checked;
 });
 function stale(){
  if(!lastSuccessfulRun)return;
  const changed=$('code').value!==lastSuccessfulRun.source || csv!==lastSuccessfulRun.input_csv;
  $('output-provenance').textContent=changed
   ?'The code in the editor differs from this result. The result and its export are from your last successful run.'
   :lastSuccessfulRun.source===initialCode
    ?'Last successful run used the published code.'
    :'Last successful run used your edited code.';
  $('output-provenance').classList.toggle('stale',changed);
 }
 function updateRecovery(){
  $('recover-draft').hidden=recoverableDraft===null||recoverableDraft===$('code').value;
 }
 function showCode(code){
  const current=$('code').value;
  // Save the outgoing draft before replacing its persisted copy.
  let canSave=true;
  if(current!==initialCode&&current!==code){
   recoverableDraft=current;
   canSave=put(draftKey('restore-backup'),current);
  }
  $('code').value=code;
  refreshEditor();
  const saved=canSave&&put(draftKey('code'),code);
  $('saved-draft').hidden=true;
  updateRecovery();
  stale();
  $('editor-tools').open=false;
  $('code').focus();
  return saved;
 }
 updateRecovery();
 $('code').addEventListener('input',()=>{
  put(draftKey('code'),$('code').value);
  updateRecovery();
  stale();
 });
 $('code').addEventListener('keydown',event=>{
  if((event.ctrlKey||event.metaKey)&&event.key==='Enter'){event.preventDefault();if(!busy)run()}
 });
 $('restore').addEventListener('click',()=>{
  const saved=showCode(initialCode);
  $('status').textContent=recoverableDraft===null
   ?'Published code is open in the editor.'
   :saved
    ?'Published code is open. Use Recover draft in Editor tools to get your code back.'
    :'Published code is open. Recover draft can bring your code back while this page stays open.';
 });
 $('recover-draft').addEventListener('click',()=>{
  if(recoverableDraft===null)return;
  const saved=showCode(recoverableDraft);
  $('status').textContent=saved?'Recovered draft is open in the editor.':'Recovered draft is open on this page only.';
 });
 document.querySelector('.change-task a').addEventListener('click',event=>{
  event.preventDefault();
  const editor=$('code');
  editor.focus({preventScroll:true});
  const headerHeight=document.querySelector('.site-header').offsetHeight;
  const top=editor.getBoundingClientRect().top+window.scrollY-headerHeight-12;
  window.scrollTo({top,behavior:'instant'});
 });
 $('download-code').addEventListener('click',()=>download(slug+'.py',$('code').value,'text/x-python'));
 $('export-run').addEventListener('click',()=>{
  if(!lastSuccessfulRun)return;
  const notes={prediction:$('prediction').value,notes:$('notes').value};
  download(slug+'-run.json',JSON.stringify({...lastSuccessfulRun,notes},null,2));
 });
 function controls(running){
  const returnFocus=!running&&document.activeElement===$('stop');
  busy=running;document.querySelector('.experiment').classList.toggle('is-running',running);$('code-editor').setAttribute('aria-busy',String(running));$('run').disabled=running;$('stop').disabled=!running;$('stop').hidden=!running;$('restore').disabled=running;
  $('recover-draft').disabled=running;
  if($('csv-upload'))$('csv-upload').disabled=running;
  if($('clear-csv'))$('clear-csv').disabled=running||csv===null;
  if(returnFocus)$('run').focus({preventScroll:true});
 }
 let pythonPrepared=false, preparationTimer;
 function disposePython(){
  clearTimeout(preparationTimer);
  worker?.terminate();
  worker=null;
  pythonPrepared=false;
 }
 function pythonWorker(){
  return worker ??= new Worker(new URL('worker.js',root));
 }
 function preparePython(){
  if(worker||busy)return;
  try{
   const preparing=pythonWorker();
   const abandon=()=>{if(worker===preparing&&!busy)disposePython()};
   preparing.onerror=abandon;
   preparing.onmessage=({data})=>{
    if(data.type==='prepare-error'){abandon();return}
    if(data.type==='prepared'){
     clearTimeout(preparationTimer);
     pythonPrepared=true;
    }
   };
   preparationTimer=setTimeout(abandon,120000);
   preparing.postMessage({type:'prepare'});
  }catch{disposePython()}
 }
 const cancelPreparation=schedulePreparation(preparePython);
 function terminate(message){
  revision++;clearTimeout(timer);disposePython();controls(false);$('status').textContent=message;
  stale();
 }
 function showRunError(message){
  const details=message.trim();
  $('error-summary').textContent=details.split('\n').at(-1)||'Python could not finish.';
  $('error-trace').textContent=details;
  $('error-details').hidden=!details.includes('\n');
  $('run-error').hidden=false;
  stale();
 }
 $('stop').addEventListener('click',()=>terminate('Stopped. Select Run Python to start a new Python session.'));
 $('restart-python').addEventListener('click',()=>{
  cancelPreparation();
  terminate('Python session reset. Select Run Python to start again.');
 });
 async function run(){
  if(busy)return;
  cancelPreparation();
  clearTimeout(preparationTimer);
  const source=$('code').value,input=csv,inputName=csvName,runRevision=++revision;
  const runWasFocused=document.activeElement===$('run');
  $('editor-tools').open=false;
  $('run-error').hidden=true;
  $('error-details').open=false;
  controls(true);
  if(runWasFocused)$('stop').focus({preventScroll:true});
  $('status').textContent=pythonPrepared?'Starting your Python…':'Loading Python and statistics packages. This can take a moment…';
  if(lastSuccessfulRun)$('output-provenance').textContent='A new run is in progress. The result below is from your last successful run.';
  const fail=message=>{
   if(runRevision!==revision)return;
   terminate('Python could not finish. Check the message, then edit or run again.');
   showRunError(message);
  };
  timer=setTimeout(()=>fail('Python took more than two minutes to load. Check your connection, then select Run Python again.'),120000);
  try{pythonWorker()}catch(error){fail(error.message);return}
  worker.onerror=event=>fail(event.message||'The Python worker could not load.');
  worker.onmessage=({data})=>{
   if(runRevision!==revision)return;
   if(data.type==='running'){
    pythonPrepared=true;
    clearTimeout(timer);$('status').textContent='Running your Python…';
    timer=setTimeout(()=>fail('Python stopped after 45 seconds. Check for a loop or reduce the work, then select Run Python again.'),45000);return;
   }
   if(data.type==='error'){fail(data.message);return}
   if(data.type!=='result')return;
   clearTimeout(timer);controls(false);
   const {stdout,error,figures,figures_narrow=[],versions}=data.value;
   if(error){
    $('status').textContent='Python reported an error. Check the message below.';
    showRunError(error);
    return;
   }
   $('run-result').hidden=false;
   lastSuccessfulRun={schema:1,course:'causal-inference-lab',lesson:slug,executed_at:new Date().toISOString(),source,input_csv:input,input_name:inputName,stdout,error:null,figures_svg_base64:figures,figures_narrow_svg_base64:figures_narrow,versions,environment:{user_agent:navigator.userAgent,timing_scope:'Local browser Pyodide; see executed source for boundaries.'}};
   $('output').textContent=stdout||'No text was printed.';
   clearPlots();
   $('plots').replaceChildren(...figures.map((svg,i)=>{
    const figure=document.createElement('figure');figure.className='worked-figure';
    const picture=document.createElement('picture');
    const image=document.createElement('img');image.className='plot';image.src=svgUrl(svg);image.alt=source===initialCode&&lesson.plot&&i===0?lesson.plot:`Plot ${i+1} from your edited Python.`;
    if(figures_narrow[i]){const source=document.createElement('source');source.media='(max-width:700px)';source.srcset=svgUrl(figures_narrow[i]);picture.append(source)}
    picture.append(image);const caption=document.createElement('figcaption'),link=document.createElement('a');
    link.href=image.src;link.target='_blank';link.rel='noopener';link.textContent='Open full-size figure ↗';caption.append(link);figure.append(picture,caption);return figure;
   }));
   $('status').textContent='Completed.';
   $('example-takeaway').hidden=source!==initialCode;
   $('export-run').disabled=false;$('export-run').hidden=false;stale();
  };
  worker.postMessage({type:'run',source,csv:input});
 }
 $('run').addEventListener('click',run);
 window.addEventListener('pagehide',event=>{
  cancelPreparation();
  revision++;
  clearTimeout(timer);
  disposePython();
  if(busy){
   controls(false);
   $('status').textContent='Select Run Python to start again.';
   stale();
  }
  if(!event.persisted)clearPlots();
 });
 let quizAttempt=null;
 try{quizAttempt=JSON.parse(initialQuiz)}catch{}
 if(quizAttempt&&Number.isInteger(quizAttempt.answer)&&quizAttempt.answer>=0&&quizAttempt.answer<lesson.options.length){
  const choice=document.querySelector(`input[name=answer][value="${quizAttempt.answer}"]`);
  if(choice){choice.checked=true;showAnswer(quizAttempt.answer);}
 }
 function showAnswer(answer){
  const correct=answer===lesson.correct;
  const feedback=$('quiz-feedback');
  feedback.replaceChildren();
  feedback.classList.toggle('incorrect',!correct);
  const title=document.createElement('b');title.textContent=correct?'That reasoning fits.':'Reconsider the comparison.';
  const text=document.createElement('span');text.innerHTML=rich(lesson.feedback);
  feedback.append(title,text);
 }
 $('quiz').addEventListener('change',()=>{
  $('quiz-feedback').replaceChildren();
  $('quiz-feedback').classList.remove('incorrect');
 });
 $('quiz').addEventListener('submit',event=>{
  event.preventDefault();const selected=document.querySelector('input[name=answer]:checked');
  if(!selected){$('quiz-feedback').textContent='Choose an answer first, then check your reasoning.';return}
  const answer=Number(selected.value),correct=answer===lesson.correct;
  put(draftKey('quiz'),JSON.stringify({answer,correct,at:new Date().toISOString()}));
  showAnswer(answer);
  $('quiz-feedback').focus({preventScroll:true});
 });
 if($('export-report')){
  $('export-report').addEventListener('click',()=>{
   const fields=[['question','Target question'],['plan','Design and assumptions'],['source','Data sources'],['finding','Estimate and uncertainty'],['limits','Limits and next test']];
   const body=['# Causal Inference Lab · Investigation',`Exported ${new Date().toISOString()}`];
   for(const[id,label]of fields)body.push(`## ${label}\n\n${$('report-'+id).value||'[Not recorded]'}`);
   body.push('## Execution record');
   if(lastSuccessfulRun){
    const {executed_at,input_name,versions,source,stdout,input_csv}=lastSuccessfulRun;
    body.push(`Last successful run at ${executed_at}. Input: ${input_name||'Inspect the source for starter data.'}\n\nVersions: ${JSON.stringify(versions)}`);
    body.push('### Exact executed Python\n\n```python\n'+source+'\n```');
    body.push('### Actual output\n\n```text\n'+stdout+'\n```');
    if(input_csv!==null)body.push('### Exact input CSV\n\n```csv\n'+input_csv+'\n```');
    if($('code').value!==source||csv!==input_csv)body.push('The editor or selected input changed after this run. The record above preserves the last successful execution.');
   }else body.push('No successful execution was recorded on this page. Worked output is available separately in the lesson.');
   body.push('## Field notes\n\n'+($('notes').value||'[Not recorded]'));
   download('causal-investigation.md',body.join('\n\n')+'\n','text/markdown');
   $('report-status').textContent=lastSuccessfulRun?'Downloaded your report with the last successful run.':'Downloaded your report. It has no run result yet.';
  });
 }
 controls(false);
}

document.addEventListener('click',event=>{
 for(const details of document.querySelectorAll('.header-help[open],.editor-tools[open]'))if(!details.contains(event.target))details.open=false;
});
document.addEventListener('keydown',event=>{
 if(event.key!=='Escape')return;
 const open=[...document.querySelectorAll('.header-help[open],.editor-tools[open]')];
 const target=open.find(d=>d.contains(document.activeElement))||open.at(-1);
 if(target){target.open=false;target.querySelector('summary').focus()}
});
