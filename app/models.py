from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

access = db.Table('access',
    db.Column('company_id', db.Integer, db.ForeignKey('company.id', primary_key=True)),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', primary_key=True)),
)
'''
month_to_company = db.Table('month_to_company',
    db.Column('company_id', db.Integer, db.ForeignKey('company.id', primary_key=True)),
    db.Column('payrun_id', db.Integer, db.ForeignKey('payrun.id', primary_key=True)),
)
'''
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True)
    access = db.relationship('Company', secondary=access, lazy='subquery',
        backref=db.backref('users', lazy=True))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.access}')"

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_name = db.Column(db.String(60), unique = True, nullable = False)
    org_number = db.Column(db.String(60))
    permanent_establishment = db.Column(db.Boolean, nullable=False)

    expats = db.relationship('Employee', backref='company', lazy=True)
    monthly_employee = db.relationship('MonthlyEmployee', backref='company', lazy=True) 
    pay_items = db.relationship('PayItem', backref='company', lazy=True)
    payroll_runs = db.relationship('PayRun', backref='company', lazy=True)

    def __repr__(self):
        return f"Company('{self.company_name}', '{self.org_number}','{self.permanent_establishment}')" 

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(60), nullable = False)
    last_name = db.Column(db.String(60), nullable = False)
    person_nummer = db.Column(db.Integer, unique = True)
    skattetabell = db.Column(db.String(60), nullable = False)
    expat_type = db.Column(db.String(60), nullable = False)
    assign_start = db.Column(db.DateTime)
    assign_end = db.Column(db.DateTime)
    expert = db.Column(db.Boolean, nullable=False)
    sink = db.Column(db.Boolean, nullable=False)
    six_month_rule = db.Column(db.Boolean, nullable=False)
    social_security = db.Column(db.String(60), nullable = False)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)
    pay_items = db.relationship('EmployeePayItem', backref='employee', lazy=True)
    monthly_employee = db.relationship('MonthlyEmployee', backref='employee', lazy=True)

    def __repr__(self):
        return f"Employee('{self.first_name}', '{self.last_name}','{self.person_nummer}','{self.expat_type}', '{self.assign_start}', '{self.assign_end}', '{self.expert}', '{self.sink}', '{self.six_month_rule}', '{self.social_security}', '{self.pay_items}')"      

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class PayItem(db.Model):
    __tablename__ = 'payitem'
    id = db.Column(db.Integer, primary_key = True)
    pay_item = db.Column(db.String(150), nullable = False)
    tax_setting = db.Column(db.String(60), nullable = False)
    cash_type = db.Column(db.String(60), nullable = False)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    employee_pay_items = db.relationship('EmployeePayItem', backref='payitem', lazy=True)

    def __repr__(self):
        return f"Pay Item('{self.pay_item}', '{self.tax_setting}', '{self.cash_type}', '{self.company_id}')" 

class EmployeePayItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    pay_item_id = db.Column(db.Integer, db.ForeignKey('payitem.id'), nullable=False)
    amount = db.Column(db.Integer, nullable = False)
    currency = db.Column(db.String(60), nullable = False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    def __repr__(self):
        return f"Employee Pay Item('{self.pay_item_id}', '{self.amount}', '{self.currency}', '{self.employee_id}')" 

class MonthlyPayItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    pay_item = db.Column(db.String(150), nullable = False)
    tax_setting = db.Column(db.String(60), nullable = False)
    cash_type = db.Column(db.String(60), nullable = False)
    amount = db.Column(db.Integer, nullable = False)
    currency = db.Column(db.String(60), nullable = False)

    payrun_id = db.Column(db.Integer, db.ForeignKey('payrun.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('monthlyemployee.id'), nullable=False)

    def __repr__(self):
        return f"Monthly Pay Item('{self.pay_item}', '{self.tax_setting}', '{self.cash_type}', '{self.amount}', '{self.currency}', '{self.payrun_id}', '{self.employee_id}')" 

class PayRun(db.Model):
    __tablename__ = 'payrun'
    id = db.Column(db.Integer, primary_key = True)
    month = db.Column(db.String(60), nullable = False)
    year = db.Column(db.String(60), nullable = False)

    monthly_pay_items = db.relationship('MonthlyPayItem', backref='payrun', lazy=True)
    monthly_expats = db.relationship('MonthlyEmployee', backref='payrun', lazy=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    def __repr__(self):
        return f"PayRun('{self.month}', '{self.year}', '{self.company}')" 


class MonthlyEmployee(db.Model):
    __tablename__ = 'monthlyemployee'

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(60), nullable = False)
    last_name = db.Column(db.String(60), nullable = False)
    person_nummer = db.Column(db.Integer)
    skattetabell = db.Column(db.String(60), nullable = False)
    expat_type = db.Column(db.String(60), nullable = False)
    assign_start = db.Column(db.DateTime)
    assign_end = db.Column(db.DateTime)
    expert = db.Column(db.Boolean, nullable=False)
    sink = db.Column(db.Boolean, nullable=False)
    six_month_rule = db.Column(db.Boolean, nullable=False)
    social_security = db.Column(db.String(60), nullable = False)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    payrun_id = db.Column(db.Integer, db.ForeignKey('payrun.id'), nullable = False)
    monthly_pay_items = db.relationship('MonthlyPayItem', backref='monthlyemployee', lazy=True)
    monthly_result = db.relationship('MonthResult', backref='monthlyemployee', lazy=False)
    
    def __repr__(self):
        return f"Monthly Expat('{self.first_name}', '{self.last_name}','{self.person_nummer}','{self.expat_type}', '{self.assign_start}', '{self.assign_end}', '{self.expert}', '{self.sink}', '{self.six_month_rule}', '{self.social_security}', '{self.monthly_pay_items}', '{self.monthly_result}')"      

class MonthResult(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    net_items = db.Column(db.Integer)
    gross_items = db.Column(db.Integer)
    net_result = db.Column(db.Integer)
    total_gross = db.Column(db.Integer)
    gross_up = db.Column(db.Integer)
    tax = db.Column(db.Integer)
    tax_free = db.Column(db.Integer)
    expert_tax_free = db.Column(db.Integer)
    social_security_charges = db.Column(db.Integer)

    monthly_employee_id = db.Column(db.Integer, db.ForeignKey('monthlyemployee.id'), nullable = False)

    def __repr__(self):
        return f"Monthly Result('{self.net_items}')"