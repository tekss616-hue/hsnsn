const intro=document.getElementById('intro');
const introVideo=document.getElementById('introVideo');
const resumeIntro=document.getElementById('resumeIntro');
const envelopeScreen=document.getElementById('envelopeScreen');
const envelope=document.getElementById('envelope');
const profile=document.getElementById('profile');
const skip=document.getElementById('skipIntro');
const formError=document.getElementById('formError');
let finished=false,envelopeOpened=false;

function showEnvelope(){
  if(finished)return;
  finished=true;
  try{introVideo.pause()}catch(e){}
  intro.classList.add('intro-exit');
  setTimeout(()=>{
    intro.hidden=true;
    envelopeScreen.hidden=false;
    document.body.style.overflow='hidden';
  },500);
}

function tryStartIntro(){
  if(!introVideo)return;
  introVideo.currentTime=0;
  introVideo.muted=false;
  introVideo.volume=1;
  const p=introVideo.play();
  if(p?.then){
    p.then(()=>{resumeIntro.hidden=true}).catch(()=>{resumeIntro.hidden=false});
  }
}

function fitIntroVideo(){
  if(!introVideo)return;
  const vw=window.innerWidth||document.documentElement.clientWidth;
  const vh=window.innerHeight||document.documentElement.clientHeight;
  const ratio=vw/Math.max(1,vh);
  intro.dataset.screenRatio=ratio.toFixed(3);
  intro.classList.toggle('very-tall',ratio<0.50);
  intro.classList.toggle('wide-portrait',ratio>0.59&&ratio<1);
}

function paperFoley(type='place'){
  try{
    const ctx=paperFoley.ctx||(paperFoley.ctx=new (window.AudioContext||window.webkitAudioContext)());
    const len=type==='open'?.42:.22,buffer=ctx.createBuffer(1,ctx.sampleRate*len,ctx.sampleRate),data=buffer.getChannelData(0);
    for(let i=0;i<data.length;i++){const t=i/data.length;const env=Math.pow(1-t,type==='open'?1.7:3.2);data[i]=(Math.random()*2-1)*env}
    const src=ctx.createBufferSource(),filter=ctx.createBiquadFilter(),gain=ctx.createGain();src.buffer=buffer;filter.type='bandpass';filter.frequency.value=type==='open'?1800:900;filter.Q.value=.7;gain.gain.value=type==='open'?.17:.23;src.connect(filter).connect(gain).connect(ctx.destination);src.start();
  }catch(e){}
}

function openEnvelope(){
  if(envelopeOpened)return;envelopeOpened=true;paperFoley('place');envelope.classList.add('opening');
  setTimeout(()=>paperFoley('open'),260);
  setTimeout(()=>envelope.classList.add('depart'),1450);
  setTimeout(()=>{envelopeScreen.style.transition='opacity .5s ease';envelopeScreen.style.opacity='0'},1700);
  setTimeout(()=>{envelopeScreen.hidden=true;profile.hidden=false;document.body.style.overflow='auto';requestAnimationFrame(()=>document.getElementById('playerName')?.focus())},2200);
}

introVideo.addEventListener('ended',showEnvelope);
introVideo.addEventListener('error',()=>{resumeIntro.hidden=false;resumeIntro.textContent='تعذر تشغيل المقدمة — اضغط للمتابعة';resumeIntro.onclick=showEnvelope});
introVideo.addEventListener('playing',()=>{resumeIntro.hidden=true});
resumeIntro.addEventListener('click',tryStartIntro);
skip.addEventListener('click',showEnvelope);
envelope.addEventListener('click',openEnvelope);
window.addEventListener('resize',fitIntroVideo,{passive:true});
window.addEventListener('orientationchange',()=>setTimeout(fitIntroVideo,120),{passive:true});
fitIntroVideo();
tryStartIntro();

document.getElementById('createProfile').addEventListener('click',()=>{
  const name=document.getElementById('playerName').value.trim();
  const email=document.getElementById('playerEmail').value.trim();
  const password=document.getElementById('playerPassword').value;
  const confirm=document.getElementById('playerPasswordConfirm').value;
  formError.textContent='';
  if(name.length<2){formError.textContent='اكتب اسم محقق من حرفين على الأقل.';document.getElementById('playerName').focus();return}
  if(!/^\S+@\S+\.\S+$/.test(email)){formError.textContent='تأكد من كتابة البريد الإلكتروني بشكل صحيح.';document.getElementById('playerEmail').focus();return}
  if(password.length<8){formError.textContent='كلمة المرور يجب أن تكون 8 أحرف على الأقل.';document.getElementById('playerPassword').focus();return}
  if(password!==confirm){formError.textContent='كلمتا المرور غير متطابقتين.';document.getElementById('playerPasswordConfirm').focus();return}
  const btn=document.getElementById('createProfile');btn.textContent=`IDENTITY VERIFIED — ${name}`;btn.disabled=true;formError.textContent='تم اعتماد الهوية محليًا للمعاينة. ربط الحساب بالسيرفر سيكون في مرحلة الحسابات.';
});