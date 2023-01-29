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
    fname = 'database/' + str(us_id) + 'transaction.db'
    if os.path.exists(fname) == False:
        return 0
    
    db = sqlite3.connect(fname)
    sql = db.cursor()
    
    names_list = []

    for value in sql.execute("SELECT us_name FROM users"):
        if value[0] not in names_list:
            names_list.append(value[0])
    db.close()
    print (names_list)
    return names_list

def get_prod(us_id):
    # db, sql = create_table(us_id)
    fname = 'database/' + str(us_id) + 'purchase.db'
    if os.path.exists(fname) == False:
        return 0
    db = sqlite3.connect(fname)
    sql = db.cursor()
    prod_list = []
    
    for value in sql.execute("SELECT title FROM products"):
        if value[0] not in prod_list:
            prod_list.append(value[0])
    db.close()
    print (prod_list)
    return prod_list

# def get_prod_from_users(us_id):
#     fname = 'database/' + str(us_id) + '.db'
#     if os.path.exists(fname) == False:
#         return 0
#     db = sqlite3.connect(fname)
#     sql = db.cursor()
#     prod_list = []
    
#     for value in sql.execute("SELECT title FROM products"):
#         if value[0] not in prod_list:
#             prod_list.append(value[0])
#     db.close()
#     print (prod_list)
#     return prod_list

def new_purchase(us_id, purchase):
    fname = 'database/' + str(us_id) + 'purchase.db'
    db = sqlite3.connect(fname)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS products (
        title TEXT,
        price FLOAT,
        amount FLOAT
        )""")
    db.commit()
    # db, sql = create_table(us_id)
    sql.execute(f"INSERT INTO products VALUES(?, ?, ?)", purchase)
    db.commit()  
    
    sql.execute("SELECT * FROM products;")
    df = pd.read_sql_query("SELECT * FROM products;", db)
    df.to_excel(r'database/' + str(us_id) + 'purchase.xlsx', index=False)
    all_results = sql.fetchall()
    print(all_results)  
    db.close()


def new_transaction(us_id, transaction):
    print(transaction)
    fname = 'database/' + str(us_id) + 'transaction.db'
    db = sqlite3.connect(fname)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        date_transaction TEXT,
        us_name TEXT,
        price FLOAT,
        currency TEXT,
        rate FLOAT,
        fee total FLOAT,
        commission TEXT
        )""")
    db.commit()
    # db, sql = create_table(us_id)
    
    sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)", transaction)
    db.commit()  
    
    sql.execute("SELECT * FROM users;")
    df = pd.read_sql_query("SELECT * FROM users;", db)
    df.to_excel(r'database/' + str(us_id) + 'transaction.xlsx', index=False)
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
    df.to_excel(r'database/' + str(us_id) + 'transaction.xlsx', index=False)
    all_results = sql.fetchall()
    print(all_results)  
    db.close()
  