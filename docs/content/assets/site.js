/* Progressive enhancement: navigation and documentation work without JavaScript. */
(() => {
  const navigation = document.querySelector('.mobile-navigation');
  const mobile = window.matchMedia('(max-width: 760px)');
  const updateNavigation = () => { navigation.open = !mobile.matches; };
  updateNavigation();
  mobile.addEventListener('change', updateNavigation);

  document.querySelectorAll('.article table').forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', 'Scrollable table');
    table.before(wrapper);
    wrapper.append(table);
  });

  // Tiny, dependency-free Python coloring; preserve the exact source text.
  document.querySelectorAll('code.language-python').forEach(code => {
    const source = code.textContent;
    const tokens = /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#[^\n]*|\b(?:from|import|async|await|def|return|class|raise|if|else|True|False|None)\b)/g;
    let position = 0;
    const fragment = document.createDocumentFragment();
    for (const match of source.matchAll(tokens)) {
      fragment.append(document.createTextNode(source.slice(position, match.index)));
      const span = document.createElement('span');
      span.className = match[0].startsWith('#') ? 'token-comment' : /^["']/.test(match[0]) ? 'token-string' : 'token-keyword';
      span.textContent = match[0];
      fragment.append(span);
      position = match.index + match[0].length;
    }
    fragment.append(document.createTextNode(source.slice(position)));
    code.replaceChildren(fragment);
  });

  const dialog = document.querySelector('#search-dialog');
  const opener = document.querySelector('.search-open');
  const input = document.querySelector('#search-input');
  const status = document.querySelector('#search-status');
  const results = document.querySelector('#search-results');
  const root = new URL(document.body.dataset.siteRoot, location.href);
  let documents;
  let loading;

  const loadIndex = () => {
    if (documents) return Promise.resolve(documents);
    if (!loading) {
      loading = fetch(document.body.dataset.searchUrl)
        .then(response => {
          if (!response.ok) throw new Error('Search unavailable');
          return response.json();
        })
        .then(index => {
          documents = index.docs.map(doc => ({ ...doc, haystack: `${doc.title} ${doc.text}`.toLowerCase() }));
          return documents;
        })
        .catch(error => { loading = null; throw error; });
    }
    return loading;
  };

  let sequence = 0;
  async function search() {
    const request = ++sequence;
    const query = input.value.trim().toLowerCase();
    results.replaceChildren();
    if (!query) { status.textContent = 'Type to find a page.'; return; }
    status.textContent = 'Searching…';
    try {
      const docs = await loadIndex();
      if (request !== sequence) return;
      const terms = query.split(/\s+/);
      const matches = docs.filter(doc => terms.every(term => doc.haystack.includes(term)))
        .map(doc => ({ doc, score: terms.reduce((score, term) => score + (doc.title.toLowerCase().includes(term) ? 5 : 1), 0) }))
        .sort((a, b) => b.score - a.score).slice(0, 12);
      status.textContent = matches.length ? `${matches.length} result${matches.length === 1 ? '' : 's'}` : 'No matches. Try a topic such as “routing” or “responses”.';
      for (const { doc } of matches) {
        const item = document.createElement('li');
        const link = document.createElement('a');
        const url = new URL(doc.location, root);
        if (url.origin !== location.origin) continue;
        link.href = url.href;
        const title = document.createElement('strong');
        title.textContent = doc.title;
        const snippet = document.createElement('small');
        const plain = doc.text.replace(/\s+/g, ' ').trim();
        const start = Math.max(0, plain.toLowerCase().indexOf(terms[0]) - 35);
        snippet.textContent = `${start ? '…' : ''}${plain.slice(start, start + 150)}${plain.length > start + 150 ? '…' : ''}`;
        link.append(title, snippet);
        item.append(link);
        results.append(item);
      }
    } catch {
      if (request === sequence) status.textContent = 'Search could not load. Please try again, or use the navigation.';
    }
  }

  function openSearch() {
    if (!dialog.open) dialog.showModal();
    input.focus();
    search();
  }
  opener.hidden = false;
  if (!/Mac|iPhone|iPad/.test(navigator.platform)) opener.querySelector('kbd').textContent = 'Ctrl K';
  opener.addEventListener('click', openSearch);
  input.addEventListener('input', search);
  input.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown' || event.key === 'Enter') {
      const first = results.querySelector('a');
      if (first) { event.preventDefault(); event.key === 'Enter' ? first.click() : first.focus(); }
    }
  });
  dialog.addEventListener('close', () => { sequence++; opener.focus(); });
  dialog.addEventListener('click', event => {
    const bounds = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
  });
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openSearch();
    }
  });
})();
