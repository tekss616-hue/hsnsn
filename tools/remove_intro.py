from pathlib import Path

html_path = Path('app/src/main/assets/index.html')
js_path = Path('app/src/main/assets/app.js')

html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')

# Keep only an inert compatibility shell for legacy intro references.
start = html.find('<main id="intro"')
if start != -1:
    end = html.find('</main>', start)
    if end == -1:
        raise SystemExit('Intro closing tag not found')
    html = html[:start] + '<main id="intro" hidden aria-hidden="true"></main>' + html[end + len('</main>'):]
elif 'id="intro"' not in html:
    html = html.replace('<body>', '<body><main id="intro" hidden aria-hidden="true"></main>', 1)

# Remove the short startup splash completely.
splash_start = html.find('<main id="quickSplash"')
if splash_start != -1:
    splash_end = html.find('</main>', splash_start)
    if splash_end == -1:
        raise SystemExit('Quick splash closing tag not found')
    html = html[:splash_start] + html[splash_end + len('</main>'):]

needle = "const intro=$('intro'),video=$('introVideo'),resume=$('resumeIntro'),envelopeScreen=$('envelopeScreen'),envelope=$('envelope'),profile=$('profile'),hq=$('hq'),error=$('formError'),splash=$('quickSplash');"
replacement = "const intro=$('intro'),video=$('introVideo')||{pause(){},play(){return Promise.resolve()},load(){},addEventListener(){},removeAttribute(){},muted:true,volume:0,currentTime:0},resume=$('resumeIntro')||{hidden:true,textContent:'',onclick:null},envelopeScreen=$('envelopeScreen'),envelope=$('envelope'),profile=$('profile'),hq=$('hq'),error=$('formError'),splash=null;"
if needle not in js:
    raise SystemExit('Startup declaration changed; refusing unsafe intro removal')
js = js.replace(needle, replacement, 1)

js = js.replace("$('skipIntro').onclick=showEnvelope;resume.onclick=()=>video.play();envelope.onclick=openEnvelope;", "resume.onclick=()=>video.play();envelope.onclick=openEnvelope;", 1)

# Remove the artificial startup delay/splash. Existing accounts go straight to HQ;
# signed-out/new users go straight to login. The envelope/account flows still remain available.
old_boot = "function boot(){const name=store.get('investigator_name');renderCases();if(store.get('intro_seen',false)){stopSceneAudio();hideAll();splash.hidden=false;setTimeout(()=>{if(name)showHQ(name);else{splash.hidden=true;profile.hidden=false;profile.classList.add('ready');setAuthMode('login');idle(warmNativeAuth,100)}},160)}else startIntro()}"
new_boot = "function boot(){const name=store.get('investigator_name');renderCases();stopSceneAudio();hideAll();if(name)showHQ(name);else{profile.hidden=false;profile.classList.add('ready');setAuthMode('login');idle(warmNativeAuth,100)}}"
if old_boot not in js:
    raise SystemExit('boot() startup flow changed; refusing unsafe splash removal')
js = js.replace(old_boot, new_boot, 1)

boot_call = "document.addEventListener('click',e=>{const c=e.target.closest?.('.case-card');if(c){store.set('last_case',c.dataset.case);c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100})}});boot();"
boot_fixed = "document.addEventListener('click',e=>{const c=e.target.closest?.('.case-card');if(c){store.set('last_case',c.dataset.case);c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100})}});store.set('intro_seen',true);boot();"
if boot_call not in js:
    raise SystemExit('boot() call changed; refusing unsafe intro removal')
js = js.replace(boot_call, boot_fixed, 1)

html_path.write_text(html, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
print('Removed cinematic intro and startup splash; direct boot enabled')
