# app.py - Complete Secure Online Shopping Portal
# SecureShop - Codeathon Project

from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash)
from flask_wtf.csrf import CSRFProtect, CSRFError
import bcrypt
import pymysql
import pymysql.cursors
import razorpay
import os
from functools import wraps
from werkzeug.utils import secure_filename

# ══════════════════════════════════════
# APP SETUP
# ══════════════════════════════════════
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secureshop_secret_key_2024_codeathon_xyz'
app.config['WTF_CSRF_TIME_LIMIT'] = None   # CSRF token never expires

# File upload config
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max

# ── Razorpay Test Keys ──
# Get these from https://dashboard.razorpay.com → Settings → API Keys
RAZORPAY_KEY_ID     = 'rzp_test_SKIe1sKK4EMoni'   # ← Replace with yours
RAZORPAY_KEY_SECRET = 's2nLhLjbnOhXPuqWvey3isBW'    # ← Replace with yours

# ── CSRF Protection ──
csrf = CSRFProtect(app)

# ══════════════════════════════════════
# DATABASE CONNECTION
# ══════════════════════════════════════
import os
import pymysql
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL")

url = urlparse(DATABASE_URL)

connection = pymysql.connect(
    host=url.hostname,
    user=url.username,
    password=url.password,
    database=url.path[1:],   # remove /
    port=url.port,
    cursorclass=pymysql.cursors.DictCursor
)

# ══════════════════════════════════════
# HELPER: ALLOWED IMAGE EXTENSIONS
# ══════════════════════════════════════
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

# ══════════════════════════════════════
# DECORATOR: LOGIN REQUIRED
# ══════════════════════════════════════
def login_required(f):
    """Use @login_required above any route that needs login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # For AJAX/JSON requests, return JSON with redirect
            if request.is_json or request.headers.get('X-CSRFToken') or request.content_type == 'application/json':
                return jsonify({'success': False, 'redirect': '/login', 'message': 'Please login to continue'})
            flash('Please login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ══════════════════════════════════════
# HELPER: GET CART COUNT
# ══════════════════════════════════════
def get_cart_count(user_id):
    """Returns total number of items in user's cart"""
    if not user_id:
        return 0
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(quantity), 0) as total FROM cart WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return int(result['total']) if result else 0
    except:
        return 0

# ══════════════════════════════════════════════════════════
# ROUTE 1: HOME PAGE
# ══════════════════════════════════════════════════════════
@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()

    # Featured products (top rated, in stock)
    cursor.execute("""
        SELECT * FROM products
        WHERE stock > 0
        ORDER BY rating DESC
        LIMIT 12
    """)
    featured_products = cursor.fetchall()

    # Hero slider products (top 5)
    cursor.execute("""
        SELECT * FROM products
        WHERE stock > 0
        ORDER BY rating DESC
        LIMIT 5
    """)
    slider_products = cursor.fetchall()

    # All categories
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = cursor.fetchall()

    # AI Recommendations - "Users also bought" (random popular products)
    cursor.execute("""
        SELECT * FROM products
        WHERE stock > 0
        ORDER BY RAND()
        LIMIT 6
    """)
    recommended = cursor.fetchall()

    cursor.close()
    db.close()

    cart_count = get_cart_count(session.get('user_id'))

    return render_template('home.html',
                           featured_products=featured_products,
                           slider_products=slider_products,
                           categories=categories,
                           recommended=recommended,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 2: REGISTER
# ══════════════════════════════════════════════════════════
@app.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, go home
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        mobile   = request.form.get('mobile', '').strip()
        password = request.form.get('password', '').strip()

        # ── Validate inputs ──
        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters')
        if not email or '@' not in email:
            errors.append('Enter a valid email address')
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            errors.append('Enter a valid 10-digit mobile number')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        # ── Hash password with bcrypt (SECURITY) ──
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        db = get_db()
        cursor = db.cursor()
        try:
            # Check if email already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = %s", (email,)
            )
            if cursor.fetchone():
                flash('Email already registered! Please login.', 'error')
                return render_template('register.html')

            # Insert new user (parameterized query = SQL injection safe)
            cursor.execute("""
                INSERT INTO users (name, email, mobile, password)
                VALUES (%s, %s, %s, %s)
            """, (name, email, mobile, hashed_password))
            db.commit()

            flash('✅ Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

# ══════════════════════════════════════════════════════════
# ROUTE 3: LOGIN
# ══════════════════════════════════════════════════════════
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email and password are required!', 'error')
            return render_template('login.html')

        db = get_db()
        cursor = db.cursor()
        # Parameterized query - SQL injection safe
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        # Check password using bcrypt
        if user and bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            # Set session variables
            session.permanent  = True
            session['user_id']    = user['id']
            session['user_name']  = user['name']
            session['user_email'] = user['email']

            flash(f"Welcome back, {user['name'].split()[0]}! 🎉", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password!', 'error')
            return render_template('login.html')

    return render_template('login.html')

# ══════════════════════════════════════════════════════════
# ROUTE 4: LOGOUT
# ══════════════════════════════════════════════════════════
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# ══════════════════════════════════════════════════════════
# ROUTE 5: USER PROFILE
# ══════════════════════════════════════════════════════════
@app.route('/profile')
@login_required
def profile():
    db = get_db()
    cursor = db.cursor()

    # Get user details
    cursor.execute(
        "SELECT * FROM users WHERE id = %s", (session['user_id'],)
    )
    user = cursor.fetchone()

    # Get order history
    cursor.execute("""
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()

    # Get favourites
    cursor.execute("""
        SELECT p.* FROM favorites f
        JOIN products p ON f.product_id = p.id
        WHERE f.user_id = %s
        ORDER BY f.added_at DESC
    """, (session['user_id'],))
    favorites = cursor.fetchall()

    cart_count = get_cart_count(session['user_id'])
    cursor.close()
    db.close()

    return render_template('user_profile.html',
                           user=user,
                           orders=orders,
                           favorites=favorites,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 6: UPDATE PROFILE
# ══════════════════════════════════════════════════════════
@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    name   = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()

    db = get_db()
    cursor = db.cursor()
    try:
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(
                    f"user_{session['user_id']}_{file.filename}"
                )
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute("""
                    UPDATE users SET name=%s, mobile=%s, profile_image=%s
                    WHERE id=%s
                """, (name, mobile, filename, session['user_id']))
            else:
                cursor.execute(
                    "UPDATE users SET name=%s, mobile=%s WHERE id=%s",
                    (name, mobile, session['user_id'])
                )
        else:
            cursor.execute(
                "UPDATE users SET name=%s, mobile=%s WHERE id=%s",
                (name, mobile, session['user_id'])
            )

        db.commit()
        session['user_name'] = name
        flash('✅ Profile updated successfully!', 'success')

    except Exception as e:
        db.rollback()
        flash('Update failed. Try again.', 'error')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('profile'))

# ══════════════════════════════════════════════════════════
# ROUTE 7: PRODUCTS PAGE
# ══════════════════════════════════════════════════════════
@app.route('/products')
@login_required
def products():
    category = request.args.get('category', '').strip()
    sort     = request.args.get('sort', '').strip()
    page     = max(1, int(request.args.get('page', 1)))
    per_page = 20
    offset   = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()

    # Build dynamic query
    where  = "WHERE stock > 0"
    params = []

    if category:
        where += " AND category = %s"
        params.append(category)

    order = {
        'price_asc':  "ORDER BY price ASC",
        'price_desc': "ORDER BY price DESC",
        'rating':     "ORDER BY rating DESC",
    }.get(sort, "ORDER BY id DESC")

    cursor.execute(
        f"SELECT * FROM products {where} {order} LIMIT %s OFFSET %s",
        params + [per_page, offset]
    )
    products_list = cursor.fetchall()

    # Total count for pagination
    cursor.execute(
        f"SELECT COUNT(*) as total FROM products {where}",
        params
    )
    total      = cursor.fetchone()['total']
    total_pages = max(1, (total + per_page - 1) // per_page)

    # All categories
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = cursor.fetchall()

    # User's favourites and cart items (to show active states)
    cursor.execute(
        "SELECT product_id FROM favorites WHERE user_id = %s",
        (session['user_id'],)
    )
    fav_ids = [r['product_id'] for r in cursor.fetchall()]

    cursor.execute(
        "SELECT product_id FROM cart WHERE user_id = %s",
        (session['user_id'],)
    )
    cart_ids = [r['product_id'] for r in cursor.fetchall()]

    cart_count = get_cart_count(session['user_id'])
    cursor.close()
    db.close()

    return render_template('products.html',
                           products=products_list,
                           categories=categories,
                           current_category=category,
                           current_sort=sort,
                           page=page,
                           total_pages=total_pages,
                           fav_ids=fav_ids,
                           cart_ids=cart_ids,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 8: PRODUCT DETAIL PAGE
# ══════════════════════════════════════════════════════════
@app.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('products'))

    # Related products (same category, different product)
    cursor.execute("""
        SELECT * FROM products
        WHERE category = %s AND id != %s AND stock > 0
        ORDER BY RAND()
        LIMIT 4
    """, (product['category'], product_id))
    related = cursor.fetchall()

    cart_count = get_cart_count(session['user_id'])
    cursor.close()
    db.close()

    return render_template('product_detail.html',
                           product=product,
                           related=related,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 9: LIVE SEARCH (AJAX - returns JSON)
# ══════════════════════════════════════════════════════════
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify({'products': [], 'suggestions': []})

    db = get_db()
    cursor = db.cursor()

    # Search products
    cursor.execute("""
        SELECT id, name, price, image_url, category, rating
        FROM products
        WHERE (name LIKE %s OR category LIKE %s) AND stock > 0
        LIMIT 8
    """, (f'%{query}%', f'%{query}%'))
    products_found = cursor.fetchall()

    # Build smart suggestions like "jeans for Men", "jeans for Women"
    cursor.execute("""
        SELECT DISTINCT category FROM products
        WHERE name LIKE %s OR category LIKE %s
    """, (f'%{query}%', f'%{query}%'))
    matching_categories = cursor.fetchall()

    suggestions = []
    for cat in matching_categories:
        suggestions.append(f"{query.title()} for {cat['category']}")

    # Also add direct name suggestions
    cursor.execute("""
        SELECT DISTINCT name FROM products
        WHERE name LIKE %s
        LIMIT 4
    """, (f'{query}%',))
    name_matches = cursor.fetchall()
    for n in name_matches:
        if n['name'] not in suggestions:
            suggestions.append(n['name'])

    cursor.close()
    db.close()

    # Convert Decimal to float for JSON
    for p in products_found:
        p['price']  = float(p['price'])
        p['rating'] = float(p['rating'])

    return jsonify({
        'products':    products_found,
        'suggestions': suggestions[:8]
    })

# ══════════════════════════════════════════════════════════
# ROUTE 10: SEARCH RESULTS PAGE (Full page with slider)
# ══════════════════════════════════════════════════════════
@app.route('/search-results')
@login_required
def search_results():
    query = request.args.get('q', '').strip()

    if not query:
        return redirect(url_for('products'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE (name LIKE %s OR category LIKE %s) AND stock > 0
        ORDER BY rating DESC
        LIMIT 50
    """, (f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()

    # Related categories for suggestion chips
    cursor.execute("""
        SELECT DISTINCT category FROM products
        WHERE name LIKE %s OR category LIKE %s
    """, (f'%{query}%', f'%{query}%'))
    related_categories = cursor.fetchall()

    cart_count = get_cart_count(session['user_id'])
    cursor.close()
    db.close()

    return render_template('search_results.html',
                           results=results,
                           query=query,
                           related_categories=related_categories,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 11: ADD TO CART (AJAX)
# ══════════════════════════════════════════════════════════
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data       = request.get_json()
    product_id = data.get('product_id')
    quantity   = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'success': False, 'message': 'Invalid product'})

    db = get_db()
    cursor = db.cursor()
    try:
        # Check if already in cart
        cursor.execute(
            "SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s",
            (session['user_id'], product_id)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE id = %s",
                (quantity, existing['id'])
            )
        else:
            cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,%s)",
                (session['user_id'], product_id, quantity)
            )
        db.commit()

        cart_count = get_cart_count(session['user_id'])
        return jsonify({
            'success':    True,
            'message':    'Added to cart!',
            'cart_count': cart_count
        })

    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Failed to add to cart'})
    finally:
        cursor.close()
        db.close()

# ══════════════════════════════════════════════════════════
# ROUTE 12: VIEW CART
# ══════════════════════════════════════════════════════════
@app.route('/cart')
@login_required
def cart():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT c.id as cart_id, c.quantity, p.*
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
        ORDER BY c.added_at DESC
    """, (session['user_id'],))
    cart_items = cursor.fetchall()

    total = sum(float(item['price']) * item['quantity'] for item in cart_items)
    cart_count = sum(item['quantity'] for item in cart_items)

    cursor.close()
    db.close()

    return render_template('cart.html',
                           cart_items=cart_items,
                           total=round(total, 2),
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 13: REMOVE FROM CART (AJAX)
# ══════════════════════════════════════════════════════════
@app.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data    = request.get_json()
    cart_id = data.get('cart_id')

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM cart WHERE id = %s AND user_id = %s",
            (cart_id, session['user_id'])
        )
        db.commit()

        # Recalculate totals
        cursor.execute("""
            SELECT COALESCE(SUM(p.price * c.quantity), 0) as total,
                   COALESCE(SUM(c.quantity), 0) as count
            FROM cart c JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['user_id'],))
        result     = cursor.fetchone()
        total      = float(result['total'])
        cart_count = int(result['count'])

        return jsonify({
            'success':    True,
            'total':      round(total, 2),
            'cart_count': cart_count
        })
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Failed to remove'})
    finally:
        cursor.close()
        db.close()

# ══════════════════════════════════════════════════════════
# ROUTE 14: UPDATE CART QUANTITY (AJAX)
# ══════════════════════════════════════════════════════════
@app.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    data     = request.get_json()
    cart_id  = data.get('cart_id')
    quantity = int(data.get('quantity', 1))

    if quantity < 1:
        return jsonify({'success': False, 'message': 'Invalid quantity'})

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE cart SET quantity=%s WHERE id=%s AND user_id=%s",
            (quantity, cart_id, session['user_id'])
        )
        db.commit()

        cursor.execute("""
            SELECT COALESCE(SUM(p.price * c.quantity), 0) as total,
                   COALESCE(SUM(c.quantity), 0) as count
            FROM cart c JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['user_id'],))
        result     = cursor.fetchone()
        total      = float(result['total'])
        cart_count = int(result['count'])

        return jsonify({
            'success':    True,
            'total':      round(total, 2),
            'cart_count': cart_count
        })
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Update failed'})
    finally:
        cursor.close()
        db.close()

# ══════════════════════════════════════════════════════════
# ROUTE 15: TOGGLE FAVOURITE (AJAX)
# ══════════════════════════════════════════════════════════
@app.route('/favorites/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    data       = request.get_json()
    product_id = data.get('product_id')

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id FROM favorites WHERE user_id=%s AND product_id=%s",
            (session['user_id'], product_id)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "DELETE FROM favorites WHERE id = %s", (existing['id'],)
            )
            db.commit()
            return jsonify({
                'success': True,
                'action':  'removed',
                'message': 'Removed from favourites'
            })
        else:
            cursor.execute(
                "INSERT INTO favorites (user_id, product_id) VALUES (%s,%s)",
                (session['user_id'], product_id)
            )
            db.commit()
            return jsonify({
                'success': True,
                'action':  'added',
                'message': 'Added to favourites!'
            })
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Action failed'})
    finally:
        cursor.close()
        db.close()

# ══════════════════════════════════════════════════════════
# ROUTE 16: PAYMENT PAGE
# ══════════════════════════════════════════════════════════
@app.route('/payment')
@login_required
def payment():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT c.id as cart_id, c.quantity, p.*
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (session['user_id'],))
    cart_items = cursor.fetchall()

    if not cart_items:
        flash('Your cart is empty! Add products first.', 'warning')
        return redirect(url_for('cart'))

    total = sum(float(item['price']) * item['quantity'] for item in cart_items)
    cart_count = get_cart_count(session['user_id'])

    cursor.close()
    db.close()

    return render_template('payment.html',
                           cart_items=cart_items,
                           total=round(total, 2),
                           razorpay_key=RAZORPAY_KEY_ID,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 17: CREATE RAZORPAY ORDER (AJAX)
# ══════════════════════════════════════════════════════════
@app.route('/payment/create-order', methods=['POST'])
@login_required
def create_payment_order():
    db = get_db()
    cursor = db.cursor()

    # Always calculate total from DB (never trust frontend)
    cursor.execute("""
        SELECT COALESCE(SUM(p.price * c.quantity), 0) as total
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (session['user_id'],))
    result = cursor.fetchone()
    total  = float(result['total']) if result else 0

    cursor.close()
    db.close()

    if total <= 0:
        return jsonify({'success': False, 'message': 'Cart is empty'})

    try:
        client     = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        order_data = {
            'amount':          int(total * 100),  # paise
            'currency':        'INR',
            'payment_capture': 1
        }
        razorpay_order = client.order.create(data=order_data)

        return jsonify({
            'success':  True,
            'order_id': razorpay_order['id'],
            'amount':   int(total * 100),
            'currency': 'INR'
        })

    except Exception as e:
        print(f"Razorpay error: {e}")
        return jsonify({'success': False, 'message': 'Payment setup failed'})

# ══════════════════════════════════════════════════════════
# ROUTE 18: VERIFY PAYMENT (AJAX)
# ══════════════════════════════════════════════════════════
@app.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    data       = request.get_json()
    payment_id = data.get('razorpay_payment_id')
    order_id   = data.get('razorpay_order_id')
    signature  = data.get('razorpay_signature')

    db = get_db()
    cursor = db.cursor()

    try:
        # Verify Razorpay signature (SECURITY CHECK)
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id':   order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature':  signature
        })

        # Get cart items
        cursor.execute("""
            SELECT c.quantity, p.id as product_id, p.price
            FROM cart c JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['user_id'],))
        cart_items = cursor.fetchall()
        total = sum(float(i['price']) * i['quantity'] for i in cart_items)

        # Create order record
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, payment_status, transaction_id)
            VALUES (%s, %s, 'paid', %s)
        """, (session['user_id'], total, payment_id))
        new_order_id = cursor.lastrowid

        # Save each item in order_items
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (new_order_id, item['product_id'], item['quantity'], item['price']))

        # Clear cart after successful payment
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s", (session['user_id'],)
        )
        db.commit()

        return jsonify({'success': True, 'order_id': new_order_id})

    except Exception as e:
        # Payment verification failed
        print(f"Payment verify error: {e}")
        try:
            cursor.execute("""
                INSERT INTO orders (user_id, total_amount, payment_status, transaction_id)
                VALUES (%s, 0, 'failed', %s)
            """, (session['user_id'], payment_id or 'unknown'))
            db.commit()
        except:
            pass
        return jsonify({'success': False, 'message': 'Payment verification failed'})
    finally:
        cursor.close()
        db.close()

# ══════════════════════════════════════════════════════════
# ROUTE 19: ORDER SUCCESS PAGE
# ══════════════════════════════════════════════════════════
@app.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM orders
        WHERE id = %s AND user_id = %s
    """, (order_id, session['user_id']))
    order = cursor.fetchone()

    cursor.close()
    db.close()

    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('home'))

    cart_count = 0  # Cart was cleared after payment
    return render_template('order_success.html',
                           order=order,
                           cart_count=cart_count)

# ══════════════════════════════════════════════════════════
# ROUTE 20: BUY NOW (skip cart → go directly to payment)
# ══════════════════════════════════════════════════════════
@app.route('/buy-now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    db = get_db()
    cursor = db.cursor()
    try:
        # Clear existing cart, add only this product
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s", (session['user_id'],)
        )
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,1)",
            (session['user_id'], product_id)
        )
        db.commit()
    except:
        db.rollback()
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('payment'))

# ══════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════
@app.errorhandler(404)
def page_not_found(e):
    return render_template('home.html',
                           featured_products=[],
                           slider_products=[],
                           categories=[],
                           recommended=[],
                           cart_count=0), 404

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Security token expired. Please try again.', 'error')
    return redirect(request.referrer or url_for('home'))

# ══════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════
if __name__ == '__main__':
    os.makedirs('static/uploads', exist_ok=True)
    print("🚀 SecureShop starting at http://localhost:5000")
    print("🔒 CSRF Protection: ON")
    print("🔑 Session Security: ON")
    app.run(debug=True, port=5000)