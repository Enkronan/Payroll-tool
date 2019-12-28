from app.models import Company, Employee, PayItem
from app import db, login_manager

def addEmployees():
    employee1 = Employee(first_name = "Robin", last_name = "Moe",person_nummer = "9210160000",skattetabell = '29', expat_type = "Outbound", social_security = "1A")

    db.session.add(employee1)
    db.session.commit()

