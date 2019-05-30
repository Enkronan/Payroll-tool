from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User, Employee, Company
from app.validators import Unique

class RegistrationForm(FlaskForm):
    username = StringField('username', 
                            validators=[DataRequired(), Length(min=2, max=30)])

    password = PasswordField('password',
                            validators=[DataRequired()])
    
    confirm_password = PasswordField('confirm password',
                            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('register')

    def validate_username(self, username):
        
        user = User.query.filter_by(username=username.data).first()
        
        if user:
            raise ValidationError('That username is taken, please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=30)])

    password = PasswordField('Password',
                            validators=[DataRequired()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('login')

class AddCompany(FlaskForm):
    company_name = StringField('company name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    org_number = StringField('org number', validators=[Optional()])

    permanent_establishment = BooleanField('PE')

    submit = SubmitField('Add company')

    def validate_company_name(self, company_name):
        
        comp = Company.query.filter_by(company_name=company_name.data).first()
        
        if comp:
            raise ValidationError('That company is already registered, please try to select it instead.')

    def validate_org_number(self, org_number):
        
        if org_number.data != '':
            comp = Company.query.filter_by(org_number=org_number.data).first()
        
            if comp:
                raise ValidationError('That org number is already registered, please try to select it instead.')
    
class AddEmployee(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=40)])

    person_nummer = IntegerField('Personal Number', validators=[Optional()])

    expat_type = SelectField('Expat Type', choices=[('Outbound', "Outbound"),('Inbound', "Inbound")], validators=[DataRequired()])

    assign_start = DateField('entry date', format='%Y-%m-%d', validators=[Optional()])

    assign_end = DateField('exit date', format='%Y-%m-%d', validators=[Optional()])

    expert = BooleanField('Expert')

    sink = BooleanField('sink')

    six_month_rule = BooleanField('six_month_rule')

    social_security = SelectField('Expat Type', choices=[('1A', "utsänd till Kanada, Usa, Indien, Sydkorea")], validators=[DataRequired()])

    submit = SubmitField('Add Employee')

    def validate_person_nummer(self, person_nummer):
        
        if person_nummer:
            emp = Employee.query.filter_by(person_nummer=person_nummer.data).first()
        
            if emp:
                raise ValidationError('That employee is already registered, please try to select it instead.')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        emp = Employee.query.filter_by(first_name = self.first_name.data, last_name = self.last_name.data).first()

        if emp: 
            self.first_name.errors.append('An employee with that first name and last name is already registered, please try to select it instead.')
            return False
        
        return True

class CalculateInitial(FlaskForm):
    net_1 = IntegerField('Net Amount', validators=[Optional()], default = 0)

    net_2 = IntegerField('Net Amount', validators=[Optional()], default = 0)

    net_3 = IntegerField('Net Amount', validators=[Optional()], default = 0)

    gross_1 = IntegerField('Gross Amount', validators=[Optional()], default = 0)

    gross_2 = IntegerField('Gross Amount', validators=[Optional()], default = 0)

    gross_3 = IntegerField('Gross Amount', validators=[Optional()], default = 0)

    submit = SubmitField('Calculate')