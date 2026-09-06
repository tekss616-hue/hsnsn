const categories = [
  { id: 'anime', title: 'تجميعات / قوالب أنمي', subtitle: 'AMV، مشاهد قتالية، إيقاع سينمائي', icon: '◉', glow: 'rgba(139,92,246,.28)' },
  { id: 'ads', title: 'إعلانات شركات', subtitle: 'منتجات، براندات، عروض احترافية', icon: '◆', glow: 'rgba(59,130,246,.24)' },
  { id: 'tiktok', title: 'تيك توك', subtitle: 'ريلز سريعة، ترندات، محتوى رأسي', icon: '♪', glow: 'rgba(236,72,153,.24)' },
  { id: 'youtube', title: 'يوتيوب', subtitle: 'مقدمات، مراجعات، فيديوهات طويلة', icon: '▶', glow: 'rgba(239,68,68,.24)' },
  { id: 'horror', title: 'رعب', subtitle: 'توتر، ظلام، انتقالات مرعبة', icon: '☾', glow: 'rgba(99,102,241,.24)' },
  { id: 'action', title: 'أكشن', subtitle: 'سرعة، ضربات، مطاردات، طاقة', icon: '⚡', glow: 'rgba(245,158,11,.24)' },
  { id: 'general', title: 'عام', subtitle: 'قوالب متنوعة لكل الاستخدامات', icon: '✦', glow: 'rgba(16,185,129,.24)' }
];

const grid = document.getElementById('categoryGrid');
const searchInput = document.getElementById('searchInput');
const panel = document.getElementById('categoryPanel');
const panelTitle = document.getElementById('panelTitle');
const closePanel = document.getElementById('closePanel');
const themeButton = document.getElementById('themeButton');

function renderCategories(items) {
  grid.innerHTML = '';

  if (!items.length) {
    grid.innerHTML = '<div class="panel" style="grid-column:1/-1"><div class="empty-state"><h3>ما لقينا هذا القسم</h3><p>جرّب كلمة ثانية.</p></div></div>';
    return;
  }

  items.forEach((category) => {
    const card = document.createElement('button');
    card.className = 'category-card';
    card.style.setProperty('--glow', category.glow);
    card.innerHTML = `
      <div class="icon">${category.icon}</div>
      <h3>${category.title}</h3>
      <p>${category.subtitle}</p>
    `;

    card.addEventListener('click', () => openCategory(category));
    grid.appendChild(card);
  });
}

function openCategory(category) {
  panelTitle.textContent = category.title;
  panel.hidden = false;
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

closePanel.addEventListener('click', () => {
  panel.hidden = true;
});

searchInput.addEventListener('input', (event) => {
  const query = event.target.value.trim().toLowerCase();
  const filtered = categories.filter((category) => {
    const haystack = `${category.title} ${category.subtitle}`.toLowerCase();
    return haystack.includes(query);
  });
  renderCategories(filtered);
});

themeButton.addEventListener('click', () => {
  document.documentElement.classList.toggle('light');
});

renderCategories(categories);
