from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_name = db.Column(db.String(60), unique = True, nullable = False)
    org_number = db.Column(db.String(60))
    permanent_establishment = db.Column(db.Boolean, nullable=False)
    expats = db.relationship('Employee', backref='employee', lazy=True)

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
    company = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)
    
    def __repr__(self):
        return f"Employee('{self.first_name}', '{self.last_name}','{self.person_nummer}', '{self.expat_type}', '{self.assign_start}', '{self.assign_end}', '{self.expert}', '{self.sink}', '{self.six_month_rule}', '{self.social_security}')"      

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')" 