import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

user_status = {}

@app.route('/')
def income():
    user_id = request.args.get('user_id')

    if not user_id:
        return "Доступ запрещён!", 403
    
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
        user_data = cur.fetchall()

        if not user_data:
            return "Пользователь не найден!", 404
        
        # Формируем данные пользователя
        user_info = {
            'id' : user_data[0],
            'telegram_id' : user_data[1],
            'username' : user_data[2],
            'role' : user_data[3],
            'password' : user_data[4]
        }
        
        if user_info['role'] == 'driver':
            cur.execute("SELECT * FROM transactions WHERE telegram_id = ?", (user_id,))
        else:
            cur.execute("SELECT * FROM transactions")
        
        db_info = cur.fetchall()
        list_transactions = [] # Список, хранящий всю информацию о таблице Транзакции
        list_transactions.append({
            "id" : db_info[0],
            "user_id" : db_info[1],
            "type" : db_info[2],
            "category" : db_info[3],
            "amount" : db_info[4],
            "comment" : db_info[5],
            'datetime' : db_info[6],
        })

        # Для каждого пользователя сделаем отдельное окно
        if user_info['role'] == 'driver':
            return render_template('user_menu.html', list_transactions=list_transactions, user_info=user_info)        
        elif user_info['role'] == 'administrator':
            return render_template('administrator_menu.html', list_transactions=list_transactions, user_info=user_info)
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    finally:
        cur.close()
        conn.close()

# Запуск нашей программы
if __name__ == "__main__":
    app.run(debug=True)