const intro=document.getElementById('intro');
const profile=document.getElementById('profile');
const skip=document.getElementById('skipIntro');
let finished=false;
let finishTimer=null;

function showProfile(){
  if(finished)return;
  finished=true;
  clearTimeout(finishTimer);
  intro.style.transition='opacity .65s ease';
  intro.style.opacity='0';
  setTimeout(()=>{
    intro.hidden=true;
    profile.hidden=false;
    document.body.style.overflow='auto';
    requestAnimationFrame(()=>document.getElementById('playerName')?.focus());
  },650);
}

skip.addEventListener('click',showProfile);
finishTimer=setTimeout(showProfile,15000);

document.getElementById('createProfile').addEventListener('click',()=>{
  const name=document.getElementById('playerName').value.trim();
  const email=document.getElementById('playerEmail').value.trim();
  if(!name){document.getElementById('playerName').focus();return;}
  if(!/^\S+@\S+\.\S+$/.test(email)){document.getElementById('playerEmail').focus();return;}
  const btn=document.getElementById('createProfile');
  btn.textContent=`تم اعتماد هويتك، ${name}`;
  btn.disabled=true;
});