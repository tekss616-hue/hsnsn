from pathlib import Path

css_path=Path('app/src/main/assets/social.css')
js_path=Path('app/src/main/assets/social.js')
css=css_path.read_text(encoding='utf-8')
js=js_path.read_text(encoding='utf-8')

marker='/* stable-four-item-main-nav */'
if marker not in css:
    css += '''\n/* stable-four-item-main-nav */
.hq-nav{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:0!important;padding-left:4px!important;padding-right:4px!important}
.hq-nav button{min-width:0!important;white-space:nowrap!important;font-size:clamp(11px,3.4vw,14px)!important;padding-inline:2px!important}
.game-overlay[hidden]{display:none!important}
'''

old="document.querySelectorAll('.game-overlay-back').forEach(b=>b.onclick=()=>window.showHQ?.());"
new="document.querySelectorAll('.game-overlay-back').forEach(b=>b.onclick=()=>{const r=$('rankingView'),st=$('gameStore');if(r)r.hidden=true;if(st)st.hidden=true;window.showHQ?.()});"
if old in js:
    js=js.replace(old,new,1)
elif new not in js:
    raise SystemExit('Overlay back handler not found; refusing unsafe patch')

css_path.write_text(css,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
print('Fixed overlay back navigation and four-item bottom bar')
