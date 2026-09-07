const $=id=>document.getElementById(id);
const intro=$('intro'),video=$('introVideo'),resume=$('resumeIntro'),envelopeScreen=$('envelopeScreen'),envelope=$('envelope'),profile=$('profile'),hq=$('hq'),error=$('formError'),splash=$('quickSplash');
let finished=false,opened=false,authMode='create',authBusy=false,hqLoaded='';
window.VEILMARK_PERF={bootStart:performance.now()};

const store={
  get:(k,d=null)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch{return d}},
  set:(k,v)=>localStorage.setItem(k,JSON.stringify(v)),
  del:k=>localStorage.removeItem(k)
};

const cases={
  free:[['الغرفة 317','جريمة غامضة'],['آخر اتصال','اختفاء'],['الشاهد الصامت','سرقة'],['الرسالة السوداء','ابتزاز'],['الممر الأخير','اختفاء'],['الملف المحذوف','تجسس']],
  premium:[['الهوية المزدوجة','انتحال'],['خيانة منتصف الليل','خيانة'],['الدائرة المغلقة','جريمة غامضة'],['العميل السابع','تجسس'],['الصوت المفقود','اختفاء'],['النسخة الأخيرة','سرقة']]
};

function renderCases(){
  ['free','premium'].forEach(t=>{
    const el=$(t+'Cases');
    if(el.dataset.ready)return;
    el.innerHTML=cases[t].map((c,i)=>`<button class="case-card" data-case="${t}-${i}"><b>${c[0]}</b><small>${c[1]} · ${t==='free'?'6':'10'} لاعبين</small></button>`).join('');
    el.dataset.ready='1';
  });
}

function chooseHQ(){
  const r=innerHeight/Math.max(1,innerWidth);
  const opts=[[16/9,'hq-9x16.webp'],[18/9,'hq-9x18.webp'],[19.5/9,'hq-9x19_5.webp'],[20/9,'hq-9x20.webp'],[21/9,'hq-9x21.webp']];
  return opts.reduce((a,b)=>Math.abs(b[0]-r)<Math.abs(a[0]-r)?b:a)[1];
}

function loadHQ(){
  const src='hq/'+chooseHQ();
  if(hqLoaded===src)return;
  hqLoaded=src;
  const bg=$('hqBackground');
  bg.classList.remove('ready');
  const im=new Image();
  im.decoding='async';
  im.onload=()=>{
    if(hqLoaded===src){
      bg.src=src;
      requestAnimationFrame(()=>bg.classList.add('ready'));
      window.VEILMARK_PERF.hqBackgroundReady=performance.now();
    }
  };
  im.src=src;
}

function warmImage(src){
  const im=new Image();
  im.decoding='async';
  im.src=src;
}

function idle(fn,delay=0){
  const go=()=>('requestIdleCallback'in window?requestIdleCallback(fn,{timeout:900}):setTimeout(fn,0));
  delay?setTimeout(go,delay):go();
}

function nativeReady(){return typeof NativeAuth!=='undefined'}
function warmNativeAuth(){
  if(!nativeReady()||typeof NativeAuth.warmAuth!=='function')return;
  try{NativeAuth.warmAuth()}catch{}
}

function warmOnboarding(){
  idle(()=>{
    warmImage('media/envelope-closed.webp');
    warmImage('media/envelope-open.webp');
  },450);
  idle(()=>warmImage('media/investigator-paper.webp'),1100);
  idle(warmNativeAuth,1600);
}

function hideAll(){
  [intro,envelopeScreen,profile,hq,splash].forEach(x=>x&&(x.hidden=true));
}

function setCaseView(view){
  const next=view==='premium'?'premium':'free';
  hq.dataset.caseView=next;
  document.querySelectorAll('.case-tab').forEach(b=>b.classList.toggle('active',b.dataset.view===next));
  const zone=document.querySelector('.case-zone');
  if(zone)zone.scrollTop=0;
}

function showHQ(name){
  hideAll();
  hq.hidden=false;
  $('hqName').textContent=name||store.get('investigator_name','المحقق');
  renderCases();
  setCaseView(hq.dataset.caseView||'free');
  window.VEILMARK_PERF.hqVisible=performance.now();
  requestAnimationFrame(loadHQ);
}

function showEnvelope(){
  if(finished)return;
  finished=true;
  try{video.pause()}catch{}
  store.set('intro_seen',true);
  envelopeScreen.hidden=false;
  envelopeScreen.classList.remove('visible');
  requestAnimationFrame(()=>envelopeScreen.classList.add('visible'));
  intro.classList.add('intro-exit');
  window.VEILMARK_PERF.envelopeVisible=performance.now();
  warmImage('media/investigator-paper.webp');
  warmNativeAuth();
  setTimeout(()=>{
    intro.hidden=true;
    intro.classList.remove('intro-exit');
  },170);
}

function startIntro(force=false){
  finished=false;
  opened=false;
  envelope.classList.remove('opening','depart');
  envelopeScreen.classList.remove('visible');
  profile.classList.remove('ready');
  hideAll();
  intro.hidden=false;
  if(force)store.set('intro_seen',false);
  warmOnboarding();
  requestAnimationFrame(()=>{
    try{
      video.currentTime=0;
      video.muted=false;
      video.volume=1;
      const p=video.play();
      p?.catch(()=>resume.hidden=false);
    }catch{resume.hidden=false}
  });
}

function openEnvelope(){
  if(opened)return;
  opened=true;
  window.VEILMARK_PERF.envelopeTapped=performance.now();
  envelope.classList.add('opening');
  warmNativeAuth();
  setTimeout(()=>envelope.classList.add('depart'),120);
  setTimeout(()=>{
    profile.hidden=false;
    profile.classList.add('ready');
    window.VEILMARK_PERF.profileVisible=performance.now();
  },150);
  setTimeout(()=>{
    envelopeScreen.hidden=true;
    envelopeScreen.classList.remove('visible');
  },380);
}

function setAuthMode(mode){
  authMode=mode;
  error.textContent='';
  const isLogin=mode==='login';
  document.querySelector('.identity-form h1').textContent=isLogin?'تسجيل دخول المحقق':'إنشاء هوية المحقق';
  $('playerName').closest('label').hidden=isLogin;
  $('playerPasswordConfirm').closest('label').hidden=isLogin;
  $('createProfile').textContent=isLogin?'تسجيل الدخول':'اعتماد هويتي';
  $('existingAccount').textContent=isLogin?'إنشاء هوية جديدة':'لدي هوية بالفعل — تسجيل الدخول';
  warmNativeAuth();
}

function boot(){
  const name=store.get('investigator_name');
  renderCases();
  if(store.get('intro_seen',false)){
    hideAll();
    splash.hidden=false;
    requestAnimationFrame(()=>window.VEILMARK_PERF.firstFrame=performance.now());
    setTimeout(()=>{
      if(name)showHQ(name);
      else{
        splash.hidden=true;
        profile.hidden=false;
        profile.classList.add('ready');
        idle(warmNativeAuth,250);
      }
    },160);
  }else{
    startIntro();
  }
}

function friendlyAuthError(msg=''){
  const m=String(msg||'');
  if(/password|credential/i.test(m))return'بيانات الدخول غير صحيحة أو كلمة المرور غير صالحة.';
  if(/email.*already|already.*use/i.test(m))return'هذا البريد مستخدم بحساب آخر.';
  if(/network/i.test(m))return'تعذر الاتصال بالشبكة. حاول مرة أخرى.';
  if(/cancel/i.test(m))return'تم إلغاء تسجيل الدخول.';
  return m||'تعذر إكمال تسجيل الدخول. حاول مرة أخرى.';
}

function setAuthBusy(on,label=''){
  authBusy=on;
  const primary=$('createProfile'),google=$('googleAuth');
  primary.disabled=on;
  google.disabled=on;
  primary.classList.toggle('busy',on&&label!=='google');
  google.classList.toggle('busy',on&&label==='google');
  if(on)error.textContent=label==='google'?'يفتح Google الآن…':'جارٍ التحقق…';
}

window.onNativeAuthResult=r=>{
  setAuthBusy(false);
  if(!r||!r.ok){
    if(r?.action!=='restore')error.textContent=friendlyAuthError(r?.message);
    return;
  }
  if(r.action==='logout'){
    store.del('investigator_name');
    store.del('profile_cache');
    setAuthMode('login');
    hideAll();
    profile.hidden=false;
    profile.classList.add('ready');
    return;
  }
  const fallback=$('playerName').value.trim()||'المحقق';
  const name=(r.name||fallback).trim();
  store.set('investigator_name',name);
  store.set('profile_cache',{name,email:r.email||$('playerEmail').value.trim(),uid:r.uid||''});
  showHQ(name);
};

video.addEventListener('ended',showEnvelope);
video.addEventListener('error',()=>{
  resume.hidden=false;
  resume.textContent='تعذر تشغيل المقدمة — اضغط للمتابعة';
  resume.onclick=showEnvelope;
});
video.addEventListener('playing',()=>{
  resume.hidden=true;
  window.VEILMARK_PERF.introPlaying=performance.now();
});
$('skipIntro').onclick=showEnvelope;
resume.onclick=()=>video.play();
envelope.onclick=openEnvelope;

$('createProfile').onclick=()=>{
  if(authBusy)return;
  const name=$('playerName').value.trim(),email=$('playerEmail').value.trim(),p=$('playerPassword').value,c=$('playerPasswordConfirm').value;
  error.textContent='';
  if(authMode==='create'&&name.length<2)return error.textContent='اكتب اسم محقق من حرفين على الأقل.';
  if(!/^\S+@\S+\.\S+$/.test(email))return error.textContent='تأكد من البريد الإلكتروني.';
  if(p.length<8)return error.textContent='كلمة المرور يجب أن تكون 8 أحرف على الأقل.';
  if(authMode==='create'&&p!==c)return error.textContent='كلمتا المرور غير متطابقتين.';
  if(!nativeReady())return error.textContent='خدمة تسجيل الدخول غير متاحة في هذه النسخة.';
  setAuthBusy(true,'email');
  requestAnimationFrame(()=>{
    if(authMode==='create')NativeAuth.createAccount(name,email,p);
    else NativeAuth.signInEmail(email,p);
  });
};

$('googleAuth').onclick=()=>{
  if(authBusy)return;
  if(!nativeReady())return error.textContent='خدمة Google غير متاحة في هذه النسخة.';
  setAuthBusy(true,'google');
  requestAnimationFrame(()=>NativeAuth.signInGoogle());
};

$('existingAccount').onclick=()=>setAuthMode(authMode==='create'?'login':'create');
document.querySelectorAll('.case-tab').forEach(b=>b.onclick=()=>setCaseView(b.dataset.view));
$('hqSettings').onclick=()=>$('settingsSheet').hidden=false;
$('closeSettings').onclick=()=>$('settingsSheet').hidden=true;
$('replayIntro').onclick=()=>{$('settingsSheet').hidden=true;startIntro(true)};

let resizeTimer;
window.addEventListener('resize',()=>{
  if(!hq.hidden){
    clearTimeout(resizeTimer);
    resizeTimer=setTimeout(loadHQ,140);
  }
},{passive:true});

document.addEventListener('click',e=>{
  const c=e.target.closest?.('.case-card');
  if(c){
    store.set('last_case',c.dataset.case);
    c.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:100});
  }
});

boot();