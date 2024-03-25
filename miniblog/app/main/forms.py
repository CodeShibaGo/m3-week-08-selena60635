from flask_wtf import FlaskForm
from flask_babel import _
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from app import db
from app.models import User

class EmptyForm(FlaskForm):
    submit = SubmitField(_('提交'))
    follow = SubmitField(_('追蹤'))
    unfollow = SubmitField(_('取消追蹤'))

class EditProfileForm(FlaskForm):
    username = StringField(_l('使用者名稱'), validators=[DataRequired()])
    about_me = TextAreaField(_l('關於我'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('提交'),)

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(
                sa.select(User).from_statement(sa.text(f"SELECT * FROM user WHERE username = '{self.username.data}'")))
            if user is not None:
                raise ValidationError(_('請使用不同的使用者名稱。'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('說點什麼'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('提交'))

