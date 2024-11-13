import sqlite3

def init_db():
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Candle INTEGER NOT NULL,
            Power INTEGER NOT NULL,
            price INTEGER NOT NULL,
            MovingAverage5 INTEGER NOT NULL,
            MovingAverage15 INTEGER NOT NULL,
            MovingAverage60 INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            Day INTEGER NULL,
            AI INTEGER NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sell (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Candle INTEGER NOT NULL,
            Power INTEGER NOT NULL,
            price INTEGER NOT NULL,
            MovingAverage5 INTEGER NOT NULL,
            MovingAverage15 INTEGER NOT NULL,
            MovingAverage60 INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            Day INTEGER NULL,
            AI INTEGER NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buy2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Candle INTEGER NOT NULL,
            Power INTEGER NOT NULL,
            price INTEGER NOT NULL,
            up_shadow INTEGER NOT NULL,
            down_shadow INTEGER NOT NULL,
            MovingAverage5 INTEGER NOT NULL,
            MovingAverage15 INTEGER NOT NULL,
            MovingAverage60 INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            Day INTEGER NULL,
            AI INTEGER NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sell2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Candle INTEGER NOT NULL,
            Power INTEGER NOT NULL,
            price INTEGER NOT NULL,
            up_shadow INTEGER NOT NULL,
            down_shadow INTEGER NOT NULL,
            MovingAverage5 INTEGER NOT NULL,
            MovingAverage15 INTEGER NOT NULL,
            MovingAverage60 INTEGER NOT NULL,
            ticket_in INTEGER NULL,
            ticket_out INTEGER NULL,
            comment TEXT NULL,
            result INTEGER NULL,
            Day INTEGER NULL,
            AI INTEGER NULL
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

def save_buy1(Candle, Power, price, MovingAverage5, MovingAverage15, MovingAverage60):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buy (Candle, Power, price, MovingAverage5, MovingAverage15, MovingAverage60)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (Candle, Power, price, MovingAverage5, MovingAverage15, MovingAverage60))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def save_sell1(Candle, Power, price, MovingAverage5, MovingAverage15, MovingAverage60):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sell (Candle, Power, price, MovingAverage5, MovingAverage15, MovingAverage60)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (Candle, Power, price, MovingAverage5, MovingAverage15, MovingAverage60))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def save_buy2(Candle, Power, price,up_shadow, down_shadow, MovingAverage5, MovingAverage15, MovingAverage60):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buy2 (Candle, Power, price, up_shadow, down_shadow, MovingAverage5, MovingAverage15, MovingAverage60)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (Candle, Power, price, up_shadow, down_shadow, MovingAverage5, MovingAverage15, MovingAverage60))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def save_sell2(Candle, Power, price,up_shadow, down_shadow, MovingAverage5, MovingAverage15, MovingAverage60):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sell2 (Candle, Power, price, up_shadow, down_shadow, MovingAverage5, MovingAverage15, MovingAverage60)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (Candle, Power, price, up_shadow, down_shadow, MovingAverage5, MovingAverage15, MovingAverage60))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def update_ticket_buy(transaction_id, comment, ticket_in, result_AI, Day):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE buy 
        SET ticket_in = ?, comment = ?, AI = ?, Day =?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, Day, transaction_id))
    conn.commit()
    conn.close()

def update_ticket_sell(transaction_id, comment, ticket_in, result_AI, Day):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE sell 
        SET ticket_in = ?, comment = ?, AI = ?, Day =?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, Day, transaction_id))
    conn.commit()
    conn.close()

def update_ticket_buy2(transaction_id, comment, ticket_in, result_AI, Day):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE buy2 
        SET ticket_in = ?, comment = ?, AI = ?, Day =?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, Day, transaction_id))
    conn.commit()
    conn.close()

def update_ticket_sell2(transaction_id, comment, ticket_in, result_AI, Day):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE sell2 
        SET ticket_in = ?, comment = ?, AI = ?, Day =?
        WHERE id = ? 
    ''', (ticket_in, comment, result_AI, Day, transaction_id))
    conn.commit()
    conn.close()

def update_result_buy(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE buy 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_result_sell(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE sell 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_result_buy2(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE buy2 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_result_sell2(result, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE sell2 
        SET result = ?
        WHERE ticket_in = ? 
    ''', (result, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_buy(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE buy 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_sell(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE sell 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_buy2(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE buy2 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def update_ticket_out_sell2(ticket_out, ticket_in):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE sell2 
        SET ticket_out = ?
        WHERE ticket_in = ? 
    ''', (ticket_out, ticket_in))
    conn.commit()
    conn.close()

def get_data_from_db(table_name):
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, Candle, Power, Price, MovingAverage5, MovingAverage15, MovingAverage60, Result, AI FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    return data
