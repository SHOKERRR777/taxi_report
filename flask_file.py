import sqlite3
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

user_status = {}

@app.route('/{user_id}')
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
        
        # Функция для создания json-файла, в котором будет храниться информация о пользователе и его дейсвиях
        def user_json():
            # Формируем данные пользователя
            user_info = {
                'id' : user_data[0],
                'telegram_id' : user_data[1],
                'username' : user_data[2],
                'role' : user_data[3],
                'password' : user_data[4],
            }
            
            return jsonify(user_info) # Возвращает json-файл
        
        user_json() # Активируем функкцию

        if jsonify['role'] == 'driver':
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
        if jsonify['role'] == 'driver':
            return render_template('user_menu.html', list_transactions=list_transactions, user_info=jsonify)        
        elif jsonify['role'] == 'administrator':
            return render_template('administrator_menu.html', list_transactions=list_transactions, user_info=jsonify)
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    except TypeError as e:
        print(f"Ошибка типов данных: {e}")
    finally:
        cur.close()
        conn.close()

# Запуск нашей программы
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)