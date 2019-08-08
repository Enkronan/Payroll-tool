from app import app, db
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from app.helpers import apology, login_required, lookup
from app.models import User, Company, Employee, Post
from app.forms import RegistrationForm, LoginForm, AddCompany, AddEmployee, CalculateInitial, UpdateAccountForm, PostForm
from app.funktioner import apportion_expert, apportion_standard, calculate_SINK, calculate_tax_table, socialavgifter, onetimetax, social_security_type, previous_period, current_period, start_calculation_logic
from flask_login import login_user, current_user, logout_user

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import re

@app.route("/")
@login_required
def home():

    posts = Post.query.all()
    return render_template("home.html", posts = posts)
    

@app.route("/company",methods=["GET", "POST"])
@login_required
def company():

    if request.method == "POST":
        selected_company = request.form.get('company')

        get_company = Company.query.filter_by(company_name = selected_company).first()

        session['current_company'] = get_company.company_name

        return render_template("employee.html", rows = get_company.expats) 
    
    else:
        all_companies = Company.query.all()
        return render_template("company1.html", rows = all_companies)

@app.route("/employee",methods=["GET", "POST"])
@login_required
def employee():

    if request.method == "POST":

        session['employee'] = int(request.form.get('employee'))
           
        return redirect(url_for('calculate'))
    else:
        
        try: 
            get_company = Company.query.filter_by(company_name = session['current_company']).first().expats
        except:
            flash('You need to pick a company first!', 'danger')
            return redirect(url_for('company'))

        return render_template("employee.html", rows = get_company)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccesfull. Please check username and password', 'danger')

    return render_template("login1.html", title='Login', form=form)



@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():

        hash_1 = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        user = User(username = form.username.data, password = hash_1) 
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register1.html", title='Register', form=form)

@app.route("/add_company", methods=["GET", "POST"])
@login_required
def add_company():

    form = AddCompany()
    if form.validate_on_submit():
        comp_to_add = Company(company_name = form.company_name.data, org_number = form.org_number.data, permanent_establishment = form.permanent_establishment.data) 

        db.session.add(comp_to_add)
        db.session.commit()

        session['current_company'] = form.company_name.data

        flash('the company has been created! You can now add employees', 'success')
        return redirect(url_for('add_employee'))

    return render_template("add_company.html", form=form, title='Company')

@app.route("/add_employee", methods=["GET", "POST"])
@login_required
def add_employee():

    form = AddEmployee()
    if form.validate_on_submit():

        try:
            current_company = Company.query.filter_by(company_name = session['current_company']).first().id
        except:
            flash('You need to pick a company first!', 'danger')
            return redirect(url_for('company'))

        emp_to_add = Employee(first_name = form.first_name.data, last_name = form.last_name.data, person_nummer = form.person_nummer.data, skattetabell = form.skattetabell.data, expat_type = form.expat_type.data, assign_start = form.assign_start.data, assign_end = form.assign_end.data, expert = form.expert.data, sink = form.sink.data, six_month_rule = form.six_month_rule.data, social_security = form.social_security.data, company = current_company) 

        db.session.add(emp_to_add)
        db.session.commit()

        flash('the employee has been added! You can now start calculating', 'success')
        return redirect(url_for('employee'))

    try:
        current_company = Company.query.filter_by(company_name = session['current_company']).first().company_name
    except:
        flash('You need to pick a company first!', 'danger')
        return redirect(url_for('company'))

    return render_template("add_employee.html", form=form, title='Employee', current_company = current_company)

@app.route("/calculate", methods=["GET", "POST"])
@login_required
def calculate():

    form = CalculateInitial()

    if form.validate_on_submit():
        cash_amount = int(form.cash_amount.data)
        cash_type = form.cash_type.data

        if cash_type == 'Net':
            result = start_calculation_logic(cash_amount,0)
            return render_template("result.html", result = result)
        else:
            result = start_calculation_logic(0,cash_amount)
            return render_template("result.html", result = result)

    try:
        current_employee = Employee.query.get(session['employee'])
        current_company = Company.query.filter_by(company_name = session['current_company']).first()
        social_security = social_security_type(current_employee.social_security)
    except:
        flash('You need to pick an employee first!', 'danger')
        return redirect(url_for('employee'))


    return render_template("calculate.html", employee = current_employee, company = current_company, SocialSecurity = social_security, form = form)


@app.route("/logout")
@login_required
def logout():

    # Forget any user_id
    logout_user()

    # Redirect user to login form
    return redirect(url_for('home'))

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    form = UpdateAccountForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('your account has been updated!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username

    return render_template('account.html', title='Account', form = form)


@app.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():

    form = PostForm()
    if form.validate_on_submit():

        post = Post(title=form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('agenda.html', title='Agenda', form = form)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)