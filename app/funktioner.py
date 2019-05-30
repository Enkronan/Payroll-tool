import csv
from datetime import date
import datetime
import time
import random

def previous_period():
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    
    result = lastMonth.strftime("%Y%m")
    
    return result

def current_period():
    today = datetime.date.today()
    result = today.strftime("%Y%m")

    return result


def apportion_standard(earn_start, earn_end, start, end):

    try:
        earn_start = datetime.datetime.strptime(earn_start, '%Y-%m-%d')
        earn_end = datetime.datetime.strptime(earn_end, '%Y-%m-%d')
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
    except:
        return "Not proper formatting"

    ## Calculate how many days the item was earned
    earning_days = (earn_end - earn_start).days

    # if person was in Sweden when earning started
    if (earn_start - start).days > 0:
        #if person came before earning start and left after earning end (i.e. 100% Sweden)
        if (earn_end - end).days < 0:
            procent = 1.00
        #Person was in sweden when started but left during the period    
        else:
            procent = (end-earn_start).days/earning_days

    #Person came and left during earnings period
    elif (start - earn_start).days > 0 and (end - earn_end).days < 0:
        procent = (end-start).days/earning_days
    
    #Person came during earning period and stayed whole period
    elif (start-earn_start).days > 0 and (end-earn_end).days > 0:
        procent = (earn_end-start).days / earning_days
    
    return {'procent': procent, 'earn_end': earn_end, 'earn_start': earn_start,'start':start, 'end':end, 'earnings days': earning_days}

#print(apportion_standard('2019-01-01','2019-05-01','2018-01-01','2019-04-21'))

def social_security_type(social_index):
    all_social = {}

    with open('socialavgifter.csv') as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")

        for row in tabeller:
            key, value = row[0], row[2]
            all_social[key] = value
    
    return all_social[social_index]

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

#print(apportion_expert(50000,50000))

'''
#Testcases
t1 = time.time()
print(apportion_standard('2018-01-01','2019-01-01','2017-03-03','2018-07-01')['procent'])
print(apportion_standard('2018-01-01','2019-01-01','2017-03-03','2019-07-01'))
print(apportion_standard('2018-01-01','2019-01-01','2018-03-03','2018-07-01'))
print(apportion_standard('2018-01-01','2019-01-01','2018-03-03','2019-07-01'))
t2 = time.time()

print(t2-t1)
'''

def calculate_SINK(expert, netto = 0, brutto = 0):
    procent = 0.25

    if not 1.00 >= expert >= 0.75:
        return "expert needs to be a value between 0.75 and 1.00"

    try:     
        if int(netto) and int(brutto):
            pass
    except:
        return "everything needs to be numbers"

    if netto > 0 :
        skatt = (brutto * expert * procent) + (netto/(1-(expert*procent))-netto)
        gross = (netto/(1-(expert*procent))-netto)
        brutto = brutto + netto + gross
    else:
        skatt = brutto * expert * procent

    return {'skatt': skatt, 'brutto': brutto, 'skattepliktigt': brutto*expert, 'skattefri': brutto*(1-expert), 'skattesats': skatt/(brutto*expert), 'expert': expert}
    

#print(calculate_SINK(0.75,77286,0))

def calculate_tax(år, tabell, expert, netto = 0, brutto = 0):
    
    if not 1.00 >= expert >= 0.75:
        return "expert needs to be a value between 0.75 and 1.00"

    try:     
        if int(år) and int(tabell) and int(netto) and int(brutto):
            pass
    except:
        return "everything needs to be numbers"

    with open('tabeller.csv') as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")

        for row in tabeller:
            if row[0] == år and row[2] == tabell:
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
    
    return {'skatt': skatt, 'brutto': brutto, 'skattepliktigt': brutto*expert, 'skattefri': brutto*(1-expert), 'skattesats': skatt/(brutto*expert), 'expert': expert, 'år': år, 'tabell': tabell}


#print(calculate_tax('2019','30',apportion_expert(50000,100000),150000,0))
'''
t1 = time.time()
for i in range(100):
    print(calculate_tax('2019','30',apportion_expert(50000,100000),random.randint(0,15000),random.randint(0,15000)))
t2 = time.time()
print(t2-t1)
'''

def socialavgifter(belopp, kod='0'):

    avgifter = 0

    try:
        belopp = int(belopp)
    except:
        return "belopp needs to be an int"

    with open('socialavgifter.csv') as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")

        for row in tabeller:
            if row[0] == kod:
                procent = float(row[2])
                avgifter = int(procent * belopp)

        return {'belopp': belopp, 'procent': procent, 'avgifter': avgifter, 'kod': kod}  


def onetimetax(år, expert, yearly_income, netto=0,brutto=0):

    if not 1.00 >= expert >= 0.75:
        return "expert needs to be a value between 0.75 and 1.00"

    with open('onetimetax.csv') as csvfile:
        tabeller = csv.reader(csvfile, delimiter=";")
        for row in tabeller:
            if row[0] == år:

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

    return {'skatt': skatt, 'brutto': brutto, 'skattepliktig': brutto * expert, 'skattefri': brutto * (1-expert), 'netto': netto, 'total yearly gross': yearly_income + brutto,'procent':procent, 'år': år}
'''
one = onetimetax('2019',0.75,1800000,77286,0)
print(one)
print(socialavgifter(one['skattepliktig']))





t1 = time.time()
for i in range(1000):
    print(onetimetax('2019',0.75,random.randint(0,1500000),random.randint(0,150000),random.randint(0,150000)))
t2 = time.time()
print(t2-t1)
'''
if __name__ == "__main__":
    '''
    func = input("Which function do you want to call? net_to_gross or skattetabell: ")

    if func == "skattetabell":
        år = input("Which tax table year?")
        tabell = input("Which tax table?")
        brutto = int(input("What gross amount?"))

        print(skattetabell(år,tabell,brutto))

    elif func == "net_to_gross":
        net = input("What net amount")
        percentage = input("What tax percentage")
        expert = bool(input("Expert? Provide True or False"))

        print(net_to_gross(net,percentage,expert))
    '''


    

