const intro=document.getElementById('intro');
const envelopeScreen=document.getElementById('envelopeScreen');
const envelope=document.getElementById('envelope');
const profile=document.getElementById('profile');
const skip=document.getElementById('skipIntro');
const formError=document.getElementById('formError');
let finished=false;
let finishTimer=null;
let envelopeOpened=false;

function showEnvelope(){
  if(finished)return;
  finished=true;
  clearTimeout(finishTimer);
  intro.style.transition='opacity .65s ease';
  intro.style.opacity='0';
  setTimeout(()=>{
    intro.hidden=true;
    envelopeScreen.hidden=false;
    document.body.style.overflow='hidden';
  },650);
}

function openEnvelope(){
  if(envelopeOpened)return;
  envelopeOpened=true;
  envelope.classList.add('opening');
  setTimeout(()=>envelope.classList.add('depart'),1450);
  setTimeout(()=>{
    envelopeScreen.style.transition='opacity .5s ease';
    envelopeScreen.style.opacity='0';
  },1650);
  setTimeout(()=>{
    envelopeScreen.hidden=true;
    profile.hidden=false;
    document.body.style.overflow='auto';
    requestAnimationFrame(()=>document.getElementById('playerName')?.focus());
  },2150);
}

skip.addEventListener('click',showEnvelope);
envelope.addEventListener('click',openEnvelope);
finishTimer=setTimeout(showEnvelope,15000);

document.getElementById('createProfile').addEventListener('click',()=>{
  const name=document.getElementById('playerName').value.trim();
  const email=document.getElementById('playerEmail').value.trim();
  const password=document.getElementById('playerPassword').value;
  const confirm=document.getElementById('playerPasswordConfirm').value;
  formError.textContent='';

  if(name.length<2){formError.textContent='اكتب اسم محقق من حرفين على الأقل.';document.getElementById('playerName').focus();return;}
  if(!/^\S+@\S+\.\S+$/.test(email)){formError.textContent='تأكد من كتابة البريد الإلكتروني بشكل صحيح.';document.getElementById('playerEmail').focus();return;}
  if(password.length<8){formError.textContent='كلمة المرور يجب أن تكون 8 أحرف على الأقل.';document.getElementById('playerPassword').focus();return;}
  if(password!==confirm){formError.textContent='كلمتا المرور غير متطابقتين.';document.getElementById('playerPasswordConfirm').focus();return;}

  const btn=document.getElementById('createProfile');
  btn.textContent=`IDENTITY VERIFIED — ${name}`;
  btn.disabled=true;
  formError.textContent='تم اعتماد الهوية محليًا للمعاينة. ربط الحساب بالسيرفر سيكون في مرحلة الحسابات.';
});