// ═══════════════════════════════════════
// search.js — SecureShop Live Search
// Shows suggestions + product cards in dropdown as user types
// ═══════════════════════════════════════

(function () {
  const input      = document.getElementById('globalSearch');
  const dropdown   = document.getElementById('searchDropdown');
  const sugList    = document.getElementById('suggestionsList');
  const resultList = document.getElementById('searchResults');
  const searchBtn  = document.querySelector('.search-btn');

  if (!input || !dropdown) return;

  let debounceTimer = null;

  // ── Open/close dropdown ───────────────────────────────────
  function showDropdown() { dropdown.style.display = 'block'; }
  function hideDropdown() { dropdown.style.display = 'none';  }

  // ── Render suggestions ────────────────────────────────────
  function renderSuggestions(suggestions) {
    sugList.innerHTML = '';
    if (!suggestions.length) return;

    const header = document.createElement('div');
    header.className = 'search-section-title';
    header.textContent = '🔍 Suggestions';
    sugList.appendChild(header);

    suggestions.forEach(s => {
      const item = document.createElement('div');
      item.className = 'suggestion-item';
      item.innerHTML = `<i class="fas fa-search"></i> <span>${s}</span>`;
      item.addEventListener('click', () => {
        input.value = s;
        hideDropdown();
        window.location.href = `/search-results?q=${encodeURIComponent(s)}`;
      });
      sugList.appendChild(item);
    });
  }

  // ── Render product cards ───────────────────────────────────
  function renderProducts(products) {
    resultList.innerHTML = '';
    if (!products.length) {
      resultList.innerHTML = '<p class="no-results">No products found. Try a different keyword.</p>';
      return;
    }

    const header = document.createElement('div');
    header.className = 'search-section-title';
    header.textContent = '🛍️ Products';
    resultList.appendChild(header);

    products.forEach(p => {
      const card = document.createElement('div');
      card.className = 'search-result-card';
      card.innerHTML = `
        <img src="${p.image_url}" alt="${p.name}"
             onerror="this.src='https://via.placeholder.com/60x60?text=IMG'">
        <div class="search-result-info">
          <span class="search-result-cat">${p.category}</span>
          <p class="search-result-name">${p.name}</p>
          <span class="search-result-price">₹${Math.round(p.price)}</span>
        </div>
        <div class="search-result-stars">${renderStars(p.rating)}</div>
      `;
      card.addEventListener('click', () => {
        window.location.href = `/product/${p.id}`;
      });
      resultList.appendChild(card);
    });

    // "View all" link
    const viewAll = document.createElement('a');
    viewAll.className = 'search-view-all';
    viewAll.href = `/search-results?q=${encodeURIComponent(input.value)}`;
    viewAll.textContent = `View all results →`;
    resultList.appendChild(viewAll);
  }

  function renderStars(rating) {
    let stars = '';
    for (let i = 0; i < 5; i++) {
      stars += `<i class="fa${i < Math.floor(rating) ? 's' : 'r'} fa-star"
        style="color:${i < Math.floor(rating) ? '#f39c12' : '#ddd'};font-size:0.7rem;"></i>`;
    }
    return stars;
  }

  // ── Fetch from API ────────────────────────────────────────
  async function doSearch(query) {
    if (query.length < 2) { hideDropdown(); return; }
    try {
      const res  = await fetch(`/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      renderSuggestions(data.suggestions || []);
      renderProducts(data.products || []);
      showDropdown();
    } catch (e) {
      console.error('Search error:', e);
    }
  }

  // ── Input event with debounce ─────────────────────────────
  input.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const q = input.value.trim();
    if (!q) { hideDropdown(); return; }
    debounceTimer = setTimeout(() => doSearch(q), 280);
  });

  // ── Enter key / Search button ─────────────────────────────
  function goToSearch() {
    const q = input.value.trim();
    if (q) window.location.href = `/search-results?q=${encodeURIComponent(q)}`;
  }
  input.addEventListener('keydown', e => { if (e.key === 'Enter') goToSearch(); });
  if (searchBtn) searchBtn.addEventListener('click', goToSearch);

  // ── Close on outside click ────────────────────────────────
  document.addEventListener('click', e => {
    if (!input.closest('.search-wrapper').contains(e.target)) hideDropdown();
  });

  // ── Focus: reopen if already has results ─────────────────
  input.addEventListener('focus', () => {
    if (input.value.trim().length >= 2) doSearch(input.value.trim());
  });
})();
