from pathlib import Path

path = Path('app/src/main/assets/app.js')
text = path.read_text(encoding='utf-8')
bad = "maybeAiRespond(m)}}};"
good = "maybeAiRespond(m)}};"
if bad not in text:
    raise SystemExit('Expected Missing Son case-event syntax pattern not found')
text = text.replace(bad, good, 1)
path.write_text(text, encoding='utf-8')
print('Fixed Missing Son case event JavaScript syntax')
