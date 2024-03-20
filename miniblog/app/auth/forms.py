from flask_wtf import FlaskForm
from flask_babel import _
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('信箱'),  validators=[DataRequired(), Email()])
    submit = SubmitField(_l('請求重設密碼'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('密碼'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('再輸入一次密碼'),  validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('重設密碼'))