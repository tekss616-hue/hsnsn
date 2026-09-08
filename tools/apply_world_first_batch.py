from pathlib import Path
import zipfile, shutil

assets=Path('app/src/main/assets')
zip_path=assets/'HSNSN_World_9_Images.zip'
world_dir=assets/'world'
world_dir.mkdir(parents=True,exist_ok=True)
expected=['01_beach.png','02_palace.png','03_garden.png','04_hospital.png','05_police_prison.png','06_market.png','07_restaurant.png','08_hotel.png','09_harbor.png']
if zip_path.exists():
    with zipfile.ZipFile(zip_path) as z:
        by_base={Path(n).name:n for n in z.namelist() if not n.endswith('/')}
        for name in expected:
            if name not in by_base: raise SystemExit('World image missing from ZIP: '+name)
            with z.open(by_base[name]) as src,(world_dir/name).open('wb') as dst: shutil.copyfileobj(src,dst)
else:
    missing=[n for n in expected if not (world_dir/n).exists()]
    if missing: raise SystemExit('World ZIP/images missing: '+', '.join(missing))

idx=assets/'index.html'; html=idx.read_text(encoding='utf-8')
cssf=assets/'social.css'; css=cssf.read_text(encoding='utf-8')
jsf=assets/'social.js'; js=jsf.read_text(encoding='utf-8')

if 'id="worldGame"' not in html:
    world=r'''<main id="worldGame" class="world-game" hidden dir="rtl"><div class="world-scene" id="worldScene"></div><header class="world-head"><button id="worldBack" class="world-round">‹</button><div class="world-place"><small>العالم</small><h2 id="worldPlaceName">الشاطئ</h2></div><button id="worldPlacesOpen" class="world-places-btn">الأماكن</button></header><section class="world-presence"><div id="worldAvatars" class="world-avatars"></div><span id="worldPresenceText">الموجودون الآن</span></section><section id="worldMessages" class="world-messages"></section><form id="worldComposer" class="world-composer"><input id="worldInput" maxlength="500" autocomplete="off" placeholder="اكتب رسالة…"><button type="submit">إرسال</button></form><aside id="worldPlaces" class="world-places" hidden><div class="world-places-card"><header><h3>أماكن العالم</h3><button id="worldPlacesClose">×</button></header><p>انتقل لأي مكان. سترى عدد الموجودين قبل الدخول، وليس هوياتهم.</p><div id="worldPlacesGrid" class="world-places-grid"></div></div></aside></main>'''
    html=html.replace('<script src="app.js"></script>',world+'<script src="app.js"></script>',1)

# Keep first-batch CSS, then override temporary gradients with approved artwork.
if '/* social-world-approved-images */' not in css:
    css += r'''
/* social-world-approved-images */
.world-scene{height:clamp(235px,38vh,390px)!important;background-position:center 42%!important;background-repeat:no-repeat!important;background-size:cover!important;filter:saturate(.94) contrast(1.03)}
.world-scene:after{background:linear-gradient(180deg,rgba(0,0,0,.08) 0%,rgba(7,10,13,.25) 52%,#070a0d 100%)!important}
.world-game[data-place="beach"] .world-scene{background-image:url('world/01_beach.png')!important}
.world-game[data-place="palace"] .world-scene{background-image:url('world/02_palace.png')!important}
.world-game[data-place="garden"] .world-scene{background-image:url('world/03_garden.png')!important}
.world-game[data-place="hospital"] .world-scene{background-image:url('world/04_hospital.png')!important;background-position:center 48%!important}
.world-game[data-place="police"] .world-scene{background-image:url('world/05_police_prison.png')!important;background-position:center 46%!important}
.world-game[data-place="market"] .world-scene{background-image:url('world/06_market.png')!important}
.world-game[data-place="restaurant"] .world-scene{background-image:url('world/07_restaurant.png')!important;background-position:center 48%!important}
.world-game[data-place="hotel"] .world-scene{background-image:url('world/08_hotel.png')!important;background-position:center 45%!important}
.world-game[data-place="harbor"] .world-scene{background-image:url('world/09_harbor.png')!important;background-position:center 48%!important}
.world-head,.world-presence{position:relative;z-index:1;text-shadow:0 1px 8px #000}.world-head{background:linear-gradient(180deg,rgba(0,0,0,.36),transparent)}
@media(max-width:430px) and (min-height:780px){.world-scene{height:300px!important}}
@media(min-width:700px){.world-scene{height:min(44vh,430px)!important}.world-place h2{font-size:28px}}
@media(orientation:landscape) and (max-height:600px){.world-scene{height:58vh!important;background-position:center 48%!important}.world-head{padding-top:calc(env(safe-area-inset-top) + 7px)}.world-presence{padding-bottom:7px}}
'''

# Replace the initial preview prototype entirely so old canned Nader/system duplication cannot survive.
marker=';(()=>{\nconst SOCIAL_WORLD_FIRST_BATCH=true'
pos=js.find(marker)
if pos!=-1:
    js=js[:pos]
js += r'''
;(()=>{
const SOCIAL_WORLD_FIRST_BATCH=true,$=id=>document.getElementById(id);
const places=[['beach','الشاطئ','🏖️'],['palace','القصر','🏰'],['garden','الحديقة','🌳'],['hospital','المستشفى','🏥'],['police','مركز الشرطة والسجن','🚔'],['market','السوق','🛍️'],['restaurant','المطعم','🍽️'],['hotel','الفندق','🏨'],['harbor','الميناء','⚓']];
let preview=false,current='beach',counts={beach:3,palace:2,garden:1,hospital:2,police:0,market:1,restaurant:2,hotel:0,harbor:1},messages={};
const nameOf=k=>(places.find(x=>x[0]===k)||[])[1]||k;
function profileName(){try{const p=JSON.parse(localStorage.getItem('profile_cache')||'{}');return p.name||p.displayName||p.username||'اللاعب'}catch{return'اللاعب'}}
function ensure(k){if(!messages[k])messages[k]=[]}
function addSystem(k,text,key){ensure(k);if(key&&messages[k].some(x=>x.system&&x.key===key))return;messages[k].push({system:true,text,key:key||''})}
function render(){ensure(current);const g=$('worldGame');if(!g)return;g.dataset.place=current;$('worldPlaceName').textContent=nameOf(current);$('worldPresenceText').textContent='الموجودون الآن · '+(counts[current]||0);const av=$('worldAvatars');av.innerHTML='';for(let i=0;i<Math.min(counts[current]||0,5);i++){const x=document.createElement('span');x.className='world-avatar';x.textContent=i===0?'أ':String(i+1);av.appendChild(x)}const m=$('worldMessages');m.innerHTML='';messages[current].forEach(x=>{const d=document.createElement('div');if(x.system){d.className='world-system';d.textContent=x.text}else{d.className='world-msg'+(x.mine?' mine':'');d.innerHTML='<b></b><span></span>';d.querySelector('b').textContent=x.name;d.querySelector('span').textContent=x.text}m.appendChild(d)});m.scrollTop=m.scrollHeight;renderPlaces()}
function renderPlaces(){const grid=$('worldPlacesGrid');if(!grid)return;grid.innerHTML='';places.forEach(([k,n,e])=>{const b=document.createElement('button');b.type='button';b.className='world-place-card'+(k===current?' active':'');b.innerHTML='<strong>'+e+' '+n+'</strong><small>الموجودون الآن · '+(counts[k]||0)+'</small>';b.onclick=()=>move(k);grid.appendChild(b)})}
function move(k){if(k===current){$('worldPlaces').hidden=true;return}const who=profileName(),from=current;addSystem(from,'غادر '+who+' '+nameOf(from),'leave:'+who+':'+from+':'+Date.now());current=k;addSystem(k,'وصل '+who+' إلى '+nameOf(k),'arrive:'+who+':'+k+':'+Date.now());$('worldPlaces').hidden=true;render()}
function openWorld(isPreview){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;g.hidden=false;document.body.style.overflow='hidden';ensure(current);render()}
function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.style.overflow=''}
document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true;if(e.target.closest?.('#adminPreviewOpen'))setTimeout(()=>openWorld(true),0)},true);
$('worldComposer')?.addEventListener('submit',e=>{e.preventDefault();const i=$('worldInput'),t=i.value.trim();if(!t)return;ensure(current);messages[current].push({name:profileName(),text:t,mine:true});i.value='';render()});
window.HSNSNWorld={open:()=>openWorld(false),preview:()=>openWorld(true),move};
})();
'''

idx.write_text(html,encoding='utf-8');cssf.write_text(css,encoding='utf-8');jsf.write_text(js,encoding='utf-8')
print('Applied approved 9 world images, responsive scene layout, clean movement messages, and no canned Nader preview replies')
