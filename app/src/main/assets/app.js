const intro=document.getElementById('intro');
const envelopeScreen=document.getElementById('envelopeScreen');
const envelope=document.getElementById('envelope');
const profile=document.getElementById('profile');
const skip=document.getElementById('skipIntro');
const formError=document.getElementById('formError');
const scenes=[...document.querySelectorAll('.scene')];
const rain=document.getElementById('rainAudio');
const impact=document.getElementById('impactAudio');
const police=document.getElementById('policeAudio');
const boom=document.getElementById('boomAudio');
let finished=false,envelopeOpened=false,currentScene=0;
const timers=[];

rain.volume=.34; impact.volume=.78; police.volume=.22; boom.volume=.72;

function later(fn,ms){const id=setTimeout(fn,ms);timers.push(id);return id}
function stopTimers(){timers.splice(0).forEach(clearTimeout)}
function safePlay(a){if(!a)return;const p=a.play();if(p?.catch)p.catch(()=>{})}
function fadeAudio(a,target,duration){if(!a)return;const start=a.volume,steps=18,delta=(target-start)/steps;let i=0;const id=setInterval(()=>{i++;a.volume=Math.max(0,Math.min(1,start+delta*i));if(i>=steps){clearInterval(id);if(target===0){a.pause();a.currentTime=0}}},duration/steps)}
function showScene(index){
  currentScene=index;
  scenes.forEach((s,i)=>{
    const active=i===index;
    s.classList.toggle('active',active);
    if(active){
      const img=s.querySelector('.scene-picture img');
      if(img){img.style.animation='none';void img.offsetWidth;img.style.animation=''}
    }
  });
}
function flashLightning(){
  if(finished||currentScene!==0)return;
  intro.classList.remove('lightning');void intro.offsetWidth;intro.classList.add('lightning');
  later(()=>intro.classList.remove('lightning'),560);
}

function startIntro(){
  showScene(0);safePlay(rain);
  later(flashLightning,1250);
  later(flashLightning,2650);
  later(()=>showScene(1),3200);
  later(()=>safePlay(impact),4450);
  later(()=>{intro.classList.add('police-on');safePlay(police);fadeAudio(police,.34,1700)},5150);
  later(()=>showScene(2),6400);
  later(()=>showScene(3),9600);
  later(()=>{showScene(4);safePlay(boom);fadeAudio(rain,.12,1200);fadeAudio(police,.1,1200)},12600);
  later(showEnvelope,15300);
}

function showEnvelope(){
  if(finished)return;
  finished=true;stopTimers();
  fadeAudio(rain,0,500);fadeAudio(police,0,500);
  intro.style.transition='opacity .55s ease';intro.style.opacity='0';
  setTimeout(()=>{intro.hidden=true;envelopeScreen.hidden=false;document.body.style.overflow='hidden';},560);
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

skip.addEventListener('click',showEnvelope);envelope.addEventListener('click',openEnvelope);startIntro();

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