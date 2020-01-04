import csv
from datetime import date
import datetime
import time
import random
import os

from flask import session, current_app
from app.models import Employee

def previous_period():
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    lastMonth = first_day_of_month - datetime.timedelta(days=1)
    
    result = lastMonth.strftime("%Y%m")
    
    return result

def current_period():
    today = datetime.date.today()
    result = today.strftime("%Y%m")

    return result


def apportion_standard(earn_start, earn_end, assignment_start, assignment_end):

    try:
        earn_start = datetime.datetime.strptime(earn_start, '%Y-%m-%d')
        earn_end = datetime.datetime.strptime(earn_end, '%Y-%m-%d')
        assignment_start = datetime.datetime.strptime(assignment_start, '%Y-%m-%d')
        assignment_end = datetime.datetime.strptime(assignment_end, '%Y-%m-%d')
    except:
        return "Not proper formatting"

    ## Calculate how many days the item was earned
    earning_days = (earn_end - earn_start).days

    # if person was in Sweden when earning started
    if (earn_start - assignment_start).days > 0:
        #if person came before earning assignment_start and left after earning assignment_end (i.e. 100% Sweden)
        if (earn_end - assignment_end).days < 0:
            procent = 1.00
        #Person was in sweden when started but left during the period    
        else:
            procent = (assignment_end-earn_start).days/earning_days

    #Person came and left during earnings period
    elif (assignment_start - earn_start).days > 0 and (assignment_end - earn_end).days < 0:
        procent = (assignment_end-assignment_start).days/earning_days
    
    #Person came during earning period and stayed whole period
    elif (assignment_start-earn_start).days > 0 and (assignment_end-earn_end).days > 0:
        procent = (earn_end-assignment_start).days / earning_days
    
    return {'procent': procent, 'earn_end': earn_end, 'earn_start': earn_start,'assignment_start':assignment_start, 'assignment_end':assignment_end,
             'earnings days': earning_days}

#print(apportion_standard('2019-01-01','2019-05-01','2018-01-01','2019-04-21'))

def social_security_type(social_index):
    all_social_security_descriptions = {}

    script_dir = os.path.dirname(__file__)
    rel_path = "socialavgifter.csv"
    abs_file_path = os.path.join(script_dir,rel_path)

    with open(abs_file_path) as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")

        for row in tabeller:
            key, value = row[0], row[2]
            all_social_security_descriptions[key] = value
    
    return all_social_security_descriptions[social_index]

#print(social_security_type('1A'))

def apportion_expert(expert,normal):
    
    standard_rate = 1.00
    expert_taxfree = 0.25
    
    try:
        if int(expert) and int(normal):
            pass
    except:
        return "needs to be integers"

    total = expert + normal
    apportion = expert/total
    
    calculated_expert = standard_rate - expert_taxfree * apportion

    return calculated_expert

def calculate_SINK(expert, netto = 0, brutto = 0):
    tax_rate_sink = 0.25

    if not 1.00 >= expert >= 0.75:
        return "expert needs to be a value between 0.75 and 1.00"

    try:     
        if int(netto) and int(brutto):
            pass
    except:
        return "everything needs to be numbers"

    if netto > 0 :
        skatt = (brutto * expert * tax_rate_sink) + (netto/(1-(expert*tax_rate_sink))-netto)
        gross = (netto/(1-(expert*tax_rate_sink))-netto)
        brutto = brutto + netto + gross
    else:
        skatt = brutto * expert * tax_rate_sink

    return {'skatt': skatt, 'brutto': brutto, 'skattepliktigt': brutto*expert, 'skattefri': brutto*(1-expert),
     'skattesats': skatt/(brutto*expert), 'expert': expert}
    

def calculate_tax_table(tabell, expert, netto = 0, brutto = 0):
    
    script_dir = os.path.dirname(__file__)
    rel_path = "tabeller.csv"
    abs_file_path = os.path.join(script_dir,rel_path)

    if not 1.00 >= expert >= 0.75:
        return "expert needs to be a value between 0.75 and 1.00"

    try:     
        if int(tabell) and int(netto) and int(brutto):
            pass
    except:
        return "everything needs to be numbers"

    if netto < 1 and brutto < 1:
            return {'skatt': 0, 'brutto': 0, 'skattepliktigt': 0, 'skattefri': 0, 'skattesats': 0}

    with open(abs_file_path) as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")

        for row in tabeller:
            if row[2] == tabell:
                if netto > 0: 
                    if row[4] == '':
                        procent = int(row[5])/100
                        skatt = (brutto * expert * procent) + (netto/(1-(expert*procent))-netto)
                        gross = (netto/(1-(expert*procent))-netto)
                        brutto = brutto + netto + gross
                        break

                    elif int(row[5]) < 100:
                        if int(row[3]) <= (brutto * expert) + expert*(netto/(1-(expert*(int(row[5])/100)))) <= int(row[4]):
                            procent = int(row[5])/100
                            skatt = (brutto * expert * procent) + (netto/(1-(expert*procent))-netto)
                            gross = (netto/(1-(expert*procent))-netto)
                            brutto = brutto + netto + gross
                            break
                    else:
                        if int(row[3]) <= (brutto * expert) + expert*(netto/(1-(expert*(float(row[11])/100)))) <= int(row[4]):
                            procent = float(row[11])/100
                            skatt = (brutto * expert * procent) + (netto/(1-(expert*procent))-netto)
                            gross = (netto/(1-(expert*procent))-netto)
                            brutto = brutto + netto + gross
                            break

                else:
                    if int(row[3]) <= (brutto*expert) <= int(row[4]):
                        skatt = int(row[5])
                        if skatt < 100:
                            skatt = int(brutto*expert) * (skatt/100)
                        break
    
    return {'skatt': skatt, 'brutto': brutto, 'skattepliktigt': brutto*expert, 'skattefri': brutto*(1-expert), 'skattesats': skatt/(brutto*expert)}


def socialavgifter(belopp, kod='0'):

    avgifter = 0

    script_dir = os.path.dirname(__file__)
    rel_path = "socialavgifter.csv"
    abs_file_path = os.path.join(script_dir,rel_path)
    
    try:
        belopp = int(belopp)
    except:
        return "belopp needs to be an int"

    with open(abs_file_path) as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")

        for row in tabeller:
            if row[0] == kod:
                procent = float(row[2])
                avgifter = int(procent * belopp)

        return {'procent': procent, 'avgifter': avgifter}  


def onetimetax(expert, yearly_income, netto=0,brutto=0):

    script_dir = os.path.dirname(__file__)
    rel_path = "onetimetax.csv"
    abs_file_path = os.path.join(script_dir,rel_path)

    if not 1.00 >= expert >= 0.75:
        return "expert needs to be a value between 0.75 and 1.00"

    with open(abs_file_path) as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")
        for row in tabeller:
            if netto > 0:
                if row[2] == '':
                    procent = int(row[3])/100
                    skatt = (brutto * expert * procent) + (netto/(1-(expert*procent))-netto)
                    gross = (netto/(1-(expert*procent))-netto)
                    brutto = brutto + netto + gross
                    break

                elif int(row[1]) <= yearly_income + (brutto*expert) + netto/(1-(expert*(int(row[3])/100))) <= int(row[2]):
                    procent = int(row[3])/100
                    skatt = (brutto*expert * procent) + (netto/(1-(expert*procent))-netto)
                    gross = (netto/(1-(expert*procent))-netto)
                    brutto = brutto + netto + gross
                    break
            else:
                if row[2] == '':
                    procent = int(row[3])/100
                    skatt = brutto* expert * procent
                    brutto = brutto
                    break

                elif int(row[1]) <= yearly_income + (brutto * expert) <= int(row[2]):
                    procent = int(row[3])/100
                    skatt = brutto * expert * procent
                    brutto = brutto
                    break

    return {'skatt': skatt, 'brutto': brutto, 'skattepliktigt': brutto * expert, 'skattefri': brutto * (1-expert),
     'netto': netto, 'total yearly gross': yearly_income + brutto,'procent':procent}



def start_calculation_logic(netto=0,brutto=0):
    current_employee = Employee.query.get(session['employee'])

    if current_employee.expert == False:
        expert = 1.00
    else:
        expert = 0.75

    if current_employee.sink == True:
        result_of_calculation = calculate_SINK(expert,netto,brutto)
        social_security_charges = socialavgifter(result_of_calculation['skattepliktigt'],current_employee.social_security)
        result_of_calculation["avgifter"] = social_security_charges["avgifter"]
    else:
        result_of_calculation = calculate_tax_table(current_employee.skattetabell,expert,netto,brutto)
        social_security_charges = socialavgifter(result_of_calculation['skattepliktigt'],current_employee.social_security)
        result_of_calculation["avgifter"] = social_security_charges["avgifter"]

    return result_of_calculation





    

