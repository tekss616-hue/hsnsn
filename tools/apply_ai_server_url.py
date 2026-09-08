from pathlib import Path

jsf=Path('app/src/main/assets/social.js')
js=jsf.read_text(encoding='utf-8')
url='https://hsnsn-game-ai.onrender.com'
marker='/* HSNSN_AI_SERVER_BINDING */'
if marker not in js:
    js += f'''\n;(()=>{{\n{marker}\nconst AI_SERVER={url!r};\ntry{{localStorage.setItem('hsnsn_ai_server_url',AI_SERVER)}}catch{{}}\nfunction bindAiServer(){{const e=document.getElementById('adminAiServer');if(e&&!String(e.value||'').trim())e.value=AI_SERVER}}\ndocument.addEventListener('click',e=>{{if(e.target.closest?.('#adminAiOpen'))setTimeout(bindAiServer,0)}},true);\nsetTimeout(bindAiServer,100);\n}})();\n'''
jsf.write_text(js,encoding='utf-8')
print('Bound AI server:',url)
