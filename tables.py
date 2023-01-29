import os
import os.path
import sqlite3
from multiprocessing.sharedctypes import Value

import pandas as pd
import requests


def get_names(us_id):
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


def new_purchase(us_id, purchase):
    fname = 'database/' + str(us_id) + 'purchase.db'
    db = sqlite3.connect(fname)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS products (
        title TEXT,
        price FLOAT,
        amount INTEGER
        )""")
    db.commit()
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
        title TEXT,
        price FLOAT,
        currency TEXT,
        rate FLOAT,
        fee total FLOAT,
        commission TEXT
        )""")
    db.commit()
    
    sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)", transaction)
    db.commit()  
    
    print('OK_commit')
    df = pd.read_sql_query("SELECT * FROM users", db)
    try:
        df.to_excel(r'database/' + str(us_id) + 'transaction.xlsx', index=False)
        all_results = sql.fetchall()
    except:
        print('excel not OK')
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
    fname = 'database/' + str(us_id) + 'transaction.db'
    if os.path.exists(fname) == False:
        return 0
    db = sqlite3.connect(fname)
    sql = db.cursor()   
    # rate_zero = []
    sql.execute("SELECT currency, summa FROM users where rate='0'")
    rate_zero = sql.fetchall()
    db.close()
    return rate_zero

def smeta_sellers(us_id):
    transaction = 'database/' + str(us_id) + 'transaction.db'
    if os.path.exists(transaction)==False:
        return 0
    
    db = sqlite3.connect(transaction)
    df = pd.read_sql_query("SELECT us_name, sum(fee), sum(commission) as sum FROM users GROUP BY us_name", db)
    df.to_excel(r'database/summ_commission.xlsx', index=False)
    db.close()
    return 'database/summ_commission.xlsx'

def smeta_sold_prod(us_id):
    #продано товаров
    transaction = 'database/' + str(us_id) + 'transaction.db'
    if os.path.exists(transaction)==False:
        return 0

    db = sqlite3.connect(transaction)
    df = pd.read_sql_query("SELECT title, count(title) as count from users GROUP BY title", db)
    df.to_excel(r'database/sold_prod.xlsx', index=False)
    db.close()
    return 'database/sold_prod.xlsx'
  
# def left_in_stock(us_id):  
#     #отсатки на складе
#     purchase = 'database/' + str(us_id) + 'purchase.db'   
#     x, df_sold_prod = smeta_sold_prod(us_id)
#     if os.path.exists(purchase)==False:
#         return 0 
#     db = sqlite3.connect(purchase)
#     sql = db.cursor()
    
#     sql.execute("SELECT title, sum(amount) as sum FROM products GROUP BY title")
#     db.commit()

#     df = pd.read_sql_query("SELECT * FROM products", db)
#     try:
#         df.to_excel(r'database/test_1.xlsx', index=False)
#         all_results = sql.fetchall()
#     except:
#         print('excel not OK')
#     print(all_results)  
#     # db.close()
#     print(df_sold_prod)
#     for rowind, row in df_sold_prod.iterrows():
#         for tit, s in row.items():
#             print(s)
#             # sql.execute("UPDATE products SET amount = (amount - ?) WHERE title = ?", (s+1, s))

#     db.commit()

#     df = pd.read_sql_query("SELECT * FROM products", db)
#     try:
#         df.to_excel(r'database/test_1.xlsx', index=False)
#         all_results = sql.fetchall()
#     except:
#         print('excel not OK')
#     print(all_results)             
            
#     df_have_prod = pd.read_sql_query("SELECT title, sum(amount) as sum FROM products GROUP BY title", db)
#     df_have_prod = df_have_prod.rename(columns={'sum': 'count'})
#     df_sold_prod = df_have_prod.rename(columns={'count': 'Продано'})
#     new_df = pd.merge(df_have_prod, df_sold_prod)
#     print(new_df)
     
     
#     db.close()
#     return 'database/lef_in_stock.xlsx'  
    
# #smeta_sold_prod('1065409295')
# left_in_stock(1065409295)