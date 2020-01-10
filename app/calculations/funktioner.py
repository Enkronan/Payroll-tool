import csv
from datetime import date
import datetime
import os

from flask import session, current_app
from app.models import Employee

class Expat:
    def __init__(self, employee_object):
        self.skattetabell = employee_object.skattetabell
        self.expert = employee_object.expert
        self.sink = employee_object.sink
        self.six_month_rule = employee_object.six_month_rule
        self.social_security = employee_object.social_security
        self.monthly_pay_items = employee_object.monthly_pay_items
        self.net = 0
        self.gross = 0
        self.gross_up = 0
        self.tax = 0
        self.social_security_charges = 0
        self.tax_free = 0
        self.expert_tax_free = 0
        self.sink_rate = 0.25
        
        
    def social_security_type(self, social_security_charges):
        all_social_security_descriptions = {}

        script_dir = os.path.dirname(__file__)
        rel_path = "skatteverket\\socialavgifter.csv"
        abs_file_path = os.path.join(script_dir,rel_path)

        with open(abs_file_path) as csvfile:
            tabeller = csv.reader(csvfile, delimiter=";")

            for row in tabeller:
                key, value = row[0], row[2]
                all_social_security_descriptions[key] = value
        
        return all_social_security_descriptions[social_security_charges]

    def evaluate_pay_items(self):
        for item in self.monthly_pay_items:
            if item.cash_type == "Gross":
                self.gross += item.amount
            elif item.cash_type == "Net":
                self.net += item.amount

    def calculate_SINK(self):
        expert = self.expert
        netto = self.net
        brutto = self.gross
        tax_rate_sink = self.sink_rate

        if expert:
            expert = 0.75
        else:
            expert = 1

        if netto > 0 :
            skatt = (brutto * expert * tax_rate_sink) + (netto/(1-(expert*tax_rate_sink))-netto)
            gross = (netto/(1-(expert*tax_rate_sink))-netto)
            brutto = brutto + netto + gross
            self.tax += skatt
            self.gross_up += skatt
            self.expert_tax_free += brutto*(1-expert)
        else:
            skatt = brutto * expert * tax_rate_sink
            self.tax += skatt
            self.expert_tax_free += brutto*(1-expert)
            self.net += brutto*expert-skatt + brutto*(1-expert)

    def calculate_pay_items(self):
        self.calculate_SINK()

    def __str__(self):
        return "Skattetabell: {}, Expert: {}, SINK: {}, Net: {}, Gross: {}, Tax: {}, Expert Tax Free: {}".format(self.skattetabell, self.expert, self.sink, self.net, self.gross, self.tax, self.expert_tax_free)


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


    

def calculate_tax_table(tabell, expert, netto = 0, brutto = 0):
    
    script_dir = os.path.dirname(__file__)
    rel_path = "skatteverket\\tabeller.csv"
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
    rel_path = "skatteverket\\socialavgifter.csv"
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








    

