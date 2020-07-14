from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Required
from hospital.models import Doctor,Patient,Admin


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add')


    def validate_email(self, email):
        if email.data != current_user.id:
            doctor = Doctor.query.filter_by(id=email.data).first()
            patient = Patient.query.filter_by(id=email.data).first()
            admin = Admin.query.filter_by(id=email.data).first()
            if doctor:
                raise ValidationError('That email is taken. Please choose a different one.')
            elif patient:
                raise ValidationError('That email is taken. Please choose a different one.')
            elif admin:
                raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    
    def validate_email(self, email):
        if email.data != current_user.id:
            doctor = Doctor.query.filter_by(id=email.data).first()
            patient = Patient.query.filter_by(id=email.data).first()
            admin = Admin.query.filter_by(id=email.data).first()
            if doctor:
                raise ValidationError('That email is taken. Please choose a different one.')
            elif patient:
                raise ValidationError('That email is taken. Please choose a different one.')
            elif admin:
                raise ValidationError('That email is taken. Please choose a different one.')

class UpdateAccountAdminForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

class UploadPictureForm(FlaskForm):
    picture = FileField('Update Diagnosis Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit1 = SubmitField('Upload Image')


class DiagnosisForm(FlaskForm):
    status = StringField('Status', validators=[DataRequired()])
    patientemail = StringField('Patient`s Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Diagnosis Picture', validators=[FileAllowed(['jpg', 'png'])])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add')


class DateForm(FlaskForm):
    date = DateField('Which date are you looking form?', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Search')
