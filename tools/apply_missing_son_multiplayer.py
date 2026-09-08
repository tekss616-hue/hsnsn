from pathlib import Path

ROOT=Path('app/src/main/assets')
html_path=ROOT/'index.html'; js_path=ROOT/'app.js'; css_path=ROOT/'styles.css'
java_path=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
html=html_path.read_text(encoding='utf-8'); js=js_path.read_text(encoding='utf-8'); css=css_path.read_text(encoding='utf-8'); java=java_path.read_text(encoding='utf-8')

# Add multiplayer lobby ahead of the existing briefing.
if 'id="caseLobby"' not in html:
    lobby=r'''
  <section id="caseLobby" class="case-lobby">
    <div class="case-seal">اختبار جماعي</div>
    <h1>الابن المفقود</h1>
    <p>ثلاثة لاعبين حقيقيين + ثلاث شخصيات يديرها محرك القضية. أنشئ غرفة وأرسل الرمز لإخوانك، أو ادخل رمز غرفة موجودة.</p>
    <div id="caseLobbyActions" class="case-lobby-actions">
      <button id="createCaseRoom" class="case-primary">إنشاء غرفة</button>
      <div class="case-code-row"><input id="caseRoomCodeInput" inputmode="numeric" maxlength="6" placeholder="رمز الغرفة"><button id="joinCaseRoom">دخول</button></div>
    </div>
    <div id="caseWaiting" class="case-waiting" hidden>
      <small>رمز الغرفة</small><div id="caseRoomCode" class="case-room-code">------</div>
      <p id="caseWaitingText">بانتظار اللاعبين… 1/3</p>
      <div id="caseHumanSlots" class="case-human-slots"></div>
      <button id="continueBriefing" class="case-primary" hidden>اكتمل الفريق — متابعة</button>
    </div>
  </section>
'''
    html=html.replace('  <section id="caseBriefing"', lobby+'  <section id="caseBriefing"',1)

CSS=r'''

/* Missing Son multiplayer slice */
body.case-immersive{overflow:hidden!important;background:#050609!important}
body.case-immersive>main:not(#caseRoom),body.case-immersive>#settingsSheet,body.case-immersive>#appDialog{display:none!important}
.case-lobby{position:relative;z-index:2;max-width:620px;margin:5vh auto 0;padding:28px 22px}.case-lobby h1{font-size:34px;margin:18px 0 10px}.case-lobby p{line-height:1.9;color:#c8c3bb}.case-lobby-actions{display:grid;gap:14px;margin-top:26px}.case-code-row{display:flex;gap:9px}.case-code-row input{flex:1;min-width:0;text-align:center;letter-spacing:5px;font-size:20px;border:1px solid #ffffff18;background:#111218;color:#fff;border-radius:14px;padding:13px}.case-code-row button{border:1px solid #9d2c36;background:#3a1117;color:#fff;border-radius:14px;padding:0 20px;font-weight:900}.case-waiting{text-align:center;padding:16px 0}.case-waiting>small{color:#9d8f83}.case-room-code{font-size:38px;font-weight:900;letter-spacing:9px;margin:8px 0;color:#f0d7b4}.case-human-slots{display:grid;gap:8px;margin:18px 0}.human-slot{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border:1px solid #ffffff12;background:#ffffff05;border-radius:13px}.human-slot small{color:#8d877f}.human-slot.ready small{color:#74c69d}.case-briefing[hidden],.case-lobby[hidden]{display:none!important}.case-conclude.locked{opacity:.45;pointer-events:none}.case-timer.waiting{color:#b4aaa0;border-color:#ffffff1a;background:#ffffff08}
@media(max-width:520px){.case-lobby{margin-top:2vh;padding:22px 17px}.case-lobby h1{font-size:30px}}
'''
if '/* Missing Son multiplayer slice */' not in css: css+=CSS

# Native Firestore bridge for one private 3-human room.
if 'new CaseBridge(), "NativeCase"' not in java:
    java=java.replace('webView.addJavascriptInterface(new SocialBridge(), "NativeSocial");','webView.addJavascriptInterface(new SocialBridge(), "NativeSocial");\n        webView.addJavascriptInterface(new CaseBridge(), "NativeCase");',1)

CASE_BRIDGE=r'''

    public class CaseBridge {
        private com.google.firebase.firestore.ListenerRegistration roomListener;
        private com.google.firebase.firestore.ListenerRegistration messageListener;
        private String watchedRoom = "";

        private void emitCase(JSONObject payload) {
            runOnUiThread(() -> webView.evaluateJavascript("window.onNativeCaseEvent&&window.onNativeCaseEvent(" + payload + ")", null));
        }
        private void fail(String action, String message) {
            try { JSONObject p=new JSONObject();p.put("ok",false);p.put("action",action);p.put("message",message==null?"تعذر إكمال العملية.":message);emitCase(p);} catch(Exception ignored){}
        }
        private String roomCode() { return String.format(Locale.US, "%06d", 100000 + new java.util.Random().nextInt(900000)); }
        private List<String> roleOrder(String code) {
            List<String> r=new ArrayList<>(Arrays.asList("سالم","مها","ياسر","نورة","ماجد","أبو فهد"));
            java.util.Collections.shuffle(r,new java.util.Random(code.hashCode())); return r;
        }
        @JavascriptInterface public void setImmersive(boolean on) {
            runOnUiThread(() -> {
                if(on) getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
                else getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
            });
        }
        @JavascriptInterface public void createRoom() {
            runOnUiThread(() -> { FirebaseUser u=currentUser(); if(u==null){fail("room","سجّل الدخول أولًا.");return;} ensureFirestore();
                String code=roomCode(); Map<String,Object> d=new HashMap<>();
                d.put("caseId","missing-son");d.put("hostUid",u.getUid());d.put("members",new ArrayList<>(Arrays.asList(u.getUid())));Map<String,Object> names=new HashMap<>();names.put(u.getUid(),u.getDisplayName()==null?"محقق":u.getDisplayName());d.put("names",names);d.put("ready",new ArrayList<String>());d.put("status","waiting");d.put("createdAt",FieldValue.serverTimestamp());
                firestore.collection("caseRooms").document(code).set(d).addOnSuccessListener(v->{watchRoom(code);}).addOnFailureListener(e->fail("room",e.getLocalizedMessage()));
            });
        }
        @JavascriptInterface public void joinRoom(String raw) {
            runOnUiThread(() -> { FirebaseUser u=currentUser(); if(u==null){fail("join","سجّل الدخول أولًا.");return;} ensureFirestore(); String code=raw==null?"":raw.trim(); if(!code.matches("\\d{6}")){fail("join","رمز الغرفة يجب أن يكون 6 أرقام.");return;}
                com.google.firebase.firestore.DocumentReference ref=firestore.collection("caseRooms").document(code);
                firestore.runTransaction(tx->{DocumentSnapshot s=tx.get(ref);if(!s.exists())throw new RuntimeException("الغرفة غير موجودة.");String status=s.getString("status");if(status!=null&&!status.equals("waiting")&&!status.equals("briefing"))throw new RuntimeException("بدأت هذه الغرفة بالفعل.");
                    List<String> mem=(List<String>)s.get("members");if(mem==null)mem=new ArrayList<>();else mem=new ArrayList<>(mem);if(!mem.contains(u.getUid())){if(mem.size()>=3)throw new RuntimeException("الغرفة مكتملة.");mem.add(u.getUid());}
                    Map<String,Object> names=(Map<String,Object>)s.get("names");if(names==null)names=new HashMap<>();else names=new HashMap<>(names);names.put(u.getUid(),u.getDisplayName()==null?"محقق":u.getDisplayName());Map<String,Object> up=new HashMap<>();up.put("members",mem);up.put("names",names);
                    if(mem.size()==3){List<String> roles=roleOrder(code);Map<String,Object> rb=new HashMap<>();for(int i=0;i<3;i++)rb.put(mem.get(i),roles.get(i));up.put("roleByUid",rb);up.put("aiRoles",roles.subList(3,6));up.put("status","briefing");}
                    tx.update(ref,up);return null;}).addOnSuccessListener(v->watchRoom(code)).addOnFailureListener(e->fail("join",e.getLocalizedMessage()));
            });
        }
        @JavascriptInterface public void watchRoom(String code) {
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();stopWatch();watchedRoom=code;
                com.google.firebase.firestore.DocumentReference ref=firestore.collection("caseRooms").document(code);
                roomListener=ref.addSnapshotListener((s,e)->{if(e!=null){fail("watch",e.getLocalizedMessage());return;}if(s==null||!s.exists())return;try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","room");p.put("code",code);p.put("uid",u.getUid());p.put("status",str(s,"status","waiting"));p.put("hostUid",str(s,"hostUid",""));
                    List<String> mem=(List<String>)s.get("members");JSONArray ma=new JSONArray();if(mem!=null)for(String id:mem)ma.put(id);p.put("members",ma);Map<String,Object> names=(Map<String,Object>)s.get("names");JSONObject no=new JSONObject();if(names!=null)for(Map.Entry<String,Object>x:names.entrySet())no.put(x.getKey(),String.valueOf(x.getValue()));p.put("names",no);
                    List<String> ready=(List<String>)s.get("ready");JSONArray ra=new JSONArray();if(ready!=null)for(String id:ready)ra.put(id);p.put("ready",ra);Map<String,Object> rb=(Map<String,Object>)s.get("roleByUid");if(rb!=null&&rb.get(u.getUid())!=null)p.put("myRole",String.valueOf(rb.get(u.getUid())));List<String> ai=(List<String>)s.get("aiRoles");JSONArray aa=new JSONArray();if(ai!=null)for(String r:ai)aa.put(r);p.put("aiRoles",aa);Timestamp st=s.getTimestamp("startAt");if(st!=null)p.put("startAt",st.toDate().getTime());p.put("resultTier",str(s,"resultTier",""));emitCase(p);}catch(Exception ex){fail("watch",ex.getLocalizedMessage());}});
                messageListener=ref.collection("messages").orderBy("createdAt",Query.Direction.ASCENDING).limit(200).addSnapshotListener((q,e)->{if(e!=null)return;try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","messages");p.put("code",code);JSONArray a=new JSONArray();if(q!=null)for(DocumentSnapshot d:q.getDocuments()){JSONObject m=new JSONObject();m.put("id",d.getId());m.put("speaker",str(d,"speaker",""));m.put("text",str(d,"text",""));m.put("type",str(d,"type","chat"));m.put("target",str(d,"target",""));m.put("senderUid",str(d,"senderUid",""));a.put(m);}p.put("messages",a);emitCase(p);}catch(Exception ignored){}});
            });
        }
        @JavascriptInterface public void markReady(String code) {
            runOnUiThread(() -> {FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("caseRooms").document(code);firestore.runTransaction(tx->{DocumentSnapshot s=tx.get(ref);List<String> ready=(List<String>)s.get("ready");if(ready==null)ready=new ArrayList<>();else ready=new ArrayList<>(ready);if(!ready.contains(u.getUid()))ready.add(u.getUid());Map<String,Object> up=new HashMap<>();up.put("ready",ready);List<String> mem=(List<String>)s.get("members");if(mem!=null&&ready.containsAll(mem)&&mem.size()==3){up.put("status","active");up.put("startAt",FieldValue.serverTimestamp());}tx.update(ref,up);return null;}).addOnFailureListener(e->fail("ready",e.getLocalizedMessage()));});
        }
        @JavascriptInterface public void sendMessage(String code,String target,String text) {
            runOnUiThread(() -> {FirebaseUser u=currentUser();if(u==null||text==null||text.trim().isEmpty())return;ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("caseRooms").document(code);ref.get().addOnSuccessListener(s->{Map<String,Object> rb=(Map<String,Object>)s.get("roleByUid");String role=rb!=null&&rb.get(u.getUid())!=null?String.valueOf(rb.get(u.getUid())):"محقق";Map<String,Object>d=new HashMap<>();d.put("speaker",role);d.put("senderUid",u.getUid());d.put("target",target==null?"":target);d.put("text",text.trim());d.put("type","chat");d.put("createdAt",FieldValue.serverTimestamp());ref.collection("messages").add(d);});});
        }
        @JavascriptInterface public void sendAiMessage(String code,String role,String text,String sourceId) {
            runOnUiThread(() -> {FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("caseRooms").document(code);ref.get().addOnSuccessListener(s->{if(!u.getUid().equals(str(s,"hostUid","")))return;com.google.firebase.firestore.DocumentReference lock=ref.collection("aiReplies").document(sourceId);firestore.runTransaction(tx->{DocumentSnapshot got=tx.get(lock);if(got.exists())return false;Map<String,Object>x=new HashMap<>();x.put("createdAt",FieldValue.serverTimestamp());tx.set(lock,x);return true;}).addOnSuccessListener(ok->{if(!Boolean.TRUE.equals(ok))return;Map<String,Object>d=new HashMap<>();d.put("speaker",role);d.put("senderUid","AI");d.put("target","");d.put("text",text);d.put("type","ai");d.put("createdAt",FieldValue.serverTimestamp());ref.collection("messages").add(d);});});});
        }
        @JavascriptInterface public void finish(String code,String loc,String reason,String action) {
            runOnUiThread(() -> {FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("caseRooms").document(code);ref.get().addOnSuccessListener(s->{if(!u.getUid().equals(str(s,"hostUid",""))) { fail("finish","صاحب الغرفة يعتمد القرار النهائي."); return; }String tier=("lake".equals(loc)&&"pressure".equals(reason)&&"safe".equals(action))?"perfect":("lake".equals(loc)?"partial":"loss");Map<String,Object>up=new HashMap<>();up.put("status","ended");up.put("resultTier",tier);up.put("resultLocation",loc);up.put("resultReason",reason);up.put("resultAction",action);up.put("endedAt",FieldValue.serverTimestamp());ref.update(up);});});
        }
        @JavascriptInterface public void stopWatch() { runOnUiThread(() -> {if(roomListener!=null){roomListener.remove();roomListener=null;}if(messageListener!=null){messageListener.remove();messageListener=null;}watchedRoom="";}); }
    }
'''
if 'public class CaseBridge {' not in java:
    pos=java.rfind('\n}')
    java=java[:pos]+CASE_BRIDGE+java[pos:]

JS=r'''

// Missing Son synchronized 3-human vertical slice.
const ROLE_DETAIL={
 'سالم':{label:'الأب',story:'أنت والد ريان. تشاجرت معه قبل خروجه بست عشرة دقيقة.',knowledge:'قلت له: «إذا مو عاجبك البيت، الباب قدامك». وقبل ثلاثة أيام وجدت تذكرة حافلة إلى مدينة أخرى ومزقتها.',goal:'اعثر على ريان، وقرر بنفسك متى تعترف بما حدث بينكما.'},
 'مها':{label:'الأم',story:'أنت والدة ريان وتحاولين إبقاء الأسرة متماسكة.',knowledge:'ريان أخبرك قبل أسبوع أنه يريد ترك تخصصه الجامعي. وكان يذهب أحيانًا إلى مكان قديم يأخذه إليه والده وهو صغير.',goal:'ساعدي في العثور عليه، وقرري متى يصبح كسر وعدك له ضروريًا.'},
 'ياسر':{label:'الصديق',story:'أنت أقرب أصدقاء ريان وآخر من وصلته رسالة منه.',knowledge:'كتب لك الساعة 8:07: «خلاص. قررت.» ثم «لا تقول لأحد وين بروح». وكان يفكر في ترك الجامعة والعمل بمدينة أخرى.',goal:'ساعد في العثور عليه، من دون أن تجعل خلافكما القديم يحرف التحقيق.'},
 'نورة':{label:'الأخت',story:'أنت أخت ريان وكنت في غرفتك أثناء الشجار.',knowledge:'سمعته يقول: «حتى المكان الوحيد اللي كنت أرتاح فيه خربته علي». ووجدت صورة قديمة له مع والده قرب بحيرة.',goal:'أوصل المعلومة للشخص المناسب في الوقت المناسب.'},
 'ماجد':{label:'العم',story:'أنت عم ريان وتعتقد أن سالم يضغط عليه أكثر مما ينبغي.',knowledge:'قبل أسبوع سألك ريان: «لو الواحد بدأ حياته من جديد، تتوقع أهله يسامحونه؟» ولم تأخذ السؤال بجدية.',goal:'ساعد في كشف الحقيقة، ولا تجعل شعورك بالذنب يتحول إلى اتهام أعمى.'},
 'أبو فهد':{label:'الجار',story:'أنت جار العائلة ورأيت ريان بعد خروجه بدقائق.',knowledge:'كان يحمل حقيبة ظهر صغيرة. وسمعته يقول لسائق: «ممشى البحيرة القديم» أو ربما «الحديقة القديمة».',goal:'اجعل الآخرين يأخذون شهادتك بجدية وحدد ما سمعته بدقة.'}
};
let mp={code:'',uid:'',hostUid:'',status:'',myRole:'',aiRoles:[],members:[],names:{},ready:[],startAt:0,lastMsgs:[],timer:null,events:new Set(),activeShown:false};
function caseNative(){return typeof NativeCase!=='undefined'}
function resetMp(){if(mp.timer)clearInterval(mp.timer);mp={code:'',uid:'',hostUid:'',status:'',myRole:'',aiRoles:[],members:[],names:{},ready:[],startAt:0,lastMsgs:[],timer:null,events:new Set(),activeShown:false}}
function openMissingSon(){resetMp();document.body.classList.add('case-immersive');[intro,envelopeScreen,profile,hq,splash,$('social')].forEach(x=>x&&(x.hidden=true));$('settingsSheet').hidden=true;$('caseRoom').hidden=false;['caseBriefing','roleCard','casePlay','caseDecision','caseEnding'].forEach(id=>$(id).hidden=true);$('caseLobby').hidden=false;$('caseLobbyActions').hidden=false;$('caseWaiting').hidden=true;$('caseTimer').textContent='--:--';$('caseTimer').classList.add('waiting');caseNative()&&NativeCase.setImmersive(true)}
window.openMissingSon=openMissingSon;
function renderLobby(){if(!mp.code)return;$('caseLobbyActions').hidden=true;$('caseWaiting').hidden=false;$('caseRoomCode').textContent=mp.code;$('caseWaitingText').textContent=mp.members.length<3?`بانتظار اللاعبين… ${mp.members.length}/3`:'اكتمل الفريق — 3/3';$('caseHumanSlots').innerHTML=mp.members.map(id=>`<div class="human-slot ${mp.ready.includes(id)?'ready':''}"><b>${mp.names[id]||'محقق'}</b><small>${mp.ready.includes(id)?'جاهز':'متصل'}</small></div>`).join('');$('continueBriefing').hidden=mp.members.length<3}
function showBriefingMp(){$('caseLobby').hidden=true;$('caseBriefing').hidden=false;$('caseTimer').textContent='15:00';$('caseTimer').classList.add('waiting')}
function setupRole(){if(!mp.myRole)return;const r=ROLE_DETAIL[mp.myRole];$('roleName').textContent=`${mp.myRole} — ${r.label}`;$('roleStory').textContent=r.story;$('roleKnowledge').textContent=r.knowledge;$('roleGoal').textContent=r.goal;$('caseBriefing').hidden=true;$('roleCard').hidden=false}
function renderCaseCast(){const all=['سالم','مها','ياسر','نورة','ماجد','أبو فهد'];$('caseCast').innerHTML=all.map(n=>`<span class="case-person ${n===mp.myRole?'me':''}">${n} — ${ROLE_DETAIL[n].label}${n===mp.myRole?' · أنت':mp.aiRoles.includes(n)?' · AI':''}</span>`).join('')}
function startActiveMp(){if(mp.activeShown)return;mp.activeShown=true;$('roleCard').hidden=true;$('caseBriefing').hidden=true;$('caseLobby').hidden=true;$('casePlay').hidden=false;renderCaseCast();$('caseFeed').innerHTML='';$('casePhase').textContent='التحقيق المفتوح';caseMsg('مدير القضية','بدأ التحقيق. أمامكم 15 دقيقة. كل لاعب يملك جزءًا مختلفًا من الحقيقة، وثلاث شخصيات في الغرفة يديرها محرك القضية.','gm');tickMp();if(mp.timer)clearInterval(mp.timer);mp.timer=setInterval(tickMp,250)}
function remainingMp(){return mp.startAt?Math.max(0,900-Math.floor((Date.now()-mp.startAt)/1000)):900}
function tickMp(){if(!mp.startAt)return;const left=remainingMp(),m=Math.floor(left/60),s=left%60;$('caseTimer').classList.remove('waiting');$('caseTimer').textContent=`${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;const elapsed=900-left;const fire=(k,sec,txt)=>{if(elapsed>=sec&&!mp.events.has(k)){mp.events.add(k);caseMsg('دليل جديد',txt,'clue')}};fire('phone',180,'تم العثور على هاتف ريان على مقعد قرب محطة الحافلات.');fire('search',300,'آخر بحث في هاتفه: «مواعيد آخر حافلة الليلة». وقبله بـ17 دقيقة: «هل ممشى البحيرة القديم مفتوح ليلًا؟»');fire('audio',420,'تسجيل قصير: «ما أبي أحد يلحقني… أبي بس أفكر.» وفي الخلفية صوت قطار.');if(left<=180){$('caseConclude').classList.remove('locked');$('caseConclude').textContent='تقديم الاستنتاج النهائي';$('casePhase').textContent='مرحلة الحسم'}else{$('caseConclude').classList.add('locked');$('caseConclude').textContent=`الاستنتاج يفتح عند 03:00`;}if(left<=0&&mp.hostUid===mp.uid)showDecision()}
function pickAiReply(role,text){const t=String(text||'');const map={
 'سالم':/تذكرة|حافلة|شجار|قلت/.test(t)?'إيه، تشاجرنا. وقلت له كلام ندمت عليه… وقبل أيام مزقت تذكرة سفر كانت معه.':'أنا آخر واحد تشاجر معه، لكن مو كل شيء قلته له كان قصدي فيه يطلع فعلًا.',
 'مها':/جامعة|تخصص|مكان|وين/.test(t)?'كان يقول إنه ما عاد يبي تخصصه. وكان فيه مكان قديم يروح له إذا ضاق صدره.':'ريان كان يخبي أشياء كثيرة عن أبوه، وبعضها قالها لي على أساس ما أتكلم.',
 'ياسر':/رسالة|قرر|وين|آخر/.test(t)?'آخر شيء كتبه لي: «خلاص. قررت. لا تقول لأحد وين بروح».':'كنا نتكلم عن ترك الجامعة والعمل في مدينة ثانية، بس ما قال لي خطته الليلة.',
 'نورة':/سمع|صورة|بحير|مكان/.test(t)?'سمعته يقول: «حتى المكان الوحيد اللي كنت أرتاح فيه خربته علي». وبعدها لقيت صورة قديمة له مع أبوي عند بحيرة.':'أنا سمعت جزء من الشجار بس… وفيه صورة لقيتها يمكن تكون مهمة.',
 'ماجد':/سأل|جديد|سامح|أهل/.test(t)?'قبل أسبوع سألني إذا الواحد بدأ حياته من جديد، أهله بيسامحونه؟ وأنا حسبتها فضفضة.':'أنا شايف إن الضغط عليه كان أكبر مما كنا نتصور، بس ما أبي أتهم أحد بلا دليل.',
 'أبو فهد':/شفت|سائق|بحير|حديقة|شنطة/.test(t)?'أغلب ظني قال للسائق «ممشى البحيرة القديم». وكان معه شنطة صغيرة بس.':'شفته يطلع بعيني. ما كان معه إلا شنطة صغيرة، وركب مع سائق.'};return map[role]||'حدد سؤالك أكثر.'}
function maybeAiRespond(msg){if(mp.uid!==mp.hostUid||!msg||msg.senderUid==='AI')return;let target=msg.target;if(!target){target=mp.aiRoles.find(r=>msg.text.includes(r))||''}if(!mp.aiRoles.includes(target))return;setTimeout(()=>{if(caseNative())NativeCase.sendAiMessage(mp.code,target,pickAiReply(target,msg.text),msg.id)},500+Math.floor(Math.random()*700))}
window.onNativeCaseEvent=e=>{if(!e)return;if(!e.ok){window.showAppDialog?showAppDialog({title:'القضية',message:e.message||'تعذر إكمال العملية.',okText:'حسنًا'}):console.warn(e.message);return}if(e.action==='room'){mp.code=e.code||mp.code;mp.uid=e.uid||mp.uid;mp.hostUid=e.hostUid||'';mp.status=e.status||'';mp.members=e.members||[];mp.names=e.names||{};mp.ready=e.ready||[];mp.myRole=e.myRole||mp.myRole;mp.aiRoles=e.aiRoles||[];mp.startAt=Number(e.startAt||0);renderLobby();if(mp.status==='briefing'&&mp.members.length===3&&!mp.activeShown&&$('caseLobby')&&!$('caseLobby').hidden){}if(mp.status==='active'){startActiveMp()}if(mp.status==='ended')showSharedEnding(e.resultTier)}else if(e.action==='messages'){const old=new Set(mp.lastMsgs.map(x=>x.id));mp.lastMsgs=e.messages||[];const feed=$('caseFeed');if(feed&&!$('casePlay').hidden){feed.innerHTML='';for(const m of mp.lastMsgs)caseMsg(m.speaker,m.text,m.type==='ai'?'':m.type==='clue'?'clue':m.senderUid===mp.uid?'player':'')}for(const m of mp.lastMsgs)if(!old.has(m.id))maybeAiRespond(m)}}};
function createMpRoom(){if(!caseNative())return;NativeCase.createRoom()}
function joinMpRoom(){if(!caseNative())return;NativeCase.joinRoom($('caseRoomCodeInput').value.trim())}
function enterMissingCase(){if(!mp.code||!caseNative())return;$('enterCase').disabled=true;$('enterCase').textContent='بانتظار جاهزية الفريق…';NativeCase.markReady(mp.code)}
function sendCaseLine(){const text=$('caseInput').value.trim();if(!text||!mp.code)return;const target=['سالم','مها','ياسر','نورة','ماجد','أبو فهد'].find(n=>text.includes(n))||'';NativeCase.sendMessage(mp.code,target,text);$('caseInput').value=''}
function showDecision(){if(mp.hostUid!==mp.uid){caseMsg('مدير القضية','صاحب الغرفة يجهز الاستنتاج النهائي الآن.','gm');return}$('casePlay').hidden=true;$('caseDecision').hidden=false}
function finishDecision(){const l=$('decisionLocation').value,r=$('decisionReason').value,a=$('decisionAction').value;if(!l||!r||!a){$('submitDecision').textContent='أكمل الخيارات الثلاثة';setTimeout(()=>$('submitDecision').textContent='اعتماد القرار',1000);return}NativeCase.finish(mp.code,l,r,a)}
function showSharedEnding(tier){if(mp.timer){clearInterval(mp.timer);mp.timer=null}$('caseLobby').hidden=true;$('caseBriefing').hidden=true;$('roleCard').hidden=true;$('casePlay').hidden=true;$('caseDecision').hidden=true;$('caseEnding').hidden=false;if(tier==='perfect'){$('endingMark').textContent='✓';$('endingTitle').textContent='تم العثور على ريان — نهاية ممتازة';$('endingText').textContent='وصلتم إلى ممشى البحيرة القديم وفهمتم سبب خروجه، واخترتم طريقة آمنة وهادئة للتعامل معه.'}else if(tier==='partial'){$('endingMark').textContent='◇';$('endingTitle').textContent='تم العثور على ريان — لكن المسافة باقية';$('endingText').textContent='وصلتم إلى المكان الصحيح، لكن تفسير السبب أو طريقة التعامل لم تكن الأفضل.'}else{$('endingMark').textContent='×';$('endingTitle').textContent='انتهت القضية دون الوصول إليه';$('endingText').textContent='اتجهتم إلى المكان الخطأ. لاحقًا عُثر على ريان سالمًا عند ممشى البحيرة القديم.'}$('endingTruth').innerHTML='<b>الحقيقة</b><br>ريان غادر بإرادته بعد ضغط وخلافات متراكمة. ترك الهاتف قرب المحطة، ثم ذهب إلى ممشى البحيرة القديم، المكان المرتبط بذكريات أهدأ مع والده.'}
function closeMissingCase(){if(mp.timer)clearInterval(mp.timer);caseNative()&&NativeCase.stopWatch();caseNative()&&NativeCase.setImmersive(false);document.body.classList.remove('case-immersive');$('caseRoom').hidden=true;resetMp();showHQ(store.get('investigator_name','المحقق'))}
if($('createCaseRoom'))$('createCaseRoom').onclick=createMpRoom;if($('joinCaseRoom'))$('joinCaseRoom').onclick=joinMpRoom;if($('continueBriefing'))$('continueBriefing').onclick=showBriefingMp;if($('revealRole'))$('revealRole').onclick=setupRole;if($('enterCase'))$('enterCase').onclick=enterMissingCase;if($('caseSend'))$('caseSend').onclick=sendCaseLine;if($('caseInput'))$('caseInput').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();sendCaseLine()}};if($('caseConclude'))$('caseConclude').onclick=showDecision;if($('submitDecision'))$('submitDecision').onclick=finishDecision;if($('caseReturn'))$('caseReturn').onclick=closeMissingCase;if($('caseExit'))$('caseExit').onclick=closeMissingCase;
'''
if '// Missing Son synchronized 3-human vertical slice.' not in js: js+=JS

html_path.write_text(html,encoding='utf-8'); js_path.write_text(js,encoding='utf-8'); css_path.write_text(css,encoding='utf-8'); java_path.write_text(java,encoding='utf-8')
print('Applied Missing Son 3-human synchronized vertical slice')
