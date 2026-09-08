from pathlib import Path

html_path = Path('app/src/main/assets/index.html')
js_path = Path('app/src/main/assets/app.js')

html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')

# Keep an inert compatibility shell because legacy startup helpers still reference #intro,
# but remove the actual video/skip/resume cinematic UI.
start = html.find('<main id="intro"')
if start != -1:
    end = html.find('</main>', start)
    if end == -1:
        raise SystemExit('Intro closing tag not found')
    html = html[:start] + '<main id="intro" hidden aria-hidden="true"></main>' + html[end + len('</main>'):]
elif 'id="intro"' not in html:
    html = html.replace('<body>', '<body><main id="intro" hidden aria-hidden="true"></main>', 1)

# Legacy app.js binds listeners to introVideo/resumeIntro/skipIntro during parsing.
# Supply inert JS objects so those bindings cannot throw before boot(), then force boot()
# down the already-seen path. No visible intro is rendered and no media is loaded.
needle = "const intro=$('intro'),video=$('introVideo'),resume=$('resumeIntro'),envelopeScreen=$('envelopeScreen'),envelope=$('envelope'),profile=$('profile'),hq=$('hq'),error=$('formError'),splash=$('quickSplash');"
replacement = "const intro=$('intro'),video=$('introVideo')||{pause(){},play(){return Promise.resolve()},load(){},addEventListener(){},removeAttribute(){},muted:true,volume:0,currentTime:0},resume=$('resumeIntro')||{hidden:true,textContent:'',onclick:null},envelopeScreen=$('envelopeScreen'),envelope=$('envelope'),profile=$('profile'),hq=$('hq'),error=$('formError'),splash=$('quickSplash');"
if needle not in js:
    raise SystemExit('Startup declaration changed; refusing unsafe intro removal')
js = js.replace(needle, replacement, 1)

# These two legacy bindings target controls that no longer exist.
js = js.replace("$('skipIntro').onclick=showEnvelope;resume.onclick=()=>video.play();envelope.onclick=openEnvelope;", "resume.onclick=()=>video.play();envelope.onclick=openEnvelope;", 1)

# Force the normal post-intro startup path before boot executes.
boot_call = "document.addEventListener('click',e=>{const c=e.target.closest?.('.case-card');if(c){store.set('last_case',c.dataset.case);c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100})}});boot();"
boot_fixed = "document.addEventListener('click',e=>{const c=e.target.closest?.('.case-card');if(c){store.set('last_case',c.dataset.case);c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100})}});store.set('intro_seen',true);boot();"
if boot_call not in js:
    raise SystemExit('boot() call changed; refusing unsafe intro removal')
js = js.replace(boot_call, boot_fixed, 1)

html_path.write_text(html, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
print('Removed cinematic intro and preserved startup compatibility')
