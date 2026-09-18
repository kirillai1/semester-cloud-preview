"""Apply the reviewed, narrowly scoped UI change to the byte-verified Cloud v3.
No external downloads. Refuse an unexpected baseline rather than overwrite it.
Usage: python apply.py BASE_HTML OUTPUT_HTML
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT=Path(__file__).resolve().parent
EXPECTED='ee4d6c53324a417a3dbb1ea4bed55779d71496aaba70c25953e7f07c5dff0769'

def once(text: str, old: str, new: str) -> str:
    if text.count(old)!=1:
        raise ValueError('Expected exactly one replacement for: '+old[:80])
    return text.replace(old,new,1)

def build(base: Path, output: Path) -> None:
    raw=base.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:
        raise ValueError('Baseline differs from reviewed Cloud v3. Reconcile before publishing.')
    html=raw.decode('utf-8')
    parts=re.split(r'(?m)^// @function (\w+)\n',(ROOT/'functions.js').read_text('utf-8'))
    extra=[]
    for i in range(1,len(parts),2):
        name,body=parts[i],parts[i+1].strip()
        pattern=r'(?m)^function '+re.escape(name)+r'\([^\n]*$'
        matches=list(re.finditer(pattern,html))
        if matches:
            if len(matches)!=1: raise ValueError('Duplicate function '+name)
            html=html[:matches[0].start()]+body+html[matches[0].end():]
        else: extra.append(body)
    html=once(html,"const BUILD='cloud-v3-2026-09-18';","const BUILD='cloud-v3.1-nav-tutor-2026-09-18';")
    html=once(html,"head('Твой ритм недели.','Найти следующую пару. Увидеть всю неделю. Выдохнуть.')+fresh()","head('Расписание','Пары, аудитории и посещаемость — в одном разделе.')+scheduleTabs('schedule')+fresh()")
    html=once(html,"['schedule','calendar','Ритм']","['schedule','calendar','Расписание']")
    html=once(html,"['subjects','book','Учёба']","['study','book','Учёба']")
    html=once(html,"if(ix<0)ix=['subject','teachers','teacher','attendance','checkpoints','exams','goals','assignments','assignment'].includes(S.page)?2:4;","if(ix<0)ix=S.page==='attendance'?1:['subjects','subject','teachers','teacher','checkpoints','exams','goals','assignments','assignment'].includes(S.page)?2:4;")
    # Sidebar: keep all existing routes; place attendance alongside schedule rather than under Study.
    html=once(html,"['schedule','calendar'],['subjects','book'],['teachers','users'],['attendance','checkcircle']","['schedule','calendar'],['attendance','checkcircle'],['subjects','book'],['teachers','users']")
    html=once(html,"n===2?'<div class=\"side-label\">Учёба</div>'","n===3?'<div class=\"side-label\">Учёба</div>'")
    html=once(html,"'Всё нужное — в понятных маленьких мирах.'","'Учебные сведения и работы по разделам.'") if "'Всё нужное — в понятных маленьких мирах.'" in html else html
    html=html.replace('ДЕМО · V3','ДЕМО · V3.1').replace('· Cloud v3`','· Cloud v3.1`').replace('Дизайн-студия · v3','Настройки просмотра · v3.1').replace('Cloud v3 · светлая','Cloud v3.1 · светлая')
    html=once(html,"function preview(){modal('Твой Cloud.'","function preview(){modal('Настройки демо'")
    html=once(html,"<div class=\"dialog-subtitle\">Выбери настроение</div>","<div class=\"dialog-subtitle\">Тема оформления</div>")
    titles={
      "Видеть больше.<br>Понимать своё.":"Предметы",
      "Твоя цель.<br>Твой маршрут.":"Баллы до автомата",
      "Люди за предметами.":"Преподаватели",
      "Маленькие шаги.<br>Видимый результат.":"Контрольные точки",
      "Что дальше по учёбе?":"Задания БРСО",
      "Сессия без хаоса.":"Сессия и зачёты",
      "Сделано.<br>И всегда под рукой.":"Сделанные задания",
      "Файл отправлен.<br>Что дальше?":"Загруженные задания",
      "У каждой работы<br>свой характер.":"Оформление файлов",
      "На одной волне.<br>Под твоим контролем.":"Автоматизация групп",
      "Хорошее хочется<br>разделить.":"Заработок и рефералы",
      "Поддержка.<br>В твоём масштабе.":"Подписка и пакеты",
      "Твоё. Личное.":"Профиль и настройки",
      "Только важное.":"Уведомления",
      "Разберёмся за минуту.":"Помощь",
    }
    for old,new in titles.items():
        html=once(html,"'"+old+"'","'"+new+"'")
    html=html.replace('Cloud v3 · не официальный','Cloud v3.1 · не официальный')
    html=once(html,"function render(scroll=true){theme();","function render(scroll=true){const c31input=$('#chat-input'),c31focus=document.activeElement===c31input&&c31input?{start:c31input.selectionStart,end:c31input.selectionEnd}:null;theme();")
    # Keep the source HTML standalone: no missing CSS or JS after deployment.
    css=(ROOT/'styles.css').read_text('utf-8')+'\n.c31-copy-text{width:100%;min-height:260px;background:var(--card);color:var(--ink);font-size:14px;border:1px solid var(--line);border-radius:12px;padding:14px}\n'
    first_style_end=html.index('</style>')
    html=html[:first_style_end]+'\n'+css+'\n'+html[first_style_end:]
    events=(ROOT/'events.js').read_text('utf-8')
    injection='\n'+'\n'.join(extra)+'\n'+events+'\n'
    html=once(html,"const initial=location.hash.slice(1);",injection+"const initial=location.hash.slice(1);")
    html=once(html,"works:works.length}),set:","works:works.length,attendancePeriod:S.attendancePeriod,attendanceSubject:S.attendanceSubject,tutorThread:S.tutorActive}),set:")
    html=once(html,"if(S.page==='tutor')requestAnimationFrame(()=>{const l=$('#chat-messages');if(l)l.scrollTop=l.scrollHeight})","if(S.page==='tutor')requestAnimationFrame(()=>{const l=$('#chat-messages');if(l)l.scrollTop=tutorState().messages.length?l.scrollHeight:0;tutorDraft();if(c31focus&&$('#chat-input')){$('#chat-input').focus({preventScroll:true});$('#chat-input').setSelectionRange(c31focus.start,c31focus.end)}})")
    html=html.replace('<title>Cloud v3', '<title>Cloud v3.1')
    if 'src="app.js"' in html or 'href="styles.css"' in html: raise ValueError('Output must be standalone')
    if html.count('function tutorPage(')!=1 or html.count('function attendancePage(')!=1:raise ValueError('Ambiguous renderers')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(html,encoding='utf-8')
    print('Built',output.name,'bytes',output.stat().st_size,'sha256',hashlib.sha256(output.read_bytes()).hexdigest())

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: apply.py BASE_HTML OUTPUT_HTML')
    build(Path(sys.argv[1]),Path(sys.argv[2]))
