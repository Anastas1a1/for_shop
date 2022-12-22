from multiprocessing.sharedctypes import Value
import sqlite3
import requests
import pandas as pd
import os
import os.path





# def create_table(us_id):
#     fname = 'database/' + str(us_id) + '.db'
#     db = sqlite3.connect(fname)
#     sql = db.cursor()

#     sql.execute("""CREATE TABLE IF NOT EXISTS users (
#         us_name TEXT,
#         summa FLOAT,
#         currency TEXT,
#         rate FLOAT,
#         fee total FLOAT,
#         note TEXT
#         )""")
#     db.commit()
#     return fname, db, sql    

def get_names(us_id):
    # db, sql = create_table(us_id)
    fname = 'database/' + str(us_id) + '.db'
    if os.path.exists(fname) == False:
        return 0
    db = sqlite3.connect(fname)
    sql = db.cursor()

    # if os.path.exists(fname) == False:
    #     sql.execute("""CREATE TABLE IF NOT EXISTS users (
    #         us_name TEXT,
    #         summa FLOAT,
    #         currency TEXT,
    #         rate FLOAT,
    #         fee total FLOAT,
    #         note TEXT
    #         )""")
    #     db.commit()
    names_list = []
    # sql.execute("SELECT us_name FROM users;")
    # all_names = sql.fetchall()
    # print(all_names)
    for value in sql.execute("SELECT us_name FROM users"):
        # name = str(name).replace("('","").replace("',)","")
        # print(value[0])
        if value[0] not in names_list:
            names_list.append(value[0])

    db.close()
    print (names_list)
    return names_list


def new_transaction(us_id, transaction):
    fname = 'database/' + str(us_id) + '.db'
    db = sqlite3.connect(fname)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        us_name TEXT,
        summa FLOAT,
        currency TEXT,
        rate FLOAT,
        fee total FLOAT,
        note TEXT
        )""")
    db.commit()
    # db, sql = create_table(us_id)
    sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", transaction)
    db.commit()  
    
    sql.execute("SELECT * FROM users;")
    df = pd.read_sql_query("SELECT * FROM users;", db)
    df.to_excel(r'database/' + str(us_id) + '.xlsx', index=False)
    all_results = sql.fetchall()
    print(all_results)  
    db.close()
    # = dict(sorted(cond.items(), key = lambda item: item[1]))
    
    
def parse_rate(rate):
    try:
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        print (data['Valute'][rate]['Value'])  
        return data['Valute'][rate]['Value']
    except:   
        print("No currency rate")
        return 0      
    

def no_rate(us_id):
    fname = 'database/' + str(us_id) + '.db'
    if os.path.exists(fname) == False:
        return 0
    db = sqlite3.connect(fname)
    sql = db.cursor()   
    # rate_zero = []
    sql.execute("SELECT currency, summa FROM users where rate='0'")
    rate_zero = sql.fetchall()
    # for value in sql.execute("SELECT currency, summa FROM users where rate='0'"):
    #     if value[0] not in rate_zero:
    #         rate_zero.append(value[0])
    # print(rate_zero)  
    db.close()
    return rate_zero

def summary(us_id):
    names_list = get_names(us_id)
    if names_list == 0:
        print('Нет базы данных')
        return 0
    fname = 'database/' + str(us_id) + '.db'
    db = sqlite3.connect(fname)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS summary (
        us_name TEXT,
        summa FLOAT,
        currency TEXT,
        rate FLOAT,
        fee total FLOAT,
        note TEXT
        )""")
    db.commit()
    # db, sql = create_table(us_id)
    sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", transaction)
    db.commit()  
    
    sql.execute("SELECT * FROM users;")
    df = pd.read_sql_query("SELECT * FROM users;", db)
    df.to_excel(r'database/' + str(us_id) + '.xlsx', index=False)
    all_results = sql.fetchall()
    print(all_results)  
    db.close()
    
# parse_rate('EUR')
# transaction = ['Nastya01', '46282', 'RUB', '1', '123', '']
# new_transaction(12345678, transaction)    
    
# get_names(1065409295)
# new_rates = []
# rate_zero = no_rate(1065409295)
# print(rate_zero)
# for i in range(len(rate_zero)):
#     rate = float(input("Ввод курса для {}:  ".format(rate_zero[i][0])))
#     fee = rate*float(rate_zero[i][1])
#     new_rates.append({
#         'currency' : rate_zero[i][0],
#         'rate' : rate,
#         'fee' : fee
#     })

# print(new_rates)