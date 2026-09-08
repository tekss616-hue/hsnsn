from pathlib import Path

html_path = Path('app/src/main/assets/index.html')
js_path = Path('app/src/main/assets/app.js')

html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')

# Remove only the cinematic intro screen. Keep authentication/onboarding and the rest of the app intact.
start = html.find('<main id="intro"')
if start != -1:
    end = html.find('</main>', start)
    if end == -1:
        raise SystemExit('Intro closing tag not found')
    html = html[:start] + html[end + len('</main>'):]

# Existing startup code expects the intro element. Provide a hidden inert compatibility node so
# old startup references cannot block the app while no visible/video intro is rendered.
body = '<body>'
compat = '<div id="intro" hidden aria-hidden="true"></div>'
if compat not in html:
    html = html.replace(body, body + compat, 1)

# Ensure the app never waits for the removed intro video/skip controls.
js += r'''

// Intro removed: bypass any legacy cinematic startup and enter the normal app flow immediately.
(() => {
  const introNode = document.getElementById('intro');
  if (introNode) introNode.hidden = true;
  const video = document.getElementById('introVideo');
  if (video) { try { video.pause(); video.removeAttribute('src'); video.load(); } catch (_) {} }
  try {
    localStorage.setItem('introSeen', '1');
    localStorage.setItem('intro_seen', '1');
  } catch (_) {}
})();
'''

html_path.write_text(html, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
print('Removed visible cinematic intro')
