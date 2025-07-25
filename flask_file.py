import sqlite3
import os

from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

user_status = {}

"""Определение роли пользователя и перенаправление его на определённую панель"""
@app.route('/')
def income():
    user_id = request.args.get('user_id')

    if not user_id:
        return "Доступ запрещён!", 403
    
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users")
        user_data = cur.fetchall()

        if not user_data:
            return "Пользователь не найден!", 404
        
        role = user_data[3]

        if role == 'driver':
            return redirect(url_for('driver_panel'))
        elif role == 'administrator':
            return redirect(url_for('admin_panel'))
        else:
            return render_template('index.html')
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    except TypeError as e:
        print(f"Ошибка типов данных: {e}")
    finally:
        cur.close()
        conn.close()

"""Панель водителя"""
@app.route('/driver')
def driver_panel():
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users")
        user_data = cur.fetchall()
        
        list_users = []
        for items in user_data:
            list_users.append({
                "id" : items[0],
                "telegram_id" : items[1],
                "username" : items[2],
                "role" : items[3],
                "password" : items[4],
            })
        
        cur.execute("SELECT * FROM transactions")
        trans_data = cur.fetchall()
        
        # Если в таблице с транзакциями нет ни единой данной
        if trans_data is None:
            return render_template('user_menu.html',  list_users=list_users)
        
        list_trans = []
        for items in trans_data:
            list_trans.append({
                "id" : items[0],
                "user_id" : items[1],
                "type" : items[2],
                "category" : items[3],
                "amount" : items[4],
                "comment" : items[5],
                "date" : items[6],
            })

        return render_template('administrator_menu.html', list_users=list_users, list_trans=list_trans)

    except sqlite3.Error as e:
        return f"Ошибка базы данных: {e}"
    except TypeError as e:
        return f"Ошибка с типами данных: {e}"
    except IOError as e:
        return f"Ошибка ввода/вывода: {e}"
    except Exception as e:
        return f"Ошибка: {e}"
    finally:
        cur.close()
        conn.close()

"""Панель администратора"""
@app.route('/administrator')
def admin_panel():
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users")
        user_data = cur.fetchall()
        
        list_users = []
        for items in user_data:
            list_users.append({
                "id" : items[0],
                "telegram_id" : items[1],
                "username" : items[2],
                "role" : items[3],
                "password" : items[4],
            })
        
        cur.execute("SELECT * FROM transactions")
        trans_data = cur.fetchall()
        
        # Если в таблице с транзакциями нет ни единой данной
        if trans_data is None:
            return render_template('administrator_menu.html',  list_users=list_users)
        
        list_trans = []
        for items in trans_data:
            list_trans.append({
                "id" : items[0],
                "user_id" : items[1],
                "type" : items[2],
                "category" : items[3],
                "amount" : items[4],
                "comment" : items[5],
                "date" : items[6],
            })

        return render_template('administrator_menu.html', list_users=list_users, list_trans=list_trans)

    except sqlite3.Error as e:
        return f"Ошибка базы данных: {e}"
    except TypeError as e:
        return f"Ошибка с типами данных: {e}"
    except IOError as e:
        return f"Ошибка ввода/вывода: {e}"
    except Exception as e:
        return f"Ошибка: {e}"
    finally:
        cur.close()
        conn.close()

# Запуск нашей программы
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)