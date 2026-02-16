# استيراد المكتبات المطلوبة
from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# إنشاء التطبيق
app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

DATABASE = "database.db"

# ==============================
# إنشاء قاعدة البيانات تلقائيًا
# ==============================
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        security_score INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# ==============================
# الاتصال بقاعدة البيانات
# ==============================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# دالة حماية الصفحات (يجب تسجيل الدخول)
# ==============================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("يجب تسجيل الدخول أولاً")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================
# الصفحة الرئيسية
# ==============================
@app.route('/')
def home():
    return redirect(url_for('login'))

# ==============================
# التسجيل
# ==============================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # تشفير كلمة المرور
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()

            flash("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("اسم المستخدم موجود بالفعل!")

    return render_template('register.html')

# ==============================
# تسجيل الدخول
# ==============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        # التحقق من كلمة المرور
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("تم تسجيل الدخول بنجاح")
            return redirect(url_for('dashboard'))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة")

    return render_template('login.html')

# ==============================
# لوحة التحكم
# ==============================
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session['user_id'],)
    ).fetchone()
    conn.close()

    return render_template('dashboard.html', user=user)

# ==============================
# تسجيل الخروج
# ==============================
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("تم تسجيل الخروج")
    return redirect(url_for('login'))

# ==============================
# تشغيل التطبيق
# ==============================
if __name__ == '__main__':
    init_db()  # إنشاء قاعدة البيانات عند التشغيل
    app.run(debug=True)


