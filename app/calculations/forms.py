from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User, Employee, Company, EmployeePayItem

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
    
class EditCompany(FlaskForm):
    company_name = StringField('company name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    org_number = StringField('org number', validators=[Optional()])

    permanent_establishment = BooleanField('PE')

    submit = SubmitField('Edit company')

class AddEmployee(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    last_name = StringField('Last Name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    person_nummer = IntegerField('Personal Number', validators=[Optional()])

    skattetabell = SelectField('Skattetabell',
                            choices=[('29', '29'),('30','30'),('31','31')], validators=[DataRequired()])

    expat_type = SelectField('Expat Type', choices=[('Outbound', "Outbound"),('Inbound', "Inbound")],
                            validators=[DataRequired()])

    assign_start = DateField('entry date', format='%Y-%m-%d', validators=[Optional()])

    assign_end = DateField('exit date', format='%Y-%m-%d', validators=[Optional()])

    expert = BooleanField('Expert')

    sink = BooleanField('sink')

    six_month_rule = BooleanField('six_month_rule')

    social_security = SelectField('Expat Type', choices=[('1A', "utsänd till Kanada, Usa, Indien, Sydkorea")],
                            validators=[DataRequired()])

    submit = SubmitField('Add Employee')

    def validate_person_nummer(self, person_nummer):
        
        if person_nummer:
            emp = Employee.query.filter_by(person_nummer=person_nummer.data).first()
        
            if emp:
                raise ValidationError('That personal number is already registered, please try to select it instead.')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        emp = Employee.query.filter_by(first_name = self.first_name.data,
                            last_name = self.last_name.data).first()

        if emp: 
            self.first_name.errors.append('An employee with that first name and last name is already registered, please try to select it instead.')
            return False
        
        return True

class EditEmployee(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    last_name = StringField('Last Name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    person_nummer = IntegerField('Personal Number', validators=[Optional()])

    skattetabell = SelectField('Skattetabell', choices=[('29', '29'),('30','30'),('31','31')], 
                            validators=[DataRequired()])

    expat_type = SelectField('Expat Type', choices=[('Outbound', "Outbound"),('Inbound', "Inbound")], 
                            validators=[DataRequired()])

    assign_start = DateField('entry date', format='%Y-%m-%d', validators=[Optional()])

    assign_end = DateField('exit date', format='%Y-%m-%d', validators=[Optional()])

    expert = BooleanField('Expert')

    sink = BooleanField('sink')

    six_month_rule = BooleanField('six_month_rule')

    social_security = SelectField('Expat Type', choices=[('1A', "utsänd till Kanada, Usa, Indien, Sydkorea")], 
                            validators=[DataRequired()])

    submit = SubmitField('Edit Employee')

class CalculateInitial(FlaskForm):
    cash_amount = IntegerField('Cash Amount', validators=[Optional()], default = 0)

    cash_type = SelectField('Cash Type', choices=[('Gross', "Gross"),('Net', "Net")], validators=[DataRequired()])

    submit = SubmitField('Calculate')
    

class PayItems(FlaskForm):
    pay_item = StringField('Pay Item Name', 
                            validators=[DataRequired(), Length(min=2, max=40)])

    tax_setting =  SelectField('Tax Settings', choices=[('Cash', "Cash"),('Benefit', "Benefit")], 
                            validators=[DataRequired()])

    cash_type = SelectField('Cash Type', choices=[('Gross', "Gross"),('Net', "Net")], 
                            validators=[DataRequired()])

    submit = SubmitField('Add Pay Item')

class AddEmployeePayItems(FlaskForm):
    amount = IntegerField('Cash Amount', validators=[DataRequired()])
    currency = SelectField('Currency', choices=[('SEK', "SEK"),('USD', "USD")], 
                            validators=[DataRequired()])

    def validate_amount(self, amount):
        if amount.data <= 0:
            raise ValidationError('The amount needs to be more than zero.')

class AuthorizationForm(FlaskForm):
    email = StringField('Email used for registration',
                            validators=[DataRequired(), Email()])

    submit = SubmitField('Provide user with access')

    def validate_email(self, email):
        
        user = User.query.filter_by(email=email.data).first()
        
        if not user:
            raise ValidationError('That email is not used, please check the spelling.')

class PayRunForm(FlaskForm):
    month = SelectField('Month', choices=[("January","January"),("February","February")], 
                            validators=[DataRequired()])
    year = SelectField('Year', choices=[("2018","2018"),("2019","2019")], 
                            validators=[DataRequired()])

    submit = SubmitField('Add Payroll Run')


