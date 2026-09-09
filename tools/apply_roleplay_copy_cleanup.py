from pathlib import Path
import re

FILES = [Path('app/src/main/assets/index.html'),Path('app/src/main/assets/app.js'),Path('app/src/main/assets/social.js')]
replacements=[('قسم التحقيق','عيش الدور'),('غرفة التحقيق','مساحة التجربة'),('ابدأ التحقيق','ابدأ عيش الدور'),('بدء التحقيق','بدء التجربة'),('هوية المحقق','هوية اللاعب'),('اسم المحقق','اسم الشخصية'),('ملف المحقق','ملف اللاعب'),('متجر المحقق','متجر اللاعب'),('بطاقات المحقق','بطاقات الشخصية'),('بطاقة المحقق','بطاقة الشخصية'),('تصنيف المحققين','تصنيف اللاعبين'),('رتبة المحقق','مستوى اللاعب'),('محقق أول','لاعب مميز'),('المحققين','اللاعبين'),('محققين','لاعبين'),('المحقق','اللاعب'),('محقق','لاعب'),('التحقيقات','التجارب'),('تحقيقات','تجارب'),('التحقيق','عيش الدور'),('تحقيق','تجربة'),('القضايا الخاصة','التجارب الخاصة'),('القضايا المجانية','التجارب العامة'),('القضايا','التجارب'),('قضايا','تجارب'),('القضية','التجربة'),('قضية','تجربة'),('الأدلة','العناصر'),('الدليل','العنصر'),('دليل','عنصر'),('Investigation','Live Roleplay'),('investigation game','roleplay game')]
for path in FILES:
    if not path.exists():continue
    text=path.read_text(encoding='utf-8')
    for old,new in replacements:text=text.replace(old,new)
    path.write_text(text,encoding='utf-8')
idx=Path('app/src/main/assets/index.html');html=idx.read_text(encoding='utf-8');nav='<nav class="hq-nav"><button class="active" data-main="play">اللعب</button><button id="rankingTab" data-main="ranking">التصنيف</button><button id="storeTab" data-main="store">المتجر</button><button id="openProfileTab" data-main="profile">الملف</button></nav>';html,n=re.subn(r'<nav class="hq-nav">.*?</nav>',nav,html,count=1,flags=re.S)
if n!=1:raise SystemExit('hq-nav not found; refusing unsafe copy cleanup')
idx.write_text(html,encoding='utf-8')
for script in ['tools/apply_final_runtime_repairs.py','tools/apply_first_roleplay_batch_compat.py','tools/apply_friend_push_restore.py','tools/apply_friend_push_sender.py']:
    p=Path(script)
    if not p.exists():raise SystemExit(script+' missing')
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),{})
print('Applied final live-roleplay cleanup, runtime repairs and first batch')