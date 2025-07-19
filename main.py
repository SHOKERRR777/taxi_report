import sqlite3
import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

bot = telebot.TeleBot('7572983938:AAHltoYubIPU9FD4UamicLHSFJ6fUQMXOQg') # Bot's token

user_status = {} # Статус пользователя

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Таблтица для регистрации пользователей
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            role TEXT NOT NULL,
            password TEXT
        )
    ''')
    
    # Таблица для просмотра водителем различной информации
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,                         # 'income' или 'expense'
            category TEXT,                              # 'order_payment', 'extra_payment' и т.д.
            amount REAL NOT NULL,                       # Сумма
            comment TEXT,                               # Комментарий
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   # Время    
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

init_db() # Вызываем таблицу бд

"""Функция, проверяющая роль пользователя (driver, administrator, None)"""
def check_user_role(telegram_id):
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        
        cur.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cur.fetchall()

        if result:
            return result[0] # Пользователь найден
        else:
            return None # Пользователь не найден

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    finally:
        cur.close()
        conn.close()

"""Обработчик команды start"""
@bot.message_handler(commands=['start'])
def menu_authorizen(message):
    markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_main.add(types.KeyboardButton("Регистрация"), types.KeyboardButton("Войти"))

    bot.send_message(message.chat.id, "Приветствую тебя, пользователь! Для начала работы пройди регистрацию или войди в систему", reply_markup=markup_main)

"""Регистрация пользователя"""
@bot.message_handler(func=lambda message: message.text == 'Регистрация')
def reqister_start(message):
    bot.send_message(message.chat.id, "Для регистрации сначала введите имя", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, register_password)

def register_password(message):
        user_name = message.text
        
        user_status[message.chat.id] = {
        "status": "registering",
        "username": message.text
        }
        
        bot.send_message(message.chat.id, "Теперь введите пароль")
        bot.register_next_step_handler(message, register_finish)

def register_finish(message):
    try:    
        user_name = user_status[message.chat.id]["username"]
        user_password = message.text
        
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = ?", (user_name,))
        db_info = cur.fetchall()

        # Проверяем, регестрировался ли раннее пользователь
        if db_info:
            bot.send_message(message.chat.id, 'Такой пользователь уже есть в таблице базы данных. Нажмите на кпопку "Войти"')
            return menu_authorizen(message)  
        else:
            cur.execute("INSERT INTO users (telegram_id, username, role, password) VALUES (?, ?, ?, ?)", 
                        (message.chat.id, user_name, 'driver', user_password))
            conn.commit()

            user_status[message.chat.id] = {
            "status": "logged_in",
            "username": user_name
            }

            bot.send_message(message.chat.id, "Регистрация прошла успешно!")
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except  IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    finally:
        cur.close()
        conn.close()

"""Вход от пользователя"""
@bot.message_handler(func=lambda message: message.text == "Войти")
def log_start(message):
    bot.send_message(message.chat.id, "Для входа в систему введите ваше имя", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, log_password)

def log_password(message):
    user_name = message.text

    user_status[message.chat.id] = {
        "status": "logging_in",
        "username": message.text
    }

    bot.send_message(message.chat.id, "Теперь введите пароль")
    bot.register_next_step_handler(message, log_finish)

def log_finish(message):
    try:    
        user_name = user_status[message.chat.id]["username"]
        user_password = message.text
        
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                    (user_name, user_password,))
        db_values = cur.fetchall()

        # Если совпадение было найдено
        if db_values:
            bot.send_message(message.chat.id, "Вы вошли в систему!")
                
            user_status[message.chat.id] = {
                "status": "logged_in",
                "username": user_name
            }
        else:
            bot.send_message(message.chat.id, "Такого пользователя нет в базе данных!")
            return menu_authorizen(message)

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    finally:
        cur.close()
        conn.close()

"""Регистрация админа"""
@bot.message_handler(func=lambda message: message.text == "feiwfwijfE[EAWFOPWEINPAP]fdw")
def registeradm_start(message):
    bot.send_message(message.chat.id, "Регистрация администратора. Введите имя")
    bot.register_next_step_handler(message, registeradm_password)

def registeradm_password(message):
    admin_name = message.text

    user_status[message.chat.id] = {
        "status": "registering",
        "username": message.text
        }
    
    bot.send_message(message.chat.id, "Отлично, теперь введите Ваш пароль")
    bot.register_next_step_handler(message, registeradm_finish)

def registeradm_finish(message, admin_name):
    try:
        admin_name = user_status[message.chat.id]["username"]
        admin_password = message.text

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = ?", (admin_name,))
        db_info = cur.fetchall()

        # Проверяем, регестрировался ли раннее пользователь
        if db_info:
            bot.send_message(message.chat.id, 'Такой администратор уже есть в таблице базы данных. Выполните вход')
            return menu_authorizen(message)  
        else:
            cur.execute("INSERT INTO users (telegram_id, username, role, password) VALUES (?, ?, ?, ?)", 
                        (message.chat.id, admin_name, 'administrator', admin_password))
            conn.commit()

            user_status[message.chat.id] = {
            "status": "logged_in",
            "username": admin_name
            }

            bot.send_message(message.chat.id, "Регистрация прошла успешно!")
            return admin_menu(message)
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except  IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    finally:
        cur.close()
        conn.close()
        
"""Вход от имени администратора"""
@bot.message_handler(func=lambda message: message.text == "fowqf[oFG[GEAWN[GNA[GWN[[gn]]")
def logadm_start(message):
    bot.send_message(message.chat.id, "Для входа в панель управления администратора нашите ваше имя")
    bot.register_next_step_handler(message, logadm_password)

def logadm_password(message):
    admin_name = message.text
    
    user_status[message.chat.id] = {
        "status": "logging_in",
        "username": message.text
    }

    bot.send_message(message.chat.id, "Отлично, теперь введите Ваш пароль")
    bot.register_next_step_handler(message, logadm_finish)

def logadm_finish(message, admin_name):
    try:
        admin_name = user_status[message.chat.id]["username"]
        admin_password = message.text

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                    (admin_name, admin_password,))
        db_values = cur.fetchall()

        # Если совпадение было найдено
        if db_values:
            bot.send_message(message.chat.id, "Вы вошли в систему!")
                
            user_status[message.chat.id] = {
                "status": "logged_in",
                "username": admin_name
            }
            
            return admin_menu(message)
        else:
            bot.send_message(message.chat.id, "Такого администратора нет в базе данных!")
            return menu_authorizen(message)

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
    finally:
        cur.close()
        conn.close()

"""Главное меню """
@bot.message_handler(func=lambda message: user_status.get(message.chat.id, {}).get('status') == 'logged_in')
def main_menu(message):
    role = check_user_role(message.chat.id)

    if role == "driver": 
        main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        main_markup.add(types.KeyboardButton("Доходы"), 
                       types.KeyboardButton("Расходы"), 
                       types.KeyboardButton("Статус"))

        bot.send_message(message.chat.id, 
                        "Вы находитесь в главном меню. Выберите раздел",
                        reply_markup=main_markup)
    elif role == "administrator":
        admin_menu(message) # Убрали return, просто вызываем функцию
    else:
        return None

"""Разделы для пользователей"""
@bot.message_handler(func=lambda message: message.text == "Доходы")
@bot.message_handler(func=lambda message: message.text == "Расходы")
@bot.message_handler(func=lambda message: message.text == "Статус")
def income(message):
    user_id = message.chat.id
    
    web_markup = InlineKeyboardMarkup()
    web_markup.add(InlineKeyboardButton(text="Зайти в web-приложение", 
                                        web_app=WebAppInfo(url=f"https://shokerrr777.github.io/taxi_report/?user_id={user_id}")))
    
    bot.send_message(message.chat.id, "Перейдите в web-приложение для дальнейших действий", reply_markup=web_markup)
    bot.send_message(reply_markup=ReplyKeyboardRemove())

"""Главное меню администратора"""
@bot.message_handler(None)
def admin_menu(message):
    user_id = message.chat.id
    
    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(InlineKeyboardButton(text="Зайти в web-приложение", 
                                          web_app=WebAppInfo(url=f"https://shokerrr777.github.io/taxi_report/?user_id={user_id}")))
    
    bot.send_message(message.chat.id, "Добро пожаловать в панель управления администратора! Для дальнейших действий перейдите в Web-приложение:",
                     reply_markup=admin_markup)
    bot.send_message(reply_markup=ReplyKeyboardRemove())

# Запуск нашей программы
if __name__ == "__main__":
    bot.polling(non_stop=True) # Для того, чтобы наша программа работа без остановки