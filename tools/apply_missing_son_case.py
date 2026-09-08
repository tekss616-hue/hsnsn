from pathlib import Path

ROOT = Path('app/src/main/assets')
html_path = ROOT / 'index.html'
js_path = ROOT / 'app.js'
css_path = ROOT / 'styles.css'

html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

CASE_HTML = r'''
<main id="caseRoom" class="case-room" hidden>
  <div class="case-ambient" aria-hidden="true"><i></i><i></i><i></i></div>
  <header class="case-room-head">
    <button id="caseExit" class="case-exit" aria-label="الخروج">×</button>
    <div><small>القضية 01</small><strong>الابن المفقود</strong></div>
    <div id="caseTimer" class="case-timer">15:00</div>
  </header>
  <section id="caseBriefing" class="case-briefing">
    <div class="case-seal">ملف سري</div>
    <h1>الابن المفقود</h1>
    <p>ريان السالم، 19 عامًا، غادر منزله الساعة 7:36 مساءً. هاتفه مغلق، وآخر ستة أشخاص كانوا جزءًا من يومه موجودون هنا.</p>
    <div class="case-objective"><b>هدف القضية</b><span>اعثروا على ريان، افهموا لماذا اختفى، واتخذوا القرار الذي يعيده إلى الأمان قبل انتهاء الوقت.</span></div>
    <button id="revealRole" class="case-primary">استلام بطاقة الدور</button>
  </section>
  <section id="roleCard" class="role-card" hidden>
    <small>بطاقتك السرية</small><h2 id="roleName">سالم — الأب</h2>
    <p id="roleStory"></p>
    <div class="role-secret"><b>ما تعرفه</b><span id="roleKnowledge"></span></div>
    <div class="role-secret"><b>هدفك الشخصي</b><span id="roleGoal"></span></div>
    <p class="role-warning">لا تقرأ بطاقتك حرفيًا للآخرين. تكلم كشخصيتك وبأسلوبك أنت.</p>
    <button id="enterCase" class="case-primary">دخول غرفة التحقيق</button>
  </section>
  <section id="casePlay" class="case-play" hidden>
    <div class="case-status"><span id="casePhase">التحقيق المفتوح</span><small id="caseHint">استخدم أسماء الشخصيات عندما توجه لهم الكلام.</small></div>
    <div id="caseCast" class="case-cast"></div>
    <div id="caseFeed" class="case-feed" aria-live="polite"></div>
    <div class="case-compose"><input id="caseInput" maxlength="320" placeholder="تكلم داخل دورك… مثال: نورة، وش سمعتي؟"><button id="caseSend">إرسال</button></div>
    <button id="caseConclude" class="case-conclude">تقديم الاستنتاج النهائي</button>
  </section>
  <section id="caseDecision" class="case-decision" hidden>
    <small>القرار النهائي</small><h2>ما الذي حدث لريان؟</h2>
    <label>أين ريان؟<select id="decisionLocation"><option value="">اختر…</option><option value="station">محطة الحافلات</option><option value="lake">ممشى البحيرة القديم</option><option value="friend">منزل صديق</option></select></label>
    <label>لماذا خرج؟<select id="decisionReason"><option value="">اختر…</option><option value="kidnap">تم اختطافه</option><option value="pressure">خرج بإرادته بعد ضغط وخلافات متراكمة</option><option value="money">هرب بسبب مشكلة مالية</option></select></label>
    <label>ماذا تفعلون الآن؟<select id="decisionAction"><option value="">اختر…</option><option value="force">نطلب منه العودة فورًا بدون نقاش</option><option value="safe">نتأكد أنه آمن، ونرسل شخصًا يثق به ليستمع له بهدوء</option><option value="leave">نتركه ولا نتواصل معه</option></select></label>
    <button id="submitDecision" class="case-primary">اعتماد القرار</button>
  </section>
  <section id="caseEnding" class="case-ending" hidden><div id="endingMark" class="ending-mark">✓</div><h2 id="endingTitle"></h2><p id="endingText"></p><div id="endingTruth" class="ending-truth"></div><button id="caseReturn" class="case-primary">العودة إلى المقر</button></section>
</main>
'''

if 'id="caseRoom"' not in html:
    html = html.replace('<div id="settingsSheet"', CASE_HTML + '\n<div id="settingsSheet"', 1)

CSS = r'''

/* Missing Son playable prototype */
.case-room{position:fixed;inset:0;z-index:80;background:#08090d;color:#f3f0e8;overflow:auto;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom);font-family:inherit}
.case-room[hidden]{display:none!important}.case-ambient{position:fixed;inset:0;pointer-events:none;overflow:hidden;background:radial-gradient(circle at 50% 0,#30121655,transparent 38%),linear-gradient(#08090d,#0b0c11)}
.case-ambient i{position:absolute;inset:auto 0;height:1px;background:#ffffff0c;animation:caseScan 7s linear infinite}.case-ambient i:nth-child(2){top:43%;animation-delay:-2s}.case-ambient i:nth-child(3){top:72%;animation-delay:-5s}@keyframes caseScan{from{transform:translateY(-20vh)}to{transform:translateY(120vh)}}
.case-room-head{position:sticky;top:0;z-index:5;display:grid;grid-template-columns:44px 1fr auto;gap:12px;align-items:center;padding:14px 16px;background:#090a0eea;border-bottom:1px solid #ffffff12;backdrop-filter:blur(12px)}
.case-room-head small{display:block;color:#a58d7c;font-size:11px}.case-room-head strong{font-size:17px}.case-exit{width:38px;height:38px;border-radius:12px;border:1px solid #ffffff18;background:#ffffff08;color:#eee;font-size:24px}.case-timer{font-variant-numeric:tabular-nums;font-weight:900;letter-spacing:1px;color:#f0d7b4;background:#c42f3b18;border:1px solid #c42f3b55;padding:8px 10px;border-radius:12px}
.case-briefing,.role-card,.case-decision,.case-ending{position:relative;z-index:2;max-width:620px;margin:8vh auto 0;padding:28px 22px}.case-seal{display:inline-block;border:1px solid #8e2630;color:#e7747e;padding:6px 10px;border-radius:8px;font-size:12px}.case-briefing h1{font-size:34px;margin:18px 0 10px}.case-briefing p,.role-card p,.case-ending p{line-height:1.9;color:#c8c3bb}.case-objective,.role-secret,.ending-truth{margin:22px 0;padding:16px;border:1px solid #ffffff12;background:#ffffff06;border-radius:16px}.case-objective b,.role-secret b{display:block;margin-bottom:8px;color:#e6c49b}.case-objective span,.role-secret span{line-height:1.8;color:#d6d1c8}.case-primary{width:100%;border:0;border-radius:15px;padding:15px 16px;background:linear-gradient(135deg,#8f1e29,#bd3844);color:white;font-weight:900;font-size:15px;box-shadow:0 10px 30px #7c18253d}.role-card small,.case-decision>small{color:#d25a65}.role-card h2,.case-decision h2{font-size:27px;margin:10px 0 18px}.role-warning{font-size:12px!important;color:#998f87!important;border-right:2px solid #8f1e29;padding-right:10px}
.case-play{position:relative;z-index:2;min-height:calc(100vh - 70px);display:flex;flex-direction:column;max-width:760px;margin:auto}.case-status{padding:13px 16px;border-bottom:1px solid #ffffff0e;display:flex;justify-content:space-between;gap:10px}.case-status span{font-weight:800}.case-status small{color:#8f8a83}.case-cast{display:flex;gap:8px;overflow-x:auto;padding:12px 14px;border-bottom:1px solid #ffffff0d}.case-person{flex:0 0 auto;padding:8px 10px;border-radius:12px;background:#ffffff07;border:1px solid #ffffff0f;font-size:12px}.case-person.me{border-color:#9a2734;color:#ffd7d9}.case-feed{flex:1;min-height:360px;padding:12px 14px 160px;overflow:auto}.case-msg{margin:9px 0;padding:11px 13px;border-radius:14px;background:#ffffff07;border:1px solid #ffffff0b;line-height:1.65;max-width:88%}.case-msg b{display:block;font-size:11px;color:#c7a77f;margin-bottom:3px}.case-msg.player{margin-right:auto;background:#7d1b2530;border-color:#9d2c3650}.case-msg.gm{max-width:100%;background:#12151d;border-color:#b4935f44;text-align:center;color:#e3d7c4}.case-msg.clue{max-width:100%;background:#18120d;border-color:#d29f524f}.case-compose{position:fixed;z-index:5;bottom:72px;left:0;right:0;max-width:760px;margin:auto;padding:10px 14px;display:flex;gap:8px;background:linear-gradient(transparent,#08090d 30%)}.case-compose input{flex:1;min-width:0;border:1px solid #ffffff18;background:#111218;color:#fff;border-radius:14px;padding:13px}.case-compose button{border:0;background:#8f1e29;color:#fff;border-radius:14px;padding:0 17px;font-weight:800}.case-conclude{position:fixed;z-index:6;bottom:18px;left:14px;right:14px;max-width:732px;margin:auto;border:1px solid #cfa96f55;background:#17130d;color:#f0d7b4;border-radius:13px;padding:12px;font-weight:800}.case-decision label{display:block;margin:16px 0;color:#a9a29a}.case-decision select{width:100%;margin-top:7px;padding:13px;border-radius:12px;border:1px solid #ffffff18;background:#111218;color:#fff}.case-ending{text-align:center}.ending-mark{width:70px;height:70px;margin:auto;display:grid;place-items:center;border-radius:50%;border:1px solid #b8905d;color:#e7c896;font-size:33px}.case-ending h2{font-size:28px}.ending-truth{text-align:right;line-height:1.9;color:#c8c3bb}
@media(max-width:520px){.case-briefing,.role-card,.case-decision,.case-ending{margin-top:3vh;padding:24px 17px}.case-briefing h1{font-size:30px}.case-status{flex-direction:column}.case-feed{padding-bottom:170px}}
'''
if '/* Missing Son playable prototype */' not in css:
    css += CSS

JS = r'''

// Missing Son playable case prototype. Local deterministic game engine for first hands-on test.
const MISSING_SON={
 roles:[
  {name:'سالم',label:'الأب',story:'أنت والد ريان. تشاجرت معه قبل خروجه بست عشرة دقيقة.',knowledge:'قلت له: «إذا مو عاجبك البيت، الباب قدامك». وقبل ثلاثة أيام وجدت تذكرة حافلة إلى مدينة أخرى ومزقتها.',goal:'اعثر على ريان، وقرر بنفسك متى تعترف بما حدث بينكما.'},
  {name:'مها',label:'الأم',story:'أنت والدة ريان وتحاولين إبقاء الأسرة متماسكة.',knowledge:'ريان أخبرك قبل أسبوع أنه يريد ترك تخصصه الجامعي. وكان يذهب أحيانًا إلى مكان قديم يأخذه إليه والده وهو صغير.',goal:'ساعدي في العثور عليه، وقرري متى يصبح كسر وعدك له ضروريًا.'},
  {name:'ياسر',label:'الصديق',story:'أنت أقرب أصدقاء ريان وآخر من وصلته رسالة منه.',knowledge:'كتب لك الساعة 8:07: «خلاص. قررت.» ثم «لا تقول لأحد وين بروح». وكان يفكر في ترك الجامعة والعمل بمدينة أخرى.',goal:'ساعد في العثور عليه، من دون أن تجعل خلافكما القديم يحرف التحقيق.'},
  {name:'نورة',label:'الأخت',story:'أنت أخت ريان وكنت في غرفتك أثناء الشجار.',knowledge:'سمعته يقول: «حتى المكان الوحيد اللي كنت أرتاح فيه خربته علي». ووجدت صورة قديمة له مع والده قرب بحيرة.',goal:'أوصل المعلومة للشخص المناسب في الوقت المناسب.'},
  {name:'ماجد',label:'العم',story:'أنت عم ريان وتعتقد أن سالم يضغط عليه أكثر مما ينبغي.',knowledge:'قبل أسبوع سألك ريان: «لو الواحد بدأ حياته من جديد، تتوقع أهله يسامحونه؟» ولم تأخذ السؤال بجدية.',goal:'ساعد في كشف الحقيقة، ولا تجعل شعورك بالذنب يتحول إلى اتهام أعمى.'},
  {name:'أبو فهد',label:'الجار',story:'أنت جار العائلة ورأيت ريان بعد خروجه بدقائق.',knowledge:'كان يحمل حقيبة ظهر صغيرة. وسمعته يقول لسائق: «ممشى البحيرة القديم» أو ربما «الحديقة القديمة».',goal:'اجعل الآخرين يأخذون شهادتك بجدية وحدد ما سمعته بدقة.'}
 ],
 cast:['سالم — الأب','مها — الأم','ياسر — الصديق','نورة — الأخت','ماجد — العم','أبو فهد — الجار']
};
let missingRun=null;
function showOnlyCase(){[intro,envelopeScreen,profile,hq,splash,$('social')].forEach(x=>x&&(x.hidden=true));$('settingsSheet').hidden=true;$('caseRoom').hidden=false}
function resetCaseScreens(){['caseBriefing','roleCard','casePlay','caseDecision','caseEnding'].forEach(id=>$(id).hidden=id!=='caseBriefing');$('caseFeed').innerHTML='';$('caseInput').value=''}
function openMissingSon(){showOnlyCase();resetCaseScreens();missingRun={role:MISSING_SON.roles[Math.floor(Math.random()*MISSING_SON.roles.length)],left:900,timer:null,started:false,events:new Set()};$('caseTimer').textContent='15:00'}
window.openMissingSon=openMissingSon;
function caseMsg(speaker,text,type=''){const feed=$('caseFeed');const d=document.createElement('div');d.className='case-msg '+type;d.innerHTML=`<b>${speaker}</b>${String(text).replace(/[<>]/g,m=>m==='<'?'&lt;':'&gt;')}`;feed.appendChild(d);feed.scrollTop=feed.scrollHeight}
function setupRole(){const r=missingRun.role;$('roleName').textContent=`${r.name} — ${r.label}`;$('roleStory').textContent=r.story;$('roleKnowledge').textContent=r.knowledge;$('roleGoal').textContent=r.goal;$('caseBriefing').hidden=true;$('roleCard').hidden=false}
function renderCaseCast(){const r=missingRun.role;$('caseCast').innerHTML=MISSING_SON.cast.map(x=>`<span class="case-person ${x.startsWith(r.name+' ')||x.startsWith(r.name+' —')?'me':''}">${x}${x.startsWith(r.name+' —')?' · أنت':''}</span>`).join('')}
function tickMissing(){if(!missingRun||!missingRun.started)return;missingRun.left=Math.max(0,missingRun.left-1);const m=Math.floor(missingRun.left/60),s=missingRun.left%60;$('caseTimer').textContent=`${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;const elapsed=900-missingRun.left;
 const fire=(key,sec,fn)=>{if(elapsed>=sec&&!missingRun.events.has(key)){missingRun.events.add(key);fn()}};
 fire('pressure',15,()=>caseMsg('ماجد','سالم، آخر واحد تشاجر معه أنت. وش قلت له قبل ما يطلع؟'));
 fire('nora',35,()=>caseMsg('نورة','أنا… سمعت ريان يقول شيء وقت الشجار، بس مو متأكدة وش كان يقصد.'));
 fire('neighbor',55,()=>caseMsg('أبو فهد','أنا شفته وهو طالع. كان معه شنطة صغيرة… وسمعته يطلب من السائق مكان قديم.'));
 fire('phone',180,()=>caseMsg('دليل جديد','تم العثور على هاتف ريان على مقعد قرب محطة الحافلات.','clue'));
 fire('search',300,()=>caseMsg('تحليل الهاتف','آخر بحث: «مواعيد آخر حافلة الليلة». وقبله بـ17 دقيقة: «هل ممشى البحيرة القديم مفتوح ليلًا؟»','clue'));
 fire('audio',420,()=>caseMsg('تسجيل صوتي','«ما أبي أحد يلحقني… أبي بس أفكر.» وفي الخلفية يُسمع صوت قطار.','clue'));
 fire('final',720,()=>{caseMsg('مدير القضية','بقيت ثلاث دقائق. اربطوا الصورة وصوت القطار وكلام العائلة، ثم قدموا استنتاجكم.','gm');$('casePhase').textContent='مرحلة الحسم'});
 if(missingRun.left<=0){clearInterval(missingRun.timer);showDecision()}}
function enterMissingCase(){$('roleCard').hidden=true;$('casePlay').hidden=false;renderCaseCast();missingRun.started=true;caseMsg('مدير القضية','مرّت أربع ساعات على اختفاء ريان. أحدكم يعرف أكثر مما يقول. تكلموا، اسألوا، ولا تفترضوا أن أول تفسير هو الحقيقة.','gm');caseMsg(missingRun.role.name,'أنت الآن داخل دورك. بقية الشخصيات في هذه النسخة التجريبية يديرها محرك القضية.','gm');missingRun.timer=setInterval(tickMissing,1000)}
function localCharacterReply(text){const t=String(text).trim();if(!t)return;const has=n=>t.includes(n);if(has('نورة'))return ['نورة','سمعته يقول لأبوي: «حتى المكان الوحيد اللي كنت أرتاح فيه خربته علي». وبعدها لقيت صورة قديمة لهم عند بحيرة.'];if(has('سالم'))return ['سالم','تشاجرنا، صحيح. قلت كلام ندمت عليه… وقبل أيام مزقت تذكرة سفر كانت معه.'];if(has('مها'))return ['مها','كان يقول إنه ما عاد يبي تخصصه. وفيه مكان قديم كان سالم يأخذه له وهو صغير.'];if(has('ياسر'))return ['ياسر','آخر رسالة منه كانت: «خلاص. قررت. لا تقول لأحد وين بروح».'];if(has('ماجد'))return ['ماجد','سألني قبل أسبوع إذا أهله بيسامحونه لو بدأ حياته من جديد. حسبتها فضفضة.'];if(has('أبو فهد')||has('فهد'))return ['أبو فهد','أغلب ظني قال ممشى البحيرة القديم. وكان معه شنطة صغيرة بس.'];if(/بحير|قطار|محطة|تذكرة/.test(t))return ['مدير القضية','هذه نقطة مهمة. وجّه السؤال لشخصية بالاسم حتى تربط المعلومة بمن يعرفها.'];return ['ماجد','حدد سؤالك لمين. نادِ الشخص باسمه عشان نعرف الكلام موجه له.']}
function sendCaseLine(){if(!missingRun?.started)return;const input=$('caseInput'),text=input.value.trim();if(!text)return;caseMsg(missingRun.role.name,text,'player');input.value='';setTimeout(()=>{const r=localCharacterReply(text);caseMsg(r[0],r[1])},450)}
function showDecision(){if(!missingRun)return;if(missingRun.timer){clearInterval(missingRun.timer);missingRun.timer=null}missingRun.started=false;$('casePlay').hidden=true;$('caseDecision').hidden=false}
function finishDecision(){const loc=$('decisionLocation').value,reason=$('decisionReason').value,action=$('decisionAction').value;if(!loc||!reason||!action){$('submitDecision').textContent='أكمل الخيارات الثلاثة';setTimeout(()=>$('submitDecision').textContent='اعتماد القرار',1200);return}const perfect=loc==='lake'&&reason==='pressure'&&action==='safe',found=loc==='lake';$('caseDecision').hidden=true;$('caseEnding').hidden=false;if(perfect){$('endingMark').textContent='✓';$('endingTitle').textContent='تم العثور على ريان — نهاية ممتازة';$('endingText').textContent='وُجد ريان سالمًا عند ممشى البحيرة القديم. لم يُجبر على العودة فورًا؛ جلس معه الشخص الذي اختاره الفريق واستمع له أولًا.'}else if(found){$('endingMark').textContent='◇';$('endingTitle').textContent='تم العثور على ريان — لكن القضية لم تنتهِ';$('endingText').textContent='وصلتم إلى المكان الصحيح، لكن تفسير السبب أو طريقة التعامل معه أبقت المسافة بينه وبين العائلة.'}else{$('endingMark').textContent='×';$('endingTitle').textContent='انتهى وقت التحقيق';$('endingText').textContent='اتجه البحث إلى المكان الخطأ. بعد ساعة عُثر على ريان سالمًا عند ممشى البحيرة القديم.'}$('endingTruth').innerHTML='<b>ما لم يكن واضحًا في البداية</b><br>ريان لم يُختطف. ترك هاتفه قرب المحطة ليبتعد قليلًا عن الجميع، ثم ذهب إلى المكان الذي ارتبط عنده بذكريات أهدأ مع والده. تذكرة السفر كانت حقيقية، لكنها لم تكن دليلًا على مكانه هذه الليلة.'}
function closeMissingCase(){if(missingRun?.timer)clearInterval(missingRun.timer);missingRun=null;$('caseRoom').hidden=true;showHQ(store.get('investigator_name','المحقق'))}
if($('revealRole'))$('revealRole').onclick=setupRole;if($('enterCase'))$('enterCase').onclick=enterMissingCase;if($('caseSend'))$('caseSend').onclick=sendCaseLine;if($('caseInput'))$('caseInput').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();sendCaseLine()}});if($('caseConclude'))$('caseConclude').onclick=showDecision;if($('submitDecision'))$('submitDecision').onclick=finishDecision;if($('caseReturn'))$('caseReturn').onclick=closeMissingCase;if($('caseExit'))$('caseExit').onclick=closeMissingCase;
'''
if '// Missing Son playable case prototype.' not in js:
    js += JS

# Make first free case the playable prototype and route only that card into the case engine.
js = js.replace("const cases={free:[['الغرفة 317','جريمة غامضة']", "const cases={free:[['الابن المفقود','غموض اجتماعي']", 1)
old = "if(c){store.set('last_case',c.dataset.case);c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100})}"
new = "if(c){store.set('last_case',c.dataset.case);c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100});if(c.dataset.case==='free-0'){setTimeout(()=>window.openMissingSon?.(),90)}}"
if old in js:
    js = js.replace(old, new, 1)

html_path.write_text(html,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
css_path.write_text(css,encoding='utf-8')
print('Applied Missing Son playable prototype')
