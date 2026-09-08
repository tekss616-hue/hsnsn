from pathlib import Path

ROOT = Path('app/src/main/assets')
html_path = ROOT / 'index.html'
js_path = ROOT / 'app.js'
css_path = ROOT / 'styles.css'
java_path = Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')

html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
java = java_path.read_text(encoding='utf-8')

# Six lightweight local investigation images. They are intentionally packaged locally so a match never
# depends on a network image host. Production content can replace these files without changing gameplay.
scenes = {
    1: ('مسرح 01', '#191b20', '#6e593e', '<path d="M260 75h70v35h-20v120h-30V110h-20z" fill="#d6b461"/><circle cx="295" cy="92" r="8" fill="#17191d"/><path d="M90 250h430" stroke="#3c4048" stroke-width="6"/>'),
    2: ('مسرح 02', '#111820', '#46647a', '<circle cx="300" cy="165" r="82" fill="#d7dbe0"/><circle cx="300" cy="165" r="68" fill="#151a20"/><path d="M300 165V115M300 165l42 24" stroke="#d7dbe0" stroke-width="8" stroke-linecap="round"/><circle cx="300" cy="165" r="7" fill="#d7dbe0"/>'),
    3: ('مسرح 03', '#181719', '#6a526e', '<path d="M155 92q145-82 290 0-145 32-290 0z" fill="#9f86a8"/><path d="M300 102v132q0 36 36 36 28 0 28-29" fill="none" stroke="#9f86a8" stroke-width="12" stroke-linecap="round"/>'),
    4: ('مسرح 04', '#151a17', '#5f715a', '<rect x="150" y="112" width="300" height="145" rx="16" fill="#d4c49a"/><path d="M174 142h252M174 175h150M174 208h212" stroke="#554a35" stroke-width="10"/><circle cx="412" cy="206" r="20" fill="#8c493e"/>'),
    5: ('مسرح 05', '#11151f', '#4a5f91', '<circle cx="337" cy="142" r="78" fill="#d9dfef"/><circle cx="372" cy="115" r="78" fill="#11151f"/><circle cx="130" cy="85" r="4" fill="#fff"/><circle cx="480" cy="110" r="5" fill="#fff"/><circle cx="205" cy="60" r="3" fill="#fff"/>'),
    6: ('مسرح 06', '#171512', '#725d42', '<path d="M160 88h116q24 0 24 24v150H184q-24 0-24-24z" fill="#b69a70"/><path d="M440 88H324q-24 0-24 24v150h116q24 0 24-24z" fill="#c8ad81"/><path d="M300 110v150" stroke="#66543c" stroke-width="5"/>'),
}
for n, (label, bg, accent, art) in scenes.items():
    p = ROOT / f'puzzle-{n}.svg'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340" viewBox="0 0 600 340">
<defs><radialGradient id="g"><stop stop-color="{accent}" stop-opacity=".42"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/></radialGradient></defs>
<rect width="600" height="340" fill="{bg}"/><circle cx="300" cy="160" r="240" fill="url(#g)"/>{art}
<path d="M0 294h600" stroke="#fff" stroke-opacity=".07"/><text x="28" y="320" fill="#fff" fill-opacity=".35" font-size="16" font-family="sans-serif">INVESTIGATION / {label}</text>
</svg>'''
    p.write_text(svg, encoding='utf-8')

GAME_HTML = r'''
<main id="puzzleGame" class="puzzle-game" hidden>
  <header class="puzzle-top">
    <button id="puzzleExit" class="puzzle-back" aria-label="الخروج">‹</button>
    <div><small>تحقيق تنافسي</small><strong id="puzzleStageLabel">المرحلة 1 / 6</strong></div>
    <span id="puzzlePlayerCount" class="puzzle-count">0/7</span>
  </header>
  <section id="puzzleWaiting" class="puzzle-waiting">
    <div class="radar"><i></i><b>⌁</b></div>
    <h1>جارٍ البحث عن محققين…</h1>
    <p>سنبدأ فور اكتمال سبعة لاعبين.</p>
    <strong id="puzzleWaitingCount">1 / 7</strong>
    <button id="cancelPuzzleMatch" class="puzzle-secondary">إلغاء المطابقة</button>
  </section>
  <section id="puzzleArena" class="puzzle-arena" hidden>
    <div class="puzzle-progress"><i id="puzzleProgressBar"></i></div>
    <div class="puzzle-image-wrap"><img id="puzzleImage" src="puzzle-1.svg" alt="صورة التحقيق"><div class="scan-line"></div></div>
    <div class="puzzle-panels">
      <section class="system-panel">
        <div class="panel-title"><b>اسأل النظام</b><small>الإجابة: نعم / لا / غير ضروري</small></div>
        <div id="puzzleSystemFeed" class="system-feed"><div class="system-note">حلّل الصورة واسأل سؤالًا واحدًا في كل مرة.</div></div>
        <div class="puzzle-compose"><input id="puzzleQuestion" maxlength="180" placeholder="مثال: هل الشيء مصنوع من معدن؟"><button id="puzzleAsk">اسأل</button></div>
      </section>
      <section class="stage-chat-panel">
        <div class="panel-title"><b>محادثة المرحلة</b><small id="stagePeersText">من في نفس مرحلتك فقط</small></div>
        <div id="puzzleStageChat" class="stage-chat"></div>
        <div class="puzzle-compose"><input id="puzzleChatInput" maxlength="500" placeholder="اكتب للمحققين في مرحلتك…"><button id="puzzleChatSend">➤</button></div>
      </section>
    </div>
    <section class="solution-box"><div><b>توصلت للكلمة؟</b><small>الحل لا يُحسب من خلال سؤال النظام.</small></div><div class="solution-row"><input id="puzzleSolution" maxlength="32" placeholder="اكتب الكلمة المفتاحية"><button id="puzzleSolve">تحقق من الحل</button></div><div id="puzzleSolveMsg"></div></section>
  </section>
  <section id="puzzleFinished" class="puzzle-finished" hidden><div class="finish-mark">✓</div><h1>أنهيت التحقيق</h1><p>اكتشفت الكلمات الست. سنضيف النقاط والترتيب الشهري في الخطوة المخصصة لهما.</p><button id="puzzleReturn" class="puzzle-primary">العودة للقسم</button></section>
  <div id="puzzleToast" class="puzzle-toast"></div>
</main>
'''
if 'id="puzzleGame"' not in html:
    html = html.replace('<div id="settingsSheet"', GAME_HTML + '\n<div id="settingsSheet"', 1)

PUZZLE_CSS = r'''

/* Seven-player investigation puzzle race */
.hq.puzzle-hq .case-tabs,.hq.puzzle-hq .case-zone{display:none!important}
.puzzle-launch-zone{min-height:58vh;display:grid;place-items:center;padding:28px 18px 90px;position:relative;z-index:2}
.puzzle-launch-card{width:min(520px,100%);text-align:center;padding:34px 22px;border:1px solid #ffffff14;border-radius:28px;background:linear-gradient(160deg,#12151bcc,#080a0ecc);box-shadow:0 24px 80px #0009}
.puzzle-launch-card .launch-mark{width:88px;height:88px;margin:0 auto 20px;border-radius:50%;display:grid;place-items:center;font-size:42px;border:1px solid #9d2c3666;background:#5a171f33;box-shadow:0 0 46px #9d2c3626}
.puzzle-launch-card h1{margin:0 0 10px;font-size:29px}.puzzle-launch-card p{color:#aaa39b;line-height:1.8;margin:0 0 26px}.puzzle-match-btn,.puzzle-primary{width:100%;border:1px solid #b63d49;background:linear-gradient(180deg,#7c222d,#4e131b);color:#fff;border-radius:17px;padding:16px;font-size:17px;font-weight:900;box-shadow:0 10px 30px #7c222d33}.puzzle-match-btn small{display:block;font-size:11px;font-weight:500;color:#e0c6c8;margin-top:5px}
.puzzle-game{position:fixed;inset:0;z-index:9999;background:radial-gradient(circle at 50% 0,#1a1d25 0,#08090d 44%,#040507 100%);color:#f4f1ec;overflow:auto;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.puzzle-top{height:64px;padding:0 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ffffff0d;background:#07080bd9;position:sticky;top:0;z-index:5;backdrop-filter:blur(16px)}.puzzle-top>div{display:grid;text-align:center}.puzzle-top small{font-size:10px;color:#8c8580}.puzzle-top strong{font-size:14px}.puzzle-back{width:40px;height:40px;border-radius:12px;border:1px solid #ffffff14;background:#ffffff08;color:#fff;font-size:29px}.puzzle-count{padding:8px 11px;border-radius:11px;background:#ffffff08;border:1px solid #ffffff10;font-weight:900;font-size:13px}
.puzzle-waiting{min-height:calc(100vh - 64px);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:28px}.puzzle-waiting h1{font-size:25px;margin:24px 0 8px}.puzzle-waiting p{color:#99918b}.puzzle-waiting>strong{font-size:31px;margin:18px}.radar{width:126px;height:126px;border:1px solid #a5313e66;border-radius:50%;position:relative;display:grid;place-items:center;background:radial-gradient(circle,#8d24302b,transparent 68%)}.radar:before,.radar:after{content:'';position:absolute;inset:20px;border:1px solid #ffffff12;border-radius:50%}.radar:after{inset:43px}.radar i{position:absolute;width:50%;height:1px;background:linear-gradient(90deg,transparent,#cf5a67);transform-origin:right;right:50%;animation:radarSpin 1.7s linear infinite}.radar b{font-size:35px}@keyframes radarSpin{to{transform:rotate(360deg)}}.puzzle-secondary{border:1px solid #ffffff18;background:#ffffff07;color:#c8c2bd;padding:12px 20px;border-radius:13px}
.puzzle-arena{max-width:980px;margin:0 auto;padding:16px 16px 70px}.puzzle-progress{height:5px;background:#ffffff0b;border-radius:5px;overflow:hidden;margin-bottom:14px}.puzzle-progress i{display:block;height:100%;width:16.66%;background:#a5313e;transition:width .35s ease}.puzzle-image-wrap{position:relative;border-radius:22px;overflow:hidden;border:1px solid #ffffff12;background:#111;box-shadow:0 18px 50px #0008;aspect-ratio:600/340}.puzzle-image-wrap img{width:100%;height:100%;object-fit:cover;display:block}.scan-line{position:absolute;left:0;right:0;height:1px;background:#ffffff24;box-shadow:0 0 18px #fff3;animation:scan 5s linear infinite}@keyframes scan{0%{top:4%}100%{top:96%}}
.puzzle-panels{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}.system-panel,.stage-chat-panel,.solution-box{border:1px solid #ffffff10;background:#0c0e13dc;border-radius:19px;padding:14px}.panel-title{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:11px}.panel-title small{font-size:10px;color:#8f8882}.system-feed,.stage-chat{height:170px;overflow:auto;display:flex;flex-direction:column;gap:8px;padding:4px}.system-note{color:#8e8882;font-size:12px;padding:10px}.qa-line,.chat-line{padding:9px 11px;border-radius:12px;background:#ffffff07;font-size:13px;line-height:1.5}.qa-line b{color:#d5a0a6}.qa-line.answer{background:#5d192226;border:1px solid #8d273233}.chat-line small{display:block;color:#a57f83;margin-bottom:3px}.puzzle-compose{display:flex;gap:8px;margin-top:10px}.puzzle-compose input,.solution-row input{flex:1;min-width:0;background:#07080b;border:1px solid #ffffff12;color:#fff;border-radius:12px;padding:12px}.puzzle-compose button,.solution-row button{border:1px solid #8f2a35;background:#551721;color:#fff;border-radius:12px;padding:0 15px;font-weight:800}.solution-box{margin-top:14px}.solution-box>div:first-child{display:flex;justify-content:space-between;align-items:center;gap:10px}.solution-box small{color:#8e8882}.solution-row{display:flex;gap:8px;margin-top:12px}.solution-row button{padding:12px 18px}.puzzle-solve-ok{color:#79c89f;margin-top:10px;font-size:13px}.puzzle-solve-bad{color:#df7b82;margin-top:10px;font-size:13px}.puzzle-finished{min-height:calc(100vh - 64px);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:30px}.finish-mark{width:92px;height:92px;border-radius:50%;display:grid;place-items:center;border:1px solid #72b99566;background:#72b99518;font-size:48px;color:#8bd0ad}.puzzle-finished h1{font-size:29px;margin:22px 0 7px}.puzzle-finished p{color:#99918b;max-width:420px;line-height:1.8}.puzzle-finished .puzzle-primary{max-width:360px;margin-top:18px}.puzzle-toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,20px);opacity:0;pointer-events:none;background:#17191f;border:1px solid #ffffff14;border-radius:13px;padding:10px 15px;transition:.2s;z-index:20}.puzzle-toast.show{opacity:1;transform:translate(-50%,0)}
@media(max-width:720px){.puzzle-panels{grid-template-columns:1fr}.system-feed,.stage-chat{height:150px}.puzzle-arena{padding:12px 12px 55px}.puzzle-image-wrap{border-radius:17px}.solution-box>div:first-child{align-items:flex-start;flex-direction:column}.solution-row{flex-direction:column}.solution-row button{min-height:45px}}
'''
if '/* Seven-player investigation puzzle race */' not in css:
    css += PUZZLE_CSS

if 'new PuzzleBridge(), "NativePuzzle"' not in java:
    java = java.replace('webView.addJavascriptInterface(new SocialBridge(), "NativeSocial");', 'webView.addJavascriptInterface(new SocialBridge(), "NativeSocial");\n        webView.addJavascriptInterface(new PuzzleBridge(), "NativePuzzle");', 1)

BRIDGE = r'''

    public class PuzzleBridge {
        private com.google.firebase.firestore.ListenerRegistration puzzleRoomListener;
        private com.google.firebase.firestore.ListenerRegistration puzzleChatListener;
        private String puzzleMatchId = "";
        private int puzzleStage = 1;

        private void emitPuzzle(JSONObject payload) {
            runOnUiThread(() -> webView.evaluateJavascript("window.onNativePuzzleEvent&&window.onNativePuzzleEvent(" + payload + ")", null));
        }
        private void puzzleFail(String action, String message) {
            try { JSONObject p=new JSONObject();p.put("ok",false);p.put("action",action);p.put("message",message==null?"تعذر إكمال العملية.":message);emitPuzzle(p); } catch(Exception ignored){}
        }
        private String clean(String s){return s==null?"":s.trim().toLowerCase(Locale.ROOT).replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ة","ه");}
        private String solutionFor(int stage){String[] a={"مفتاح","ساعة","مظلة","تذكرة","قمر","كتاب"};return stage>=1&&stage<=6?a[stage-1]:"";}
        private String answerQuestion(int stage,String raw){
            String q=clean(raw); if(q.isEmpty())return "غير ضروري";
            String[][] yes={
                {"مفتاح","معدن","معدني","باب","قفل","يفتح","صغير"},
                {"ساعه","وقت","زمن","عقارب","دائري","جدار"},
                {"مظله","مطر","يحمي","مقبض","تفتح","فوق الراس"},
                {"تذكره","سفر","ركوب","محطه","ورق","قطار","حافله"},
                {"قمر","ليل","سماء","فضاء","مضيء","هلال"},
                {"كتاب","قراءه","صفحات","ورق","مجلد","مكتبه"}
            };
            for(String x:yes[stage-1])if(q.contains(clean(x)))return "نعم";
            for(int i=1;i<=6;i++)if(i!=stage&&q.contains(clean(solutionFor(i))))return "لا";
            String[] negatives={"سياره","هاتف","جوال","كرسي","شجره","حيوان","انسان","طعام","سلاح","كمبيوتر","بحر"};
            for(String x:negatives)if(q.contains(clean(x)))return "لا";
            return "غير ضروري";
        }
        private String playerName(FirebaseUser u){String n=u.getDisplayName();return n==null||n.trim().isEmpty()?"محقق":n.trim();}
        private void stopPuzzleWatchInternal(){if(puzzleRoomListener!=null){puzzleRoomListener.remove();puzzleRoomListener=null;}if(puzzleChatListener!=null){puzzleChatListener.remove();puzzleChatListener=null;}}

        @JavascriptInterface public void matchmake(){
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null){puzzleFail("match","سجّل الدخول أولًا.");return;}ensureFirestore();
                final com.google.firebase.firestore.DocumentReference queue=firestore.collection("puzzleSystem").document("queue7");
                final String candidate=java.util.UUID.randomUUID().toString();
                firestore.runTransaction(tx->{
                    DocumentSnapshot q=tx.get(queue);String mid=q.exists()?str(q,"waitingMatchId",""):"";com.google.firebase.firestore.DocumentReference match;
                    if(mid.isEmpty()){mid=candidate;match=firestore.collection("puzzleMatches").document(mid);Map<String,Object>d=new HashMap<>();d.put("status","waiting");d.put("members",new ArrayList<>(Arrays.asList(u.getUid())));Map<String,Object>names=new HashMap<>();names.put(u.getUid(),playerName(u));d.put("names",names);Map<String,Object>st=new HashMap<>();st.put(u.getUid(),1);d.put("stageByUid",st);d.put("createdAt",FieldValue.serverTimestamp());tx.set(match,d);Map<String,Object>qd=new HashMap<>();qd.put("waitingMatchId",mid);qd.put("updatedAt",FieldValue.serverTimestamp());tx.set(queue,qd);return mid;}
                    match=firestore.collection("puzzleMatches").document(mid);DocumentSnapshot m=tx.get(match);if(!m.exists()||!"waiting".equals(str(m,"status","waiting"))){mid=candidate;match=firestore.collection("puzzleMatches").document(mid);Map<String,Object>d=new HashMap<>();d.put("status","waiting");d.put("members",new ArrayList<>(Arrays.asList(u.getUid())));Map<String,Object>names=new HashMap<>();names.put(u.getUid(),playerName(u));d.put("names",names);Map<String,Object>st=new HashMap<>();st.put(u.getUid(),1);d.put("stageByUid",st);d.put("createdAt",FieldValue.serverTimestamp());tx.set(match,d);Map<String,Object>qd=new HashMap<>();qd.put("waitingMatchId",mid);qd.put("updatedAt",FieldValue.serverTimestamp());tx.set(queue,qd);return mid;}
                    List<String> members=(List<String>)m.get("members");members=members==null?new ArrayList<>():new ArrayList<>(members);if(!members.contains(u.getUid()))members.add(u.getUid());Map<String,Object>names=(Map<String,Object>)m.get("names");names=names==null?new HashMap<>():new HashMap<>(names);names.put(u.getUid(),playerName(u));Map<String,Object>stages=(Map<String,Object>)m.get("stageByUid");stages=stages==null?new HashMap<>():new HashMap<>(stages);stages.put(u.getUid(),1);Map<String,Object>up=new HashMap<>();up.put("members",members);up.put("names",names);up.put("stageByUid",stages);
                    if(members.size()>=7){up.put("status","active");up.put("startedAt",FieldValue.serverTimestamp());tx.update(queue,"waitingMatchId","");}tx.update(match,up);return mid;
                }).addOnSuccessListener(mid->watchPuzzle(String.valueOf(mid))).addOnFailureListener(e->puzzleFail("match",e.getLocalizedMessage()));
            });
        }
        @JavascriptInterface public void watchPuzzle(String matchId){
            runOnUiThread(() -> {FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();stopPuzzleWatchInternal();puzzleMatchId=matchId;com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);
                puzzleRoomListener=ref.addSnapshotListener((s,e)->{if(e!=null){puzzleFail("watch",e.getLocalizedMessage());return;}if(s==null||!s.exists())return;try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","state");p.put("matchId",matchId);p.put("status",str(s,"status","waiting"));List<String>mem=(List<String>)s.get("members");JSONArray ma=new JSONArray();if(mem!=null)for(String id:mem)ma.put(id);p.put("members",ma);Map<String,Object>names=(Map<String,Object>)s.get("names");JSONObject no=new JSONObject();if(names!=null)for(Map.Entry<String,Object>x:names.entrySet())no.put(x.getKey(),String.valueOf(x.getValue()));p.put("names",no);Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");int stage=1;if(st!=null&&st.get(u.getUid()) instanceof Number)stage=((Number)st.get(u.getUid())).intValue();p.put("stage",stage);JSONObject so=new JSONObject();if(st!=null)for(Map.Entry<String,Object>x:st.entrySet())so.put(x.getKey(),x.getValue());p.put("stages",so);emitPuzzle(p);if(stage!=puzzleStage){puzzleStage=stage;watchPuzzleChat(matchId,stage);}else if(puzzleChatListener==null)watchPuzzleChat(matchId,stage);}catch(Exception ex){puzzleFail("watch",ex.getLocalizedMessage());}});
            });
        }
        private void watchPuzzleChat(String matchId,int stage){if(puzzleChatListener!=null){puzzleChatListener.remove();puzzleChatListener=null;}if(stage>6)return;com.google.firebase.firestore.CollectionReference c=firestore.collection("puzzleMatches").document(matchId).collection("stage"+stage+"Chat");puzzleChatListener=c.limit(100).addSnapshotListener((q,e)->{if(e!=null)return;try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","chat");p.put("stage",stage);JSONArray a=new JSONArray();if(q!=null)for(DocumentSnapshot d:q.getDocuments()){JSONObject m=new JSONObject();m.put("id",d.getId());m.put("uid",str(d,"uid",""));m.put("name",str(d,"name","محقق"));m.put("text",str(d,"text",""));Timestamp t=d.getTimestamp("createdAt");if(t!=null)m.put("time",t.toDate().getTime());a.put(m);}p.put("messages",a);emitPuzzle(p);}catch(Exception ignored){}});}
        @JavascriptInterface public void ask(String matchId,int stage,String question){runOnUiThread(()->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","answer");p.put("stage",stage);p.put("question",question==null?"":question.trim());p.put("answer",answerQuestion(stage,question));emitPuzzle(p);}catch(Exception ignored){}});}
        @JavascriptInterface public void sendStageChat(String matchId,int stage,String text){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null||text==null||text.trim().isEmpty()||stage<1||stage>6)return;ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);ref.get().addOnSuccessListener(s->{Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");if(st==null||!(st.get(u.getUid()) instanceof Number)||((Number)st.get(u.getUid())).intValue()!=stage)return;Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",playerName(u));d.put("text",text.trim());d.put("createdAt",FieldValue.serverTimestamp());ref.collection("stage"+stage+"Chat").add(d);});});}
        @JavascriptInterface public void submitSolution(String matchId,int stage,String raw){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String guess=clean(raw),answer=clean(solutionFor(stage));if(!guess.equals(answer)){try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","solution");p.put("correct",false);p.put("stage",stage);emitPuzzle(p);}catch(Exception ignored){}return;}com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);firestore.runTransaction(tx->{DocumentSnapshot s=tx.get(ref);Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");st=st==null?new HashMap<>():new HashMap<>(st);Object cur=st.get(u.getUid());int now=cur instanceof Number?((Number)cur).intValue():1;if(now!=stage)return now;st.put(u.getUid(),stage+1);Map<String,Object>up=new HashMap<>();up.put("stageByUid",st);if(stage==6){Map<String,Object>finished=(Map<String,Object>)s.get("finishedAtByUid");finished=finished==null?new HashMap<>():new HashMap<>(finished);finished.put(u.getUid(),new Date().getTime());up.put("finishedAtByUid",finished);}tx.update(ref,up);return stage+1;}).addOnSuccessListener(next->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","solution");p.put("correct",true);p.put("stage",stage);p.put("nextStage",next);emitPuzzle(p);}catch(Exception ignored){}}).addOnFailureListener(e->puzzleFail("solution",e.getLocalizedMessage()));});}
        @JavascriptInterface public void cancelMatch(String matchId){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null||matchId==null||matchId.isEmpty()){stopPuzzleWatchInternal();return;}ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);firestore.runTransaction(tx->{DocumentSnapshot s=tx.get(ref);if(!s.exists()||!"waiting".equals(str(s,"status","waiting")))return null;List<String>mem=(List<String>)s.get("members");mem=mem==null?new ArrayList<>():new ArrayList<>(mem);mem.remove(u.getUid());Map<String,Object>names=(Map<String,Object>)s.get("names");names=names==null?new HashMap<>():new HashMap<>(names);names.remove(u.getUid());Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");st=st==null?new HashMap<>():new HashMap<>(st);st.remove(u.getUid());Map<String,Object>up=new HashMap<>();up.put("members",mem);up.put("names",names);up.put("stageByUid",st);tx.update(ref,up);return null;}).addOnCompleteListener(t->stopPuzzleWatchInternal());});}
        @JavascriptInterface public void stop(){runOnUiThread(this::stopPuzzleWatchInternal);}
    }
'''
if 'public class PuzzleBridge {' not in java:
    pos = java.rfind('\n}')
    java = java[:pos] + BRIDGE + java[pos:]

PUZZLE_JS = r'''

// Seven-player picture investigation race. Each stage owns its own chat; players only watch their current stage.
(function(){
  const q=s=>document.querySelector(s), game=q('#puzzleGame'), waiting=q('#puzzleWaiting'), arena=q('#puzzleArena'), finished=q('#puzzleFinished');
  if(!game)return;
  let state={matchId:'',stage:1,status:'idle',members:[],names:{},stages:{}};
  function toast(t){const e=q('#puzzleToast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1800)}
  function setupHQ(){
    const H=q('#hq'); if(!H||H.classList.contains('puzzle-hq'))return; H.classList.add('puzzle-hq');
    const nav=H.querySelector('.hq-nav button');if(nav)nav.textContent='اللعب';
    const tabs=H.querySelector('.case-tabs'),zone=H.querySelector('.case-zone');if(tabs)tabs.hidden=true;if(zone)zone.hidden=true;
    const launch=document.createElement('section');launch.className='puzzle-launch-zone';launch.innerHTML='<div class="puzzle-launch-card"><div class="launch-mark">⌁</div><h1>غرفة التحقيق</h1><p>سبعة محققين. ست صور. في كل صورة كلمة مفتاحية واحدة. اسأل النظام، ناقش من بقي في مرحلتك، وتقدم قبل الآخرين.</p><button id="startPuzzleMatch" class="puzzle-match-btn">⚡ ابدأ التحقيق<small>مطابقة تلقائية مع 6 محققين آخرين</small></button></div>';
    const navEl=H.querySelector('.hq-nav');H.insertBefore(launch,navEl||null);q('#startPuzzleMatch').onclick=startMatch;
  }
  setupHQ();document.addEventListener('DOMContentLoaded',setupHQ);
  function openGame(){game.hidden=false;waiting.hidden=false;arena.hidden=true;finished.hidden=true;document.body.style.overflow='hidden'}
  function closeGame(cancel){if(cancel&&state.matchId&&window.NativePuzzle)NativePuzzle.cancelMatch(state.matchId);else if(window.NativePuzzle)NativePuzzle.stop();game.hidden=true;document.body.style.overflow='';state={matchId:'',stage:1,status:'idle',members:[],names:{},stages:{}}}
  function startMatch(){if(!window.NativePuzzle){toast('المطابقة تحتاج نسخة Android.');return}openGame();q('#puzzleWaitingCount').textContent='…';NativePuzzle.matchmake()}
  q('#cancelPuzzleMatch').onclick=()=>closeGame(true);q('#puzzleExit').onclick=()=>{if(state.status==='waiting')closeGame(true);else closeGame(false)};q('#puzzleReturn').onclick=()=>closeGame(false);
  function renderState(){
    const count=state.members.length;q('#puzzlePlayerCount').textContent=count+'/7';q('#puzzleWaitingCount').textContent=count+' / 7';
    if(state.status==='waiting'){waiting.hidden=false;arena.hidden=true;finished.hidden=true;return}
    waiting.hidden=true;
    if(state.stage>6){arena.hidden=true;finished.hidden=false;q('#puzzleStageLabel').textContent='اكتمل 6 / 6';return}
    arena.hidden=false;finished.hidden=true;q('#puzzleStageLabel').textContent='المرحلة '+state.stage+' / 6';q('#puzzleImage').src='puzzle-'+state.stage+'.svg';q('#puzzleProgressBar').style.width=((state.stage/6)*100)+'%';
    const peers=state.members.filter(id=>Number(state.stages[id]||1)===state.stage).length;q('#stagePeersText').textContent=peers===1?'أنت وحدك في هذه المرحلة':peers+' محققين في هذه المرحلة';
  }
  function clearForStage(){q('#puzzleSystemFeed').innerHTML='<div class="system-note">بدأت مرحلة جديدة. أسئلة هذه المرحلة خاصة بك.</div>';q('#puzzleStageChat').innerHTML='';q('#puzzleQuestion').value='';q('#puzzleChatInput').value='';q('#puzzleSolution').value='';q('#puzzleSolveMsg').textContent=''}
  window.onNativePuzzleEvent=function(ev){
    if(!ev||!ev.ok){if(ev&&ev.message)toast(ev.message);return}
    if(ev.action==='state'){const old=state.stage;state.matchId=ev.matchId;state.status=ev.status;state.members=ev.members||[];state.names=ev.names||{};state.stages=ev.stages||{};state.stage=Number(ev.stage||1);if(old!==state.stage)clearForStage();renderState();return}
    if(ev.action==='answer'){const feed=q('#puzzleSystemFeed');const a=document.createElement('div');a.className='qa-line';a.textContent='أنت: '+ev.question;feed.appendChild(a);const b=document.createElement('div');b.className='qa-line answer';b.innerHTML='<b>النظام:</b> '+ev.answer;feed.appendChild(b);feed.scrollTop=feed.scrollHeight;return}
    if(ev.action==='chat'&&Number(ev.stage)===state.stage){const box=q('#puzzleStageChat');const arr=[...(ev.messages||[])].sort((a,b)=>(a.time||0)-(b.time||0));box.innerHTML=arr.length?'':'<div class="system-note">لا توجد رسائل بعد.</div>';arr.forEach(m=>{const d=document.createElement('div');d.className='chat-line';d.innerHTML='<small></small><span></span>';d.querySelector('small').textContent=m.name||'محقق';d.querySelector('span').textContent=m.text||'';box.appendChild(d)});box.scrollTop=box.scrollHeight;return}
    if(ev.action==='solution'){const m=q('#puzzleSolveMsg');if(ev.correct){m.className='puzzle-solve-ok';m.textContent=Number(ev.stage)===6?'✓ الكلمة السادسة صحيحة. أنهيت التحقيق!':'✓ صحيح — انتقلت للمرحلة التالية.';q('#puzzleSolution').value=''}else{m.className='puzzle-solve-bad';m.textContent='ليست الكلمة المطلوبة. أكمل التحقيق.'}return}
  };
  q('#puzzleAsk').onclick=()=>{const v=q('#puzzleQuestion').value.trim();if(!v)return;if(!state.matchId||state.stage>6)return;NativePuzzle.ask(state.matchId,state.stage,v);q('#puzzleQuestion').value=''};
  q('#puzzleQuestion').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();q('#puzzleAsk').click()}});
  q('#puzzleChatSend').onclick=()=>{const v=q('#puzzleChatInput').value.trim();if(!v||!state.matchId)return;NativePuzzle.sendStageChat(state.matchId,state.stage,v);q('#puzzleChatInput').value=''};
  q('#puzzleChatInput').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();q('#puzzleChatSend').click()}});
  q('#puzzleSolve').onclick=()=>{const v=q('#puzzleSolution').value.trim();if(!v||!state.matchId)return;NativePuzzle.submitSolution(state.matchId,state.stage,v)};
  q('#puzzleSolution').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();q('#puzzleSolve').click()}});
})();
'''
if '// Seven-player picture investigation race.' not in js:
    js += PUZZLE_JS

html_path.write_text(html, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
java_path.write_text(java, encoding='utf-8')
print('Applied seven-player puzzle race')
