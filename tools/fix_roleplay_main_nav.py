from pathlib import Path
import re

idx = Path('app/src/main/assets/index.html')
s = idx.read_text(encoding='utf-8')

# Keep the existing four-function navigation intact even when the visible copy
# of the base HQ is changed from the old investigation wording.
nav = '<nav class="hq-nav"><button class="active" data-main="play">اللعب</button><button id="rankingTab" data-main="ranking">التصنيف</button><button id="storeTab" data-main="store">المتجر</button><button id="openProfileTab">الملف</button></nav>'
s, count = re.subn(r'<nav class="hq-nav">.*?</nav>', nav, s, count=1, flags=re.S)
if count != 1:
    raise SystemExit('hq-nav not found')

# Update only visible wording to the live-roleplay direction; IDs/classes stay
# unchanged so existing store/ranking behavior continues to work.
s = s.replace('<h1>تصنيف المحققين</h1>', '<h1>تصنيف اللاعبين</h1>')
s = s.replace('ترتيبك التنافسي سيُحتسب من نتائج التحقيقات.', 'ترتيبك يتطور من مشاركاتك ونتائجك داخل تجارب عيش الدور.')
s = s.replace('<h1>متجر المحقق</h1>', '<h1>متجر اللاعب</h1>')
s = s.replace('اختر تصميم بطاقة المحقق وخلفيتها وحركاتها.', 'اختر تصميم بطاقة شخصيتك وخلفيتها وحركاتها.')
s = s.replace('بطاقات المحقق<small>', 'بطاقات الشخصية<small>')

idx.write_text(s, encoding='utf-8')
print('Restored four-item main nav with working ranking/store IDs')
