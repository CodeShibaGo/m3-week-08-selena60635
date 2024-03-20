from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from datetime import datetime, timezone
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app, db
from app.forms import EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Post
from werkzeug.security import generate_password_hash

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('你的貼文現在已發布！'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('首頁'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title=_('登入'), username_error=username_error, password_error=password_error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
            username_error = _('此名稱已有人使用')
        if check_email:
            email_error = _('此信箱已有人使用')
        if not username:
            username_error = _('請填寫使用者名稱')
        if not email:
            email_error = _('請填寫郵件地址')
        if not password:
            password_error = _('請填寫密碼')
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
            return redirect(url_for('login'))
    return render_template('register.html', title=_('註冊'), username_error=username_error, email_error=email_error, password_error=password_error, password2_error=password2_error)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.locale = str(get_locale())
        
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('你的修改已被儲存。'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('編輯個人資料'),
                           form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('使用者 %(username)s 未找到。', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('你不能追蹤自己！'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('你正在追蹤 %(username)s ！', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('使用者 %(username)s 未找到。', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('你不能取消追蹤自己！'))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('你已經取消追蹤 %(username)s ！', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    # post總數
    posts_count = db.session.scalar(sa.text("SELECT COUNT(*) FROM post"))
    query = sa.text(f"SELECT * FROM post ORDER BY timestamp DESC LIMIT {per_page} OFFSET {(page - 1) * per_page}")
    posts = db.session.scalars(sa.select(Post).from_statement(query)).all()
    # 前幾頁的資料數量 < post總數，代表後面還有post，下一頁開啟
    next_url = url_for('explore', page=page + 1) if (page * per_page) < posts_count else None
    prev_url = url_for('explore', page=page - 1) if page > 1 else None
    return render_template("index.html", title=_('探索'), posts=posts,
                           next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash(_('請檢查你的電子郵件以獲取重設密碼的指示'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('重設密碼'), form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('您的密碼已重設。'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
