// ═══════════════════════════════════════
// payment.js — Razorpay Payment Integration
// ═══════════════════════════════════════

function initiatePayment() {
  const payBtn = document.getElementById('payBtn');
  if (payBtn) {
    payBtn.disabled = true;
    payBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
  }

  // Step 1: Create Razorpay order on backend
  fetch('/payment/create-order', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    }
  })
  .then(r => r.json())
  .then(data => {
    if (!data.success) {
      showToast(data.message || 'Payment setup failed', 'error');
      if (payBtn) {
        payBtn.disabled = false;
        payBtn.innerHTML = `<i class="fas fa-lock"></i> Pay ${window.PAYMENT_AMOUNT} Securely`;
      }
      return;
    }

    // Step 2: Open Razorpay checkout
    const options = {
      key:         window.RAZORPAY_KEY,
      amount:      data.amount,
      currency:    data.currency,
      name:        'SecureShop 🛡️',
      description: 'Secure Online Purchase',
      order_id:    data.order_id,
      prefill: {
        name:    window.USER_NAME  || '',
        email:   window.USER_EMAIL || '',
        contact: window.USER_MOBILE || ''
      },
      theme: { color: '#6c63ff' },

      // Step 3: On payment success
      handler: function (response) {
        fetch('/payment/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify({
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_order_id:   response.razorpay_order_id,
            razorpay_signature:  response.razorpay_signature
          })
        })
        .then(r => r.json())
        .then(verifyData => {
          if (verifyData.success) {
            window.location.href = `/order/success/${verifyData.order_id}`;
          } else {
            showToast('Payment verification failed. Contact support.', 'error');
            if (payBtn) {
              payBtn.disabled = false;
              payBtn.innerHTML = `<i class="fas fa-lock"></i> Pay ${window.PAYMENT_AMOUNT} Securely`;
            }
          }
        });
      },

      // On modal close / failure
      modal: {
        ondismiss: function () {
          showToast('Payment cancelled.', 'warning');
          if (payBtn) {
            payBtn.disabled = false;
            payBtn.innerHTML = `<i class="fas fa-lock"></i> Pay ${window.PAYMENT_AMOUNT} Securely`;
          }
        }
      }
    };

    const rzp = new Razorpay(options);
    rzp.on('payment.failed', function (response) {
      showToast('Payment failed: ' + (response.error.description || 'Unknown error'), 'error');
      if (payBtn) {
        payBtn.disabled = false;
        payBtn.innerHTML = `<i class="fas fa-lock"></i> Pay ${window.PAYMENT_AMOUNT} Securely`;
      }
    });
    rzp.open();
  })
  .catch(() => {
    showToast('Network error. Please try again.', 'error');
    if (payBtn) {
      payBtn.disabled = false;
      payBtn.innerHTML = `<i class="fas fa-lock"></i> Pay ${window.PAYMENT_AMOUNT} Securely`;
    }
  });
}
