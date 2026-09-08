from pathlib import Path
p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text()
perm='<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />'
if 'android.permission.POST_NOTIFICATIONS' not in s:
    s=s.replace('<manifest', '<manifest', 1)
    pos=s.find('>')+1
    s=s[:pos]+'\n    '+perm+s[pos:]
p.write_text(s)
print('Declared Android notification permission')
