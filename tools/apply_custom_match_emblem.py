from pathlib import Path
import base64

html_path = Path('app/src/main/assets/index.html')
css_path = Path('app/src/main/assets/styles.css')
asset_b64 = Path('branding/investigation-match-emblem.webp.b64')
asset_out = Path('app/src/main/assets/media/investigation-match-emblem.webp')

html = html_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

data = ''.join(asset_b64.read_text(encoding='utf-8').split())
data += '=' * (-len(data) % 4)
asset_out.parent.mkdir(parents=True, exist_ok=True)
asset_out.write_bytes(base64.b64decode(data, validate=False))

old = 'ابدأ التحقيق ⚡'
new = 'ابدأ التحقيق <img class="match-emblem-inline" src="media/investigation-match-emblem.webp" alt="">'
if old not in html:
    raise SystemExit('Puzzle match lightning label not found; refusing unsafe replacement')
html = html.replace(old, new, 1)

marker = '/* Custom investigation match emblem */'
if marker not in css:
    css += r'''

/* Custom investigation match emblem */
.match-emblem-inline{width:28px;height:28px;object-fit:cover;object-position:center;border-radius:50%;vertical-align:middle;margin-inline-start:7px;box-shadow:0 0 14px #a5313e66;border:1px solid #ffffff18;background:#08090d}
.puzzle-match-btn{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;column-gap:2px}
.puzzle-match-btn small{flex-basis:100%}
'''

html_path.write_text(html, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
print('Applied custom investigation match emblem')
