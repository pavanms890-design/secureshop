# 🛡️ SecureShop — Secure Online Shopping Portal

A full-featured e-commerce web application built with Flask + MySQL + Razorpay.

---

## 📋 WHAT YOU NEED BEFORE STARTING

1. **Python 3.8+** — [python.org/downloads](https://python.org/downloads)
2. **MySQL** — [mysql.com/downloads](https://mysql.com/downloads) OR use XAMPP/WAMP
3. **A Razorpay Test Account** — [razorpay.com](https://dashboard.razorpay.com/signin) (Free)

---

## 🗂️ FOLDER STRUCTURE

```
SecureShop/
├── app.py                 ← Main Flask application (all routes)
├── config.py              ← Configuration (edit your DB password here)
├── requirements.txt       ← Python packages
├── schema.sql             ← Database + 1000 products
├── README.md              ← This file
│
├── static/
│   ├── css/
│   │   ├── style.css      ← Global styles, navbar, footer, cards
│   │   ├── home.css       ← Home page hero slider, categories
│   │   ├── auth.css       ← Login & register pages
│   │   ├── products.css   ← Products page + filters
│   │   ├── cart.css       ← Cart page
│   │   └── profile.css    ← User profile page
│   ├── js/
│   │   ├── main.js        ← Global JS: toasts, mobile menu
│   │   ├── search.js      ← Live search dropdown
│   │   ├── cart.js        ← Add to cart, favourites
│   │   └── payment.js     ← Razorpay checkout
│   └── uploads/           ← Profile images (auto-created)
│
└── templates/
    ├── base.html           ← Master layout
    ├── home.html           ← Home page
    ├── login.html          ← Login
    ├── register.html       ← Register
    ├── products.html       ← Product listing
    ├── product_detail.html ← Single product
    ├── cart.html           ← Shopping cart
    ├── payment.html        ← Payment page
    ├── order_success.html  ← Order confirmed animation
    ├── user_profile.html   ← User profile + orders + favs
    └── search_results.html ← Full search results page
```

---

## ⚡ STEP-BY-STEP SETUP

### STEP 1 — Set Up MySQL Database

**Option A: Using MySQL Command Line**
```bash
# Open your terminal / command prompt and type:
mysql -u root -p

# Then enter your MySQL password when asked
# Then run:
source /path/to/SecureShop/schema.sql

# Example on Windows:
source C:/Users/YourName/Downloads/SecureShop/schema.sql

# Example on Mac/Linux:
source /home/yourname/Downloads/SecureShop/schema.sql
```

**Option B: Using XAMPP/phpMyAdmin**
1. Open XAMPP → Start Apache + MySQL
2. Open browser → go to `http://localhost/phpmyadmin`
3. Click **Import** tab at the top
4. Click **Choose File** → select `schema.sql`
5. Click **Go** at the bottom
6. You should see "1000 records inserted" ✅

**Option C: Using MySQL Workbench**
1. Open MySQL Workbench → Connect to your server
2. Click `File → Open SQL Script` → select `schema.sql`
3. Press `Ctrl+Shift+Enter` to run all

---

### STEP 2 — Edit Your Database Password

Open `app.py` and find line ~44:
```python
password='Pavanvas@123',   # ← Change to YOUR password
```
Change it to your actual MySQL root password.

Also open `config.py` and update:
```python
MYSQL_PASSWORD = 'your_password_here'
```

---

### STEP 3 — Get Razorpay Test API Keys (FREE)

1. Go to [dashboard.razorpay.com/signin](https://dashboard.razorpay.com/signin)
2. Create a free account
3. Go to **Settings → API Keys**
4. Click **Generate Test Key**
5. Copy your `Key ID` and `Key Secret`

In `app.py`, find lines ~26-27 and replace:
```python
RAZORPAY_KEY_ID     = 'rzp_test_YOUR_KEY_ID_HERE'
RAZORPAY_KEY_SECRET = 'YOUR_KEY_SECRET_HERE'
```

---

### STEP 4 — Install Python Packages

Open terminal in the SecureShop folder:

**Windows:**
```cmd
cd C:\Users\YourName\Downloads\SecureShop
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd ~/Downloads/SecureShop
pip3 install -r requirements.txt
```

If you get errors, try:
```bash
pip install flask flask-wtf bcrypt pymysql razorpay
```

---

### STEP 5 — Run the Application

```bash
# Windows
python app.py

# Mac/Linux
python3 app.py
```

You should see:
```
🚀 SecureShop starting at http://localhost:5000
🔒 CSRF Protection: ON
🔑 Session Security: ON
 * Running on http://127.0.0.1:5000
```

Open your browser and go to: **http://localhost:5000** 🎉

---

## 🧪 TESTING PAYMENTS (Test Mode)

Use these fake card details in the Razorpay popup:

| Field   | Value                  |
|---------|------------------------|
| Card No | `4111 1111 1111 1111`  |
| Expiry  | Any future date (e.g. 12/26) |
| CVV     | Any 3 digits (e.g. 123) |
| OTP     | `1234` (if asked)      |

---

## 🌐 APIS USED (All Free!)

| API | Purpose | Cost |
|-----|---------|------|
| **Razorpay** | Payment gateway (test mode) | Free |
| **Unsplash Source** | Product images | Free |
| **Google Fonts** | Syne + DM Sans fonts | Free |
| **Font Awesome** | Icons | Free |
| **cdnjs** | CDN for libraries | Free |

**Recommendation:** For even better search, you can later add:
- **Algolia** (free tier) — super-fast product search
- **OpenAI API** — for real AI recommendations

---

## 🔧 COMMON ERRORS & FIXES

**Error: `Access denied for user 'root'@'localhost'`**
→ Wrong MySQL password in `app.py`. Fix line 44.

**Error: `No module named 'flask'`**
→ Run: `pip install -r requirements.txt`

**Error: `Table 'secure_shop.products' doesn't exist`**
→ You haven't imported the database. Follow Step 1.

**Error: `razorpay.errors.BadRequestError`**
→ Your Razorpay keys are wrong. Get new keys from dashboard.

**Error: `CSRF token missing`**
→ Make sure all POST forms have `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`

---

## 🔑 DEFAULT TEST LOGIN

After importing the database, register a new account at `/register`.

---

## 📱 FEATURES LIST

✅ User Registration & Login (bcrypt hashed passwords)  
✅ CSRF Protection on all forms  
✅ Hero Slider (auto-slides every 1 second)  
✅ Live Search with Autocomplete  
✅ Product Listing with Filters & Sorting  
✅ Category Filtering  
✅ "Only X left!" Stock Indicators  
✅ Add to Cart (AJAX, no page reload)  
✅ Favourite Products (heart button)  
✅ Shopping Cart with Quantity Update  
✅ Razorpay Payment Integration  
✅ Order Confirmation Animation  
✅ Order History in Profile  
✅ Profile Image Upload  
✅ AI "Users Also Bought" Recommendations  
✅ Fully Responsive (Mobile Friendly)  

---

## 🛡️ SECURITY FEATURES

- **bcrypt** password hashing (industry standard)
- **CSRF protection** on all POST forms
- **Parameterized SQL queries** (no SQL injection possible)
- **Session-based authentication**
- **Razorpay signature verification** (payment cannot be faked)
- **Server-side total calculation** (price cannot be manipulated)
- **File upload validation** (only images allowed)

---

Built with ❤️ for SecureShop Codeathon
