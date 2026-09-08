from pathlib import Path

js_path=Path('app/src/main/assets/social.js')
js=js_path.read_text(encoding='utf-8')

# 1) Admin preview: the preview button already has a direct binding from the
# admin patch. The world runtime also listened globally to the same click,
# opening the world twice. The second open erased the saved return screen,
# which caused the permanent black screen on Back.
old_open="function openWorld(isPreview=false){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;isolate();g.hidden=false;document.body.style.overflow='hidden';ensure(current);if(!messages[current].length)addSystem(current,'وصلت إلى '+nameOf(current));render();maybeNaderGreets()}"
new_open="function openWorld(isPreview=false){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;if(!g.hidden){render();return}isolate();g.hidden=false;document.body.style.overflow='hidden';ensure(current);if(!messages[current].length)addSystem(current,'وصلت إلى '+nameOf(current));render();maybeNaderGreets()}"
if old_open in js:
    js=js.replace(old_open,new_open,1)
elif new_open not in js:
    raise SystemExit('world open function not found')

old_close="function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.classList.remove('world-preview-active');document.body.style.overflow='';returnState.forEach(id=>{const e=$(id);if(e)e.hidden=false});returnState=[]}"
new_close="function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.classList.remove('world-preview-active');document.body.style.overflow='';const saved=[...returnState];returnState=[];let restored=false;saved.forEach(id=>{const e=$(id);if(e){e.hidden=false;restored=true}});if(!restored){if(preview&&$('adminDashboard')){$('adminDashboard').hidden=false}else window.showHQ?.()}}"
if old_close in js:
    js=js.replace(old_close,new_close,1)
elif new_close not in js:
    raise SystemExit('world close function not found')

old_click="document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true;if(e.target.closest?.('#adminPreviewOpen'))setTimeout(()=>openWorld(true),0)},true);"
new_click="document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true},true);"
if old_click in js:
    js=js.replace(old_click,new_click,1)
elif new_click not in js:
    raise SystemExit('world click binding not found')

# 2) Conversation long press: keep the old pin/mute/delete sheet but make the
# gesture tolerant of tiny finger movement instead of cancelling on every move.
old_lp="const chats=$('chatsList');if(chats){new MutationObserver(decorateChats).observe(chats,{childList:true,subtree:true});chats.addEventListener('pointerdown',e=>{const row=e.target.closest('.chat-row');if(!row)return;clearTimeout(longTimer);longTimer=setTimeout(()=>openChatActions(row),650)});['pointerup','pointercancel','pointermove'].forEach(ev=>chats.addEventListener(ev,()=>clearTimeout(longTimer)))}"
new_lp="const chats=$('chatsList');if(chats){new MutationObserver(decorateChats).observe(chats,{childList:true,subtree:true});let holdX=0,holdY=0,holding=false;chats.addEventListener('pointerdown',e=>{const row=e.target.closest('.chat-row');if(!row)return;holding=true;holdX=e.clientX;holdY=e.clientY;clearTimeout(longTimer);longTimer=setTimeout(()=>{holding=false;openChatActions(row)},550)});chats.addEventListener('pointermove',e=>{if(!holding)return;if(Math.hypot(e.clientX-holdX,e.clientY-holdY)>14){holding=false;clearTimeout(longTimer)}});['pointerup','pointercancel'].forEach(ev=>chats.addEventListener(ev,()=>{holding=false;clearTimeout(longTimer)}));chats.addEventListener('contextmenu',e=>{const row=e.target.closest('.chat-row');if(!row)return;e.preventDefault();clearTimeout(longTimer);holding=false;openChatActions(row)})}"
if old_lp in js:
    js=js.replace(old_lp,new_lp,1)
elif new_lp not in js:
    raise SystemExit('chat long press binding not found')

# 3) AI controls must still exist after the final world/runtime patching.
# If this is missing, fail the build rather than shipping a dead admin button.
if 'NADER_AI_ADMIN_V1' not in js:
    raise SystemExit('Nader AI admin runtime was removed; refusing broken build')

js += "\n;(()=>{const ROLEPLAY_REGRESSION_RECOVERY_V1=true;})();\n"
js_path.write_text(js,encoding='utf-8')
print('Fixed preview return, conversation long-press actions, and guarded admin AI runtime')
