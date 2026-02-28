# config.py

class Config:
    SECRET_KEY = 'your_super_secret_key_change_this_123456'
    
    # MySQL config using PyMySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root123'   # ← Your correct password
    MYSQL_DB = 'secure_shop'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    
    RAZORPAY_KEY_ID = 'rzp_test_XXXXXXXXXXXXXXXX'
    RAZORPAY_KEY_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXX'