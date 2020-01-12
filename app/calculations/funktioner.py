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
        self.net_items = 0
        self.gross_items = 0
        self.net_benefits = 0
        self.gross_benefits = 0
        self.gross_up = 0
        self.tax = 0
        self.net_result = 0
        self.total_gross = 0
        self.social_security_charges = 0
        self.tax_free = 0
        self.expert_tax_free = 0

        self.monthly_employee_id = employee_object.id

        self.sink_rate = 0.25
        
    def social_security_type(self):
        all_social_security_descriptions = {}

        script_dir = os.path.dirname(__file__)
        rel_path = "skatteverket\\socialavgifter.csv"
        abs_file_path = os.path.join(script_dir,rel_path)

        with open(abs_file_path) as csvfile:
            tabeller = csv.reader(csvfile, delimiter=";")

            for row in tabeller:
                key, value = row[0], row[2]
                all_social_security_descriptions[key] = value
        
        return all_social_security_descriptions[self.social_security_charges]

    def evaluate_pay_items(self):
        for item in self.monthly_pay_items:
            if item.cash_type == "Gross" and item.tax_setting == "Cash":
                self.gross_items += item.amount
            elif item.cash_type == "Net" and item.tax_setting == "Cash":
                self.net_items += item.amount
            elif item.cash_type == "Gross" and item.tax_setting == "Benefit":
                self.gross_benefits += item.amount
            else:
                self.net_benefits += item.amount

    def calculate_SINK(self):
        expert = self.expert
        netto = self.net_items + self.net_benefits
        brutto = self.gross_items + self.gross_benefits
        tax_rate_sink = self.sink_rate

        if expert:
            expert = 0.75
        else:
            expert = 1

        if netto > 0:
            skatt = (brutto * expert * tax_rate_sink) + (netto/(1-(expert*tax_rate_sink))-netto)
            self.tax += int(skatt)
            self.gross_up += int(skatt)
        else:
            skatt = brutto * expert * tax_rate_sink
            self.tax += int(skatt)

    def calculate_tax_table(self):
    
        expert = self.expert
        netto = self.net_items + self.net_benefits
        brutto = self.gross_items + self.gross_benefits
        tabell = self.skattetabell
        
        script_dir = os.path.dirname(__file__)
        rel_path = "skatteverket\\tabeller.csv"
        abs_file_path = os.path.join(script_dir,rel_path)

        if expert:
            expert = 0.75
        else:
            expert = 1

        with open(abs_file_path) as csvfile:
            tabeller = csv.reader(csvfile, delimiter=";")

            for row in tabeller:
                if row[2] == tabell:
                    if netto > 0: 
                        if row[4] == '':
                            procent = int(row[5])/100
                            self.tax += int((brutto * expert * procent) + (netto/(1-(expert*procent))-netto))
                            self.gross_up = int((netto/(1-(expert*procent))-netto))
                            break

                        elif int(row[5]) < 100:
                            if int(row[3]) <= (brutto * expert) + expert*(netto/(1-(expert*(int(row[5])/100)))) <= int(row[4]):
                                procent = int(row[5])/100
                                self.tax += int((brutto * expert * procent) + (netto/(1-(expert*procent))-netto))
                                self.gross_up = int((netto/(1-(expert*procent))-netto))
                                break
                        else:
                            if int(row[3]) <= (brutto * expert) + expert*(netto/(1-(expert*(float(row[11])/100)))) <= int(row[4]):
                                procent = float(row[11])/100
                                self.tax = int((brutto * expert * procent) + (netto/(1-(expert*procent))-netto))
                                self.gross_up = int((netto/(1-(expert*procent))-netto))
                                break

                    else:
                        if int(row[3]) <= (brutto*expert) <= int(row[4]):
                            skatt = int(row[5])
                            if skatt < 100:
                                skatt = brutto*expert*(skatt/100)
                            self.tax += int(skatt)
                            break
        
        return 1
    
    def calculate_result(self):
        self.total_gross = int(self.gross_items + self.gross_up + self.net_items + self.gross_benefits + self.net_benefits)
        self.net_result = int(self.gross_items + self.gross_up + self.net_items - self.tax)
        self.expert_tax_free = int(self.total_gross * 0.25) if self.expert else 0 

    def calculate_pay_items(self):
        self.evaluate_pay_items()
        if self.sink:
            self.calculate_SINK()
        else:
            self.calculate_tax_table()
        self.calculate_result()
        
    def __str__(self):
        return "Skattetabell: {}, Expert: {}, SINK: {}, Net: {}, Total gross: {}, Tax: {}, Expert Tax Free: {}".format(self.skattetabell, self.expert, self.sink, self.net_result, self.total_gross, self.tax, self.expert_tax_free)


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








    

