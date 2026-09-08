from pathlib import Path

idx=Path('app/src/main/assets/index.html')
jsf=Path('app/src/main/assets/social.js')
cssf=Path('app/src/main/assets/social.css')
javaf=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
html=idx.read_text(encoding='utf-8')
js=jsf.read_text(encoding='utf-8')
css=cssf.read_text(encoding='utf-8')
java=javaf.read_text(encoding='utf-8')

# ---------- Admin AI tile + panel ----------
if 'id="adminAiOpen"' not in html:
    marker='''      <button data-admin-section="logs" class="admin-tile"><b>سجل الإدارة</b><small>سجل الإجراءات الإدارية الأخيرة</small></button>'''
    tile=marker+'''\n      <button id="adminAiOpen" class="admin-tile"><b>الذكاء الاصطناعي</b><small>حفظ مفتاح OpenAI واختبار نادر من وضع المعاينة</small></button>'''
    if marker not in html:
        raise SystemExit('admin logs tile marker missing')
    html=html.replace(marker,tile,1)

    panel=r'''
<section id="adminAiPanel" class="admin-ai-panel" hidden>
  <header class="admin-section-head"><button id="adminAiBack">‹</button><h3>الذكاء الاصطناعي</h3></header>
  <div class="admin-ai-body">
    <article class="admin-card">
      <b>اتصال السيرفر</b>
      <small>المفتاح السري لا يُحفظ داخل التطبيق. التطبيق يرسله مرة واحدة إلى السيرفر بعد التحقق من حساب الإدارة.</small>
      <label class="admin-ai-label" for="adminAiServer">عنوان خادم الذكاء الاصطناعي</label>
      <input id="adminAiServer" class="admin-input" type="url" inputmode="url" autocomplete="off" placeholder="https://your-server.example.com">
      <label class="admin-ai-label" for="adminAiKey">مفتاح OpenAI API</label>
      <input id="adminAiKey" class="admin-input" type="password" autocomplete="off" placeholder="sk-••••••••••••••••">
      <div class="admin-ai-actions"><button id="adminAiSave" class="admin-action good">حفظ المفتاح</button><button id="adminAiTest" class="admin-action">اختبار الاتصال</button></div>
      <p id="adminAiStatus" class="admin-ai-status">لم يتم فحص الاتصال بعد.</p>
    </article>
    <article class="admin-card">
      <div class="admin-ai-character-head"><div><b>مختبر الشخصيات — نادر</b><small>جلسة خاصة بحساب الإدارة لا تدخل في المطابقة أو النقاط.</small></div><span>PREVIEW</span></div>
      <div id="naderPreviewChat" class="nader-preview-chat"><div class="nader-preview-empty">ابدأ الجلسة، ونادر سيبادر بالكلام من نفسه.</div></div>
      <div class="admin-ai-actions"><button id="naderStart" class="admin-action good">بدء جلسة جديدة</button></div>
      <div class="nader-compose"><input id="naderInput" class="admin-input" maxlength="1200" placeholder="اكتب لنادر…"><button id="naderSend" class="admin-action">إرسال</button></div>
    </article>
  </div>
</section>
'''
    html=html.replace('<div id="helpReportPanel"',panel+'<div id="helpReportPanel"',1)

# ---------- Styling ----------
if '/* nader-ai-admin */' not in css:
    css += r'''
/* nader-ai-admin */
.admin-ai-panel{position:fixed;inset:0;z-index:205;background:#080a0c;color:#f5f2ed;overflow:auto}.admin-ai-panel[hidden]{display:none!important}.admin-ai-body{max-width:760px;margin:auto;padding:18px 16px 60px}.admin-ai-label{display:block;color:#aab1b6;font-size:12px;margin-top:14px}.admin-ai-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}.admin-ai-status{margin:12px 0 0;color:#959da3;font-size:13px;line-height:1.6}.admin-ai-status.good{color:#80d2a4}.admin-ai-status.bad{color:#e18b92}.admin-ai-character-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.admin-ai-character-head span{font-size:10px;letter-spacing:1px;color:#d0ad72;border:1px solid #5d492b;border-radius:999px;padding:6px 8px}.nader-preview-chat{height:330px;overflow:auto;margin-top:14px;padding:12px;border:1px solid #293035;border-radius:16px;background:#090d0f}.nader-preview-empty{display:grid;place-items:center;height:100%;text-align:center;color:#7e878d;font-size:13px;padding:20px}.nader-msg{max-width:82%;padding:10px 12px;border-radius:14px;margin:8px 0;line-height:1.55;white-space:pre-wrap;word-break:break-word}.nader-msg.ai{margin-left:auto;background:#171d21;border:1px solid #30383d}.nader-msg.me{margin-right:auto;background:#251c14;border:1px solid #5b432c}.nader-msg small{display:block;font-size:10px;color:#899197;margin-bottom:4px}.nader-compose{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;margin-top:10px}.nader-compose .admin-input{margin:0}.nader-compose button{height:46px}.admin-ai-panel button:disabled,.admin-ai-panel input:disabled{opacity:.5;pointer-events:none}
'''

# ---------- Native authenticated HTTPS bridge ----------
if 'import java.io.BufferedReader;' not in java:
    java=java.replace('import java.text.SimpleDateFormat;', '''import java.io.BufferedReader;\nimport java.io.InputStream;\nimport java.io.InputStreamReader;\nimport java.io.OutputStream;\nimport java.net.HttpURLConnection;\nimport java.net.URL;\nimport java.nio.charset.StandardCharsets;\nimport java.text.SimpleDateFormat;''',1)

if 'sendAdminAiResult(' not in java:
    anchor='    private void notifyJs(String functionName) { if (webView != null) webView.evaluateJavascript("window." + functionName + "&&window." + functionName + "()", null); }'
    helper=anchor+r'''

    private void sendAdminAiResult(String requestId, boolean ok, int status, String body, String message) {
        try {
            JSONObject p=new JSONObject();p.put("requestId",requestId==null?"":requestId);p.put("ok",ok);p.put("status",status);p.put("body",body==null?"":body);if(message!=null)p.put("message",message);
            runOnUiThread(()->webView.evaluateJavascript("window.onNativeAdminAiResult&&window.onNativeAdminAiResult("+p+")",null));
        } catch(Exception ignored){}
    }

    private boolean currentUserIsAiAdmin(){ FirebaseUser u=currentUser(); String e=u==null||u.getEmail()==null?"":u.getEmail().trim(); return "bajanznsb@gmail.com".equalsIgnoreCase(e); }

    private void adminAiHttp(String requestId,String serverUrl,String path,String method,String body,String idToken){
        new Thread(()->{
            HttpURLConnection c=null;
            try{
                String base=serverUrl==null?"":serverUrl.trim();
                if(!base.startsWith("https://"))throw new Exception("يجب أن يبدأ عنوان السيرفر بـ https://");
                while(base.endsWith("/"))base=base.substring(0,base.length()-1);
                String cleanPath=path!=null&&path.startsWith("/")?path:"/"+(path==null?"":path);
                URL u=new URL(base+cleanPath);c=(HttpURLConnection)u.openConnection();c.setConnectTimeout(12000);c.setReadTimeout(30000);c.setRequestMethod(method==null?"POST":method);c.setRequestProperty("Authorization","Bearer "+idToken);c.setRequestProperty("Accept","application/json");c.setRequestProperty("Content-Type","application/json; charset=utf-8");
                if(!"GET".equalsIgnoreCase(method)){c.setDoOutput(true);byte[]bytes=(body==null?"{}":body).getBytes(StandardCharsets.UTF_8);try(OutputStream os=c.getOutputStream()){os.write(bytes);}}
                int status=c.getResponseCode();InputStream in=status>=200&&status<400?c.getInputStream():c.getErrorStream();StringBuilder out=new StringBuilder();if(in!=null){try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;while((line=br.readLine())!=null)out.append(line);}}
                sendAdminAiResult(requestId,status>=200&&status<300,status,out.toString(),null);
            }catch(Exception e){sendAdminAiResult(requestId,false,0,"",e.getLocalizedMessage());}finally{if(c!=null)c.disconnect();}
        }).start();
    }'''
    if anchor not in java: raise SystemExit('notifyJs marker missing')
    java=java.replace(anchor,helper,1)

if '@JavascriptInterface public void adminAiRequest(' not in java:
    anchor='        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }'
    method=anchor+r'''
        @JavascriptInterface public void adminAiRequest(String requestId,String serverUrl,String path,String method,String body){
            runOnUiThread(()->{
                if(!currentUserIsAiAdmin()){sendAdminAiResult(requestId,false,403,"","غير مصرح لحساب الإدارة.");return;}
                FirebaseUser u=currentUser();if(u==null){sendAdminAiResult(requestId,false,401,"","انتهت جلسة تسجيل الدخول.");return;}
                u.getIdToken(false).addOnSuccessListener(t->adminAiHttp(requestId,serverUrl,path,method,body,t.getToken())).addOnFailureListener(e->sendAdminAiResult(requestId,false,401,"",e.getLocalizedMessage()));
            });
        }'''
    if anchor not in java: raise SystemExit('AuthBridge warmAuth marker missing')
    java=java.replace(anchor,method,1)

# ---------- JS admin UI / Nader lab ----------
if 'NADER_AI_ADMIN_V1' not in js:
    js += r'''
;(()=>{
const NADER_AI_ADMIN_V1=true,$=id=>document.getElementById(id);
let pending=new Map(),naderSession='';
const serverKey='hsnsn_ai_server_url';
function aiPanel(open){const p=$('adminAiPanel');if(p)p.hidden=!open}
function aiStatus(text,kind=''){const e=$('adminAiStatus');if(!e)return;e.textContent=text;e.className='admin-ai-status'+(kind?' '+kind:'')}
function serverUrl(){return String($('adminAiServer')?.value||'').trim().replace(/\/+$/,'')}
function saveServer(){const v=serverUrl();if(v)localStorage.setItem(serverKey,v)}
function parseBody(raw){try{return JSON.parse(raw||'{}')}catch{return {}}}
function request(path,method='POST',body={}){return new Promise((resolve,reject)=>{const base=serverUrl();if(!base){reject(new Error('ضع عنوان خادم الذكاء الاصطناعي أولاً.'));return}if(!base.startsWith('https://')){reject(new Error('عنوان الخادم يجب أن يبدأ بـ https://'));return}saveServer();const id='ai_'+Date.now()+'_'+Math.random().toString(36).slice(2);pending.set(id,{resolve,reject});try{if(typeof NativeAuth==='undefined'||typeof NativeAuth.adminAiRequest!=='function')throw new Error('نسخة التطبيق لا تدعم اتصال الذكاء الاصطناعي.');NativeAuth.adminAiRequest(id,base,path,method,JSON.stringify(body||{}))}catch(e){pending.delete(id);reject(e)}})}
window.onNativeAdminAiResult=p=>{const q=pending.get(String(p?.requestId||''));if(!q)return;pending.delete(String(p.requestId));const data=parseBody(p.body);if(p.ok)q.resolve(data);else q.reject(new Error(data.error||p.message||('HTTP '+(p.status||0))))};
function busy(btn,on,label){if(!btn)return;if(on){btn.dataset.old=btn.textContent;btn.textContent=label||'جارٍ…';btn.disabled=true}else{btn.textContent=btn.dataset.old||btn.textContent;btn.disabled=false}}
async function refreshStatus(){try{aiStatus('جارٍ فحص إعدادات السيرفر…');const d=await request('/api/admin/ai/status','GET');$('adminAiKey').placeholder=d.configured?'المفتاح محفوظ على السيرفر ••••••••':'sk-••••••••••••••••';aiStatus(d.configured?`المفتاح محفوظ ✓ · النموذج ${d.model||'gpt-5.6-luna'}`:'لم يتم حفظ مفتاح OpenAI بعد.',d.configured?'good':'')}catch(e){aiStatus('تعذر الاتصال: '+e.message,'bad')}}
$('adminAiOpen')?.addEventListener('click',()=>{const v=localStorage.getItem(serverKey)||'';if($('adminAiServer'))$('adminAiServer').value=v;aiPanel(true);if(v)refreshStatus();else aiStatus('ضع عنوان خادم الذكاء الاصطناعي أولاً.','')});
$('adminAiBack')?.addEventListener('click',()=>aiPanel(false));
$('adminAiSave')?.addEventListener('click',async()=>{const b=$('adminAiSave'),key=String($('adminAiKey')?.value||'').trim();if(!key){aiStatus('الصق مفتاح OpenAI أولاً.','bad');return}try{busy(b,true,'جارٍ الحفظ…');await request('/api/admin/ai/key','POST',{apiKey:key});$('adminAiKey').value='';$('adminAiKey').placeholder='المفتاح محفوظ على السيرفر ••••••••';aiStatus('تم حفظ المفتاح كسر مشفر على السيرفر ✓','good')}catch(e){aiStatus('فشل الحفظ: '+e.message,'bad')}finally{busy(b,false)}});
$('adminAiTest')?.addEventListener('click',async()=>{const b=$('adminAiTest');try{busy(b,true,'جارٍ الاختبار…');const d=await request('/api/admin/ai/test','POST',{});aiStatus(`الاتصال ناجح ✓ · ${d.model||'OpenAI'}`,'good')}catch(e){aiStatus('فشل اختبار الاتصال: '+e.message,'bad')}finally{busy(b,false)}});
function addMsg(who,text){const box=$('naderPreviewChat');if(!box)return;box.querySelector('.nader-preview-empty')?.remove();const d=document.createElement('div');d.className='nader-msg '+(who==='me'?'me':'ai');const s=document.createElement('small');s.textContent=who==='me'?'أنت':'نادر';const t=document.createElement('div');t.textContent=text;d.append(s,t);box.appendChild(d);box.scrollTop=box.scrollHeight}
$('naderStart')?.addEventListener('click',async()=>{const b=$('naderStart');try{busy(b,true,'نادر يدخل…');naderSession='';const box=$('naderPreviewChat');if(box)box.innerHTML='<div class="nader-preview-empty">جارٍ بدء الجلسة…</div>';const d=await request('/api/admin/nader/session','POST',{playerName:'الادمن'});naderSession=d.sessionId||'';if(box)box.innerHTML='';addMsg('ai',d.message||'هلا')}catch(e){aiStatus('تعذر بدء جلسة نادر: '+e.message,'bad')}finally{busy(b,false)}});
async function sendNader(){const input=$('naderInput'),b=$('naderSend'),text=String(input?.value||'').trim();if(!text)return;if(!naderSession){aiStatus('ابدأ جلسة نادر أولاً.','bad');return}input.value='';addMsg('me',text);try{busy(b,true,'…');input.disabled=true;const d=await request('/api/admin/nader/chat','POST',{sessionId:naderSession,text});addMsg('ai',d.message||'')}catch(e){addMsg('ai','[تعذر الرد: '+e.message+']')}finally{busy(b,false);input.disabled=false;input.focus()}}
$('naderSend')?.addEventListener('click',sendNader);$('naderInput')?.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendNader()}});
})();
'''

idx.write_text(html,encoding='utf-8')
jsf.write_text(js,encoding='utf-8')
cssf.write_text(css,encoding='utf-8')
javaf.write_text(java,encoding='utf-8')
print('Applied secure AI admin settings and Nader preview lab')
