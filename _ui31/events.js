// Local-only UI state. No phone, chat or attachment contents stored persistently.
Object.assign(S,{attendancePeriod:'month',attendanceFrom:'2026-09-01',attendanceTo:'2026-09-17',attendanceSubject:'all',tutorThreads:null,tutorActive:null,tutorCounter:0});
PAID.delete('attendance'); // attendancePage enforces its own demo gate, keeping both tabs accessible.
LABELS.study='Учёба';LABELS.space='Все разделы';LABELS.works='Сделанные задания';LABELS.uploads='Загруженные задания';LABELS.goals='Баллы до автомата';LABELS.groups='Автоматизация групп';LABELS.referrals='Заработок и рефералы';
renderers.study=studyPage;
sourceLinks.push(['AI Input With File · Kokonut UI','Референс крупного ввода и карточек вложений; собственная адаптация','https://21st.dev/@kokonutd/components/ai-input-with-file'],['Prompt Input · Prompt Kit','Референс панели действий и отправки/остановки','https://21st.dev/community/components/ibelick/prompt-input/with-actions']);

document.addEventListener('click',e=>{
 const b=e.target.closest('[data-action]');if(!b||b.disabled)return;
 const a=b.dataset.action,id=b.dataset.id;
 if(a==='reset'){S.tutorThreads?.forEach(t=>clearTimeout(t.timer));S.tutorThreads=null;S.chat=[];S.attendancePeriod='month';S.attendanceSubject='all';return}
 const intercepted=['prepare','new-chat','chat-context','select-chat-context','suggest'];
 if(!a.startsWith('c31-')&&!intercepted.includes(a))return;
 e.preventDefault();e.stopImmediatePropagation();
 switch(a){
 case 'c31-period':if(['week','month','semester','custom'].includes(b.dataset.period)){S.attendancePeriod=b.dataset.period;render(false)}break;
 case 'c31-att-detail':{const r=attendanceRecords().find(x=>x.id===id);if(!r)return;const s=subjects.find(s=>s.id===r.subject);modal('Отметка о посещении',`<h2>${s.name}</h2><dl class="mt">${key('Дата',shortDate(r.date))}${key('Время',r.time+'–'+r.end)}${key('Вид занятия',r.kind)}${key('Отметка',{present:'Присутствовал',absent:'Пропуск',unknown:'Нет отметки'}[r.status])}</dl><div class="note mt">Демонстрационный пример. Отметки БРСО здесь не изменяются. «Нет отметки» не означает пропуск.</div>`);break}
 case 'prepare':{const sid=subjects.some(s=>s.id===id)?id:S.subject,t=tutorNew(sid);t.mode='prepare';t.draft='Помоги составить план подготовки по предмету «'+subjects.find(s=>s.id===sid).name+'».';route('tutor');break}
 case 'new-chat':case 'c31-new':tutorNew();closeDialog(true);render(false);break;
 case 'c31-history':tutorHistory();break;
 case 'c31-thread':{const t=S.tutorThreads?.find(t=>t.id===b.dataset.thread);if(!t)return;S.tutorActive=t.id;S.subject=t.subject;S.chat=t.messages;closeDialog(true);render(false);break}
 case 'chat-context':case 'select-chat-context':tutorChooseSubject(id);break;
 case 'c31-mode':{const t=tutorState();if(['explain','solve','prepare'].includes(b.dataset.mode)){t.mode=b.dataset.mode;render(false)}break}
 case 'suggest':case 'c31-suggestion':{const t=tutorState();t.draft=b.dataset.text||'';if(b.dataset.mode)t.mode=b.dataset.mode;render(false);$('#chat-input')?.focus({preventScroll:true});tutorDraft();break}
 case 'c31-example':{const t=tutorState();if(!t.draft.trim())t.draft='Как разобраться в теме, если пока не понимаю, с чего начать?';tutorSend();break}
 case 'c31-stop':{const t=tutorState();clearTimeout(t.timer);t.pending=false;render(false);toast('Демо-ответ остановлен. Модель не вызывалась.');break}
 case 'c31-attach':$('#c31-file-input')?.click();break;
 case 'c31-remove-file':{const t=tutorState(),n=Number(b.dataset.file);if(Number.isInteger(n)&&n>=0&&n<t.files.length)t.files.splice(n,1);render(false);break}
 case 'c31-answer-source':modal('Это пример, а не ответ AI',`<p class="small">Текст заранее подготовлен, чтобы проверить дизайн диалога. Он не основан на твоём вопросе, приложенных файлах или БРСО.</p><div class="note mt">В рабочем продукте учитель должен опираться на проверенные требования и материалы. В этом макете модель не подключена.</div>`);break;
 case 'c31-copy':{const m=tutorState().messages[Number(b.dataset.message)];if(!m)return;if(navigator.clipboard?.writeText)navigator.clipboard.writeText(m.text).then(()=>toast('Текст примера скопирован.')).catch(()=>modal('Скопировать текст',`<textarea class="c31-copy-text" readonly aria-label="Текст примера для копирования">${esc(m.text)}</textarea>`));else modal('Скопировать текст',`<textarea class="c31-copy-text" readonly aria-label="Текст примера для копирования">${esc(m.text)}</textarea>`);break}
 }
},true);
document.addEventListener('submit',e=>{
 if(!['c31-chat-form','c31-range-form'].includes(e.target.id))return;
 e.preventDefault();e.stopImmediatePropagation();
 if(e.target.id==='c31-chat-form'){tutorDraft();tutorSend();return}
 const from=$('#c31-from').value,to=$('#c31-to').value;
 const valid=v=>/^2026-\d\d-\d\d$/.test(v)&&!isNaN(Date.parse(v))&&new Date(v+'T12:00:00Z').toISOString().slice(0,10)===v;
 if(!valid(from)||!valid(to)||from<'2026-09-01'||to>'2026-12-31'||from>to){$('#c31-date-error').textContent='Выбери даты с 1 сентября по 31 декабря. Начало не должно быть позже окончания.';return}
 S.attendanceFrom=from;S.attendanceTo=to;render(false);
},true);
document.addEventListener('input',e=>{if(e.target.id==='chat-input'&&$('#c31-chat-form'))tutorDraft()});
document.addEventListener('change',e=>{
 if(e.target.id==='c31-att-subject'){S.attendanceSubject=e.target.value;render(false)}
 if(e.target.id==='c31-file-input'){
  const t=tutorState();let rejected=0;
  for(const f of Array.from(e.target.files||[])){
   if(t.files.length>=4||f.size>10*1024*1024||!(/\.(pdf|docx|pptx|xlsx|txt|png|jpg|jpeg|webp)$/i.test(f.name))){rejected++;continue}
   if(!t.files.some(x=>x.name===f.name&&x.size===f.size))t.files.push({name:f.name.slice(0,200),size:f.size});
  }
  e.target.value='';render(false);toast(rejected?'Некоторые файлы не добавлены: максимум 4, до 10 МБ, только поддерживаемые форматы.':'Показаны только названия. Файлы не читаются и никуда не отправляются.');
 }
});
document.addEventListener('keydown',e=>{
 if(e.target.id==='chat-input'&&$('#c31-chat-form')&&e.key==='Enter'&&!e.shiftKey&&!e.isComposing&&!matchMedia('(pointer:coarse)').matches){e.preventDefault();tutorDraft();tutorSend()}
});
