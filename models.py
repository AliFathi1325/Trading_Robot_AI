import sqlite3

def init_db():
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BUYBUY (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            candle INTEGER NOT NULL,
            power INTEGER NOT NULL,
            close INTEGER NOT NULL,
            up_shadow INTEGER NOT NULL,
            down_shadow INTEGER NOT NULL,
            price_map INTEGER NOT NULL,
            moving15 INTEGER NOT NULL,
            moving30 INTEGER NOT NULL,
            moving45 INTEGER NOT NULL,
            moving60 INTEGER NOT NULL,
            macd INTEGER NOT NULL,
            adx INTEGER NOT NULL,
            rsi INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            resultAI INTEGER NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SELLSELL (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            candle INTEGER NOT NULL,
            power INTEGER NOT NULL,
            close INTEGER NOT NULL,
            up_shadow INTEGER NOT NULL,
            down_shadow INTEGER NOT NULL,
            price_map INTEGER NOT NULL,
            moving15 INTEGER NOT NULL,
            moving30 INTEGER NOT NULL,
            moving45 INTEGER NOT NULL,
            moving60 INTEGER NOT NULL,
            macd INTEGER NOT NULL,
            adx INTEGER NOT NULL,
            rsi INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            resultAI INTEGER NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BUYSELL (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            candle INTEGER NOT NULL,
            power INTEGER NOT NULL,
            close INTEGER NOT NULL,
            up_shadow INTEGER NOT NULL,
            down_shadow INTEGER NOT NULL,
            price_map INTEGER NOT NULL,
            moving15 INTEGER NOT NULL,
            moving30 INTEGER NOT NULL,
            moving45 INTEGER NOT NULL,
            moving60 INTEGER NOT NULL,
            macd INTEGER NOT NULL,
            adx INTEGER NOT NULL,
            rsi INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            resultAI INTEGER NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SELLBUY (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            candle INTEGER NOT NULL,
            power INTEGER NOT NULL,
            close INTEGER NOT NULL,
            up_shadow INTEGER NOT NULL,
            down_shadow INTEGER NOT NULL,
            price_map INTEGER NOT NULL,
            moving15 INTEGER NOT NULL,
            moving30 INTEGER NOT NULL,
            moving45 INTEGER NOT NULL,
            moving60 INTEGER NOT NULL,
            macd INTEGER NOT NULL,
            adx INTEGER NOT NULL,
            rsi INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            resultAI INTEGER NULL
        )
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_user(username, email, password):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', (username, email, password))
    conn.commit()
    conn.close()
    
def login_user(username, password):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def save_buy_buy(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO BUYBUY (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def save_sell_sell(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO SELLSELL (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def save_buy_sell(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO BUYSELL (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def save_sell_buy(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO SELLBUY (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def update_ticket_buy(transaction_id, comment, ticket_in, result_AI):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE BUYBUY 
        SET ticket_in = ?, comment = ?, resultAI = ?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, transaction_id))
    conn.commit()
    conn.close()

def update_ticket_sell(transaction_id, comment, ticket_in, result_AI):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE SELLSELL 
        SET ticket_in = ?, comment = ?, resultAI = ?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, transaction_id))
    conn.commit()
    conn.close()

def update_ticket_buy2(transaction_id, comment, ticket_in, result_AI):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE SELLBUY  
        SET ticket_in = ?, comment = ?, resultAI = ?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, transaction_id))
    conn.commit()
    conn.close()

def update_ticket_sell2(transaction_id, comment, ticket_in, result_AI):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE BUYSELL 
        SET ticket_in = ?, comment = ?, resultAI = ?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, transaction_id))
    conn.commit()
    conn.close()

def update_result_buy(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE BUYBUY 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_result_sell(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE SELLSELL 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_result_buy2(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE BUYSELL 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_result_sell2(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE SELLBUY 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_buy(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE BUYBUY 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_sell(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE SELLSELL  
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_buy2(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE BUYSELL 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_sell2(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE SELLBUY 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def get_data_from_db(table_name):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, Candle, Power, Price, MovingAverage5, MovingAverage15, MovingAverage60, Result, resultAI FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    return data
