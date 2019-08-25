import os
import re

from app.helpers import apology, login_required
from app.models import Post

from app import app, db
from app.models import User, Company, Employee, Post
from app.forms import AddCompany, AddEmployee, CalculateInitial
from app.funktioner import (apportion_expert, apportion_standard, calculate_SINK, calculate_tax_table, socialavgifter,
                        onetimetax, social_security_type, previous_period, current_period, start_calculation_logic)

from flask import flash, jsonify, redirect, session, url_for, render_template, request, Blueprint                        
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError


main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
@login_required
def home():

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page = 5)
    return render_template("home.html", posts = posts)
    

@main.route("/company",methods=["GET", "POST"])
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

@main.route("/employee",methods=["GET", "POST"])
@login_required
def employee():

    if request.method == "POST":

        session['employee'] = int(request.form.get('employee'))
           
        return redirect(url_for('main.calculate'))
    else:
        
        try: 
            get_company = Company.query.filter_by(company_name = session['current_company']).first().expats
        except:
            flash('You need to pick a company first!', 'danger')
            return redirect(url_for('main.company'))

        return render_template("employee.html", rows = get_company)

@main.route("/add_company", methods=["GET", "POST"])
@login_required
def add_company():

    form = AddCompany()
    if form.validate_on_submit():
        comp_to_add = Company(company_name = form.company_name.data, org_number = form.org_number.data, permanent_establishment = form.permanent_establishment.data) 

        db.session.add(comp_to_add)
        db.session.commit()

        session['current_company'] = form.company_name.data

        flash('the company has been created! You can now add employees', 'success')
        return redirect(url_for('main.add_employee'))

    return render_template("add_company.html", form=form, title='Company')

@main.route("/add_employee", methods=["GET", "POST"])
@login_required
def add_employee():

    form = AddEmployee()
    if form.validate_on_submit():

        try:
            current_company = Company.query.filter_by(company_name = session['current_company']).first().id
        except:
            flash('You need to pick a company first!', 'danger')
            return redirect(url_for('main.company'))

        emp_to_add = Employee(first_name = form.first_name.data, last_name = form.last_name.data, person_nummer = form.person_nummer.data, skattetabell = form.skattetabell.data, expat_type = form.expat_type.data, assign_start = form.assign_start.data, assign_end = form.assign_end.data, expert = form.expert.data, sink = form.sink.data, six_month_rule = form.six_month_rule.data, social_security = form.social_security.data, company = current_company) 

        db.session.add(emp_to_add)
        db.session.commit()

        flash('the employee has been added! You can now start calculating', 'success')
        return redirect(url_for('main.employee'))

    try:
        current_company = Company.query.filter_by(company_name = session['current_company']).first().company_name
    except:
        flash('You need to pick a company first!', 'danger')
        return redirect(url_for('main.company'))

    return render_template("add_employee.html", form=form, title='Employee', current_company = current_company)

@main.route("/calculate", methods=["GET", "POST"])
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
        return redirect(url_for('main.employee'))


    return render_template("calculate.html", employee = current_employee, company = current_company, SocialSecurity = social_security, form = form)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)