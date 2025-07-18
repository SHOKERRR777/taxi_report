import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

user_status = {}

@app.route('/')
def income():
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM transactions")
        db_info = cur.fetchall()

        list_info = []
        list.append({
            "id" : db_info[0],
            "user_id" : db_info[1],
            "type" : db_info[2],
            "category" : db_info[3],
            "amount" : db_info[4],
            "comment" : db_info[5],
            'datetime' : db_info[6],
        })
        
        return render_template('', list_info=list_info)        

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