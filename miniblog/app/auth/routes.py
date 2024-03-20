from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email
from app.models import User
from werkzeug.security import generate_password_hash


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    username_error = None
    password_error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me')
        # 檢查是否有填寫(required)
        if username:
            username_error = None
        else:
            username_error = _('此欄位不得為空')
        if password:
            password_error = None
        else:
            password_error = _('此欄位不得為空')
        # 抓出使用者資料，查看是否有這筆資料、驗證密碼
        user = db.session.scalar(db.select(User).from_statement(db.text(f"SELECT * FROM user WHERE  username='{username}'")))
        if user is None or not user.check_password(password):
            flash(_('無效的使用者名稱或密碼'))
        else:
            login_user(user, remember = remember)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
    return render_template('auth/login.html', title=_('登入'), username_error=username_error, password_error=password_error)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # 錯誤訊息
    username_error = None
    email_error = None
    password_error = None
    password2_error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('re_password')
        db_password = generate_password_hash(password)
        check_name = db.session.scalar(db.select(User).from_statement(db.text(f"SELECT * FROM user WHERE username = '{username}'")))
        check_email = db.session.scalar(db.select(User).from_statement(db.text(f"SELECT * FROM user WHERE email = '{email}'"))) 
        # 表單驗證
        if check_name:
            username_error =  _('此名稱已有人使用')
        if check_email:
            email_error = _('此信箱已有人使用')
        if not username:
            username_error = _('請填寫使用者名稱')
        if not email:
            email_error =  _('請填寫郵件地址')
        if not password:
            password_error =  _('請填寫密碼')
        if not password2:
            password2_error = _('再輸入一次密碼')
        # 驗證第二次密碼
        if password and password2 and password != password2:
            password2_error = _('密碼錯誤')
            # 驗證通過，新增一筆使用者資料
        elif not (username_error or email_error or password_error or password2_error):
            new_user = User(username=username, email=email, password_hash=db_password)
            insert_query = db.text("INSERT INTO user (username, email, password_hash, about_me, last_seen) VALUES (:username, :email, :password_hash, :about_me, :last_seen)")
            params = {
                'username': new_user.username,
                'email': new_user.email,
                'password_hash': new_user.password_hash,
                'about_me': new_user.about_me,
                'last_seen': new_user.last_seen
                }
            db.session.execute(insert_query, params)
            db.session.commit()
            flash(_('恭喜，你現在是一名註冊使用者！'))
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('註冊'), username_error=username_error, email_error=email_error, password_error=password_error, password2_error=password2_error)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash(_('請檢查你的電子郵件以獲取重設密碼的指示'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('重設密碼'), form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('您的密碼已重設。'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

