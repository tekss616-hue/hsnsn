from pathlib import Path

html_path = Path('app/src/main/assets/index.html')
js_path = Path('app/src/main/assets/app.js')
java_path = Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')

html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
java = java_path.read_text(encoding='utf-8')

# Temporary hands-on test mode: 2 real humans + 4 AI roles.
html = html.replace(
    'ثلاثة لاعبين حقيقيين + ثلاث شخصيات يديرها محرك القضية. أنشئ غرفة وأرسل الرمز لإخوانك، أو ادخل رمز غرفة موجودة.',
    'وضع اختبار: لاعبان حقيقيان + أربع شخصيات يديرها محرك القضية. أنشئ غرفة من الجوال الأول وادخل الرمز من الجوال الثاني.',
    1,
)
html = html.replace('بانتظار اللاعبين… 1/3', 'بانتظار اللاعب الثاني… 1/2', 1)

repls_js = [
    ("mp.members.length<3?`بانتظار اللاعبين… ${mp.members.length}/3`:'اكتمل الفريق — 3/3'", "mp.members.length<2?`بانتظار اللاعب الثاني… ${mp.members.length}/2`:'اكتمل الاختبار — 2/2'"),
    ("$('continueBriefing').hidden=mp.members.length<3", "$('continueBriefing').hidden=mp.members.length<2"),
    ("mp.members.length===3", "mp.members.length===2"),
    ("وثلاث شخصيات في الغرفة يديرها محرك القضية.", "وأربع شخصيات في الغرفة يديرها محرك القضية."),
]
for old, new in repls_js:
    if old not in js:
        raise SystemExit(f'Missing JS marker: {old}')
    js = js.replace(old, new)

repls_java = [
    ('if(mem.size()>=3)throw new RuntimeException("الغرفة مكتملة.");', 'if(mem.size()>=2)throw new RuntimeException("الغرفة مكتملة لوضع الاختبار.");'),
    ('if(mem.size()==3){List<String> roles=roleOrder(code);Map<String,Object> rb=new HashMap<>();for(int i=0;i<3;i++)rb.put(mem.get(i),roles.get(i));up.put("roleByUid",rb);up.put("aiRoles",roles.subList(3,6));up.put("status","briefing");}',
     'if(mem.size()==2){List<String> roles=roleOrder(code);Map<String,Object> rb=new HashMap<>();for(int i=0;i<2;i++)rb.put(mem.get(i),roles.get(i));up.put("roleByUid",rb);up.put("aiRoles",roles.subList(2,6));up.put("status","briefing");}'),
    ('mem.size()==3){up.put("status","active")', 'mem.size()==2){up.put("status","active")'),
]
for old, new in repls_java:
    if old not in java:
        raise SystemExit(f'Missing Java marker: {old[:80]}')
    java = java.replace(old, new, 1)

html_path.write_text(html, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
java_path.write_text(java, encoding='utf-8')
print('Applied temporary Missing Son 2-human + 4-AI test mode')
