from pathlib import Path

index=Path('app/src/main/assets/index.html')
s=index.read_text(encoding='utf-8')

# The gameplay settings replacement used to remove the app confirmation dialog
# that app.js expects during startup. Restore it before app.js loads.
if 'id="appDialog"' not in s:
    modal='''\n<div id="appDialog" class="app-dialog" hidden aria-hidden="true"><div class="app-dialog-card" role="dialog" aria-modal="true" aria-labelledby="appDialogTitle"><div class="app-dialog-mark">◈</div><h3 id="appDialogTitle">تأكيد</h3><p id="appDialogMessage"></p><div class="app-dialog-actions"><button id="appDialogCancel" class="app-dialog-btn secondary">إلغاء</button><button id="appDialogOk" class="app-dialog-btn primary-dialog">تأكيد</button></div></div></div>\n'''
    anchor='<script src="app.js"></script>'
    if anchor not in s:
        raise SystemExit('app.js script anchor missing; refusing unsafe startup fix')
    s=s.replace(anchor,modal+anchor,1)

required=['appDialog','appDialogCancel','appDialogOk','appDialogTitle','appDialogMessage']
for rid in required:
    if f'id="{rid}"' not in s:
        raise SystemExit(f'Missing required startup dialog element: {rid}')

index.write_text(s,encoding='utf-8')
print('Restored startup dialog contract after gameplay upgrade')
