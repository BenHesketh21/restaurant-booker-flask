from table_booking import app
from table_booking.models import Users
from flask_login import current_user
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField, TimeField, DateTimeField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo


class NewTableForm(FlaskForm):
    table_number = IntegerField('Table Number',
        validators=[
            DataRequired()
        ]
    )
    number_of_seats = IntegerField('Number of Seats',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField('Add Table')

class BookTableForm(FlaskForm):
    number_of_customers = IntegerField("Number of Guests",
        validators=[
            DataRequired()
        ]
    )
    date_of_booking = DateField("Date of Booking",
        validators=[
            DataRequired()
        ],
        format='%Y-%m-%d'
    )
    time_of_booking = TimeField('Time of Booking',
        format="%H:%M")

    submit = SubmitField('Check Availability')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name',
            validators = [
                DataRequired(),
                Length(min=2, max=30)
            ]
    )

    last_name = StringField('Last Name',
            validators = [
                DataRequired(),
                Length(min=4, max=30)
            ]
    )
    email = StringField('Email',
        validators = [
            DataRequired(),
            Email()
        ]
    )
    password = PasswordField('Password',
        validators = [
            DataRequired(),
        ]
    )
    confirm_password = PasswordField('Confirm Password',
        validators = [
            DataRequired(),
            EqualTo('password')
        ]
    )
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('Email already in use')


class LoginForm(FlaskForm):
	email = StringField('Email',
		validators=[
			DataRequired(),
			Email()
		])
	password = PasswordField('Password',
		validators=[
			DataRequired(),
		])
	remember = BooleanField('Remember Me')
    
	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name',
            validators = [
                DataRequired(),
                Length(min=2, max=30)
            ]
    )

    last_name = StringField('Last Name',
            validators = [
                DataRequired(),
                Length(min=4, max=30)
            ]
    )
    email = StringField('Email',
        validators = [
            DataRequired(),
            Email()
        ]
    )
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use')

