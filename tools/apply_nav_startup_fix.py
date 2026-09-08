from pathlib import Path
import re

idx_path=Path('app/src/main/assets/index.html')
css_path=Path('app/src/main/assets/social.css')
js_path=Path('app/src/main/assets/social.js')
idx=idx_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')
js=js_path.read_text(encoding='utf-8')

# The roleplay copy update changed the old 3-item HQ markup, so the earlier
# gameplay patch could no longer match it and inject the functional 4-item nav.
# Restore the same existing functions/IDs without changing the visual shell.
nav='<nav class="hq-nav"><button class="active" data-main="play">اللعب</button><button id="rankingTab" data-main="ranking">التصنيف</button><button id="storeTab" data-main="store">المتجر</button><button id="openProfileTab">الملف</button></nav>'
idx,count=re.subn(r'<nav class="hq-nav">.*?</nav>',nav,idx,count=1,flags=re.S)
if count!=1:
    raise SystemExit('HQ navigation not found; refusing unsafe patch')

# Keep the visible text aligned with the new live-roleplay concept only.
idx=idx.replace('<h1>تصنيف المحققين</h1>','<h1>تصنيف اللاعبين</h1>')
idx=idx.replace('ترتيبك التنافسي سيُحتسب من نتائج التحقيقات.','ترتيبك يتطور من مشاركاتك ونتائجك داخل تجارب عيش الدور.')
idx=idx.replace('<h1>متجر المحقق</h1>','<h1>متجر اللاعب</h1>')
idx=idx.replace('بطاقات المحقق<small>','بطاقات الشخصية<small>')

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

idx_path.write_text(idx,encoding='utf-8')
css_path.write_text(css,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
print('Restored working store/ranking navigation and four-item bottom bar')
