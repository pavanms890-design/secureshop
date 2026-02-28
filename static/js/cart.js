// ═══════════════════════════════════════
// cart.js — SecureShop Cart & Favourites
// ═══════════════════════════════════════

// ── Add to Cart ───────────────────────────────────────────
function addToCart(productId, quantity = 1) {
  fetch('/cart/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({ product_id: productId, quantity: quantity })
  })
  .then(r => r.json())
  .then(data => {
    if (data.redirect) {
      // Not logged in — redirect to login
      window.location.href = data.redirect;
      return;
    }
    if (data.success) {
      showToast('Added to cart! 🛒', 'success');
      // Update badge
      const badge = document.getElementById('cartBadge');
      if (badge) badge.textContent = data.cart_count;
      // Update button state
      const btns = document.querySelectorAll(`[onclick="addToCart(${productId})"]`);
      btns.forEach(btn => {
        btn.innerHTML = '<i class="fas fa-check"></i> In Cart';
        btn.classList.add('in-cart');
        setTimeout(() => {
          btn.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
          btn.classList.remove('in-cart');
        }, 2000);
      });
    } else {
      showToast(data.message || 'Failed to add to cart', 'error');
    }
  })
  .catch(() => showToast('Network error. Try again.', 'error'));
}

// ── Toggle Favourite ──────────────────────────────────────
function toggleFavorite(productId, btnEl) {
  fetch('/favorites/toggle', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({ product_id: productId })
  })
  .then(r => r.json())
  .then(data => {
    if (data.redirect) {
      window.location.href = data.redirect;
      return;
    }
    if (data.success) {
      if (data.action === 'added') {
        showToast('Added to favourites ❤️', 'success');
        if (btnEl) btnEl.classList.add('active');
      } else {
        showToast('Removed from favourites', 'info');
        if (btnEl) btnEl.classList.remove('active');
      }
    } else {
      showToast(data.message || 'Action failed', 'error');
    }
  })
  .catch(() => showToast('Network error. Try again.', 'error'));
}
