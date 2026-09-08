from pathlib import Path

p=Path('app/src/main/assets/social.js')
s=p.read_text()

# Sender: keep typing alive while input changes, then clear one second after the last input.
old="$('chatInput').addEventListener('input',()=>{if(currentPeer&&NativeSocial?.setTyping)NativeSocial.setTyping(currentPeer,$('chatInput').value.trim().length>0)});"
new="""let typingStopTimer=null;let typingPeer=null;
function stopLocalTyping(){if(typingStopTimer){clearTimeout(typingStopTimer);typingStopTimer=null}const peer=typingPeer||currentPeer;if(peer&&NativeSocial?.setTyping){try{NativeSocial.setTyping(peer,false)}catch{}}typingPeer=null}
$('chatInput').addEventListener('input',()=>{if(!currentPeer||!NativeSocial?.setTyping)return;const active=$('chatInput').value.trim().length>0;typingPeer=currentPeer;NativeSocial.setTyping(currentPeer,active);if(typingStopTimer)clearTimeout(typingStopTimer);if(active)typingStopTimer=setTimeout(stopLocalTyping,1000);else stopLocalTyping()});"""
if old not in s:
    raise SystemExit('Typing input hook not found')
s=s.replace(old,new,1)

# Sending and leaving the chat must clear typing immediately.
s=s.replace("if(currentPeer&&NativeSocial?.setTyping)NativeSocial.setTyping(currentPeer,false);$('chatSend').click()", "stopLocalTyping();$('chatSend').click()",1)
s=s.replace("$('chatBack').onclick=()=>{$('chatView').hidden=true;NativeSocial.stopChatWatch?.();currentPeer=null;refresh()}", "$('chatBack').onclick=()=>{stopLocalTyping();$('chatView').hidden=true;NativeSocial.stopChatWatch?.();currentPeer=null;refresh()}",1)

# Receiver: never leave a stale typing label visible if a false event is delayed/lost.
old_event="else if(e.type==='typing'&&currentPeer===e.uid){const n=$('chatPeerName');if(n)n.textContent=e.typing?(e.name||'المحقق')+' يكتب…':(e.name||'المحقق')}"
new_event="else if(e.type==='typing'&&currentPeer===e.uid){const n=$('chatPeerName');if(n){clearTimeout(window.__peerTypingTimer);n.textContent=e.typing?(e.name||'المحقق')+' يكتب…':(e.name||'المحقق');if(e.typing){const uid=e.uid,name=e.name||'المحقق';window.__peerTypingTimer=setTimeout(()=>{if(currentPeer===uid&&n)n.textContent=name},1200)}}}"
if old_event not in s:
    raise SystemExit('Realtime typing event hook not found')
s=s.replace(old_event,new_event,1)

p.write_text(s)
print('Fixed one-second typing indicator timeout')
