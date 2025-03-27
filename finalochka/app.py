from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor
from sympy import public
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import traceback
import string
import random
from flask_mail import Mail, Message 
from dotenv import load_dotenv
import logging
### библиотеки ↑↑↑

app = Flask(__name__)
app.secret_key = 'Секретный ключ моего компьютера это - *******************************'
DB_NAME = "schedulehah"
DB_USER = "postgres"
DB_PASSWORD = "123"
DB_HOST = "localhost"
app.config['SESSION_PERMANENT'] = False


load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')

# порты протоколы 
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_SSL_PORT'] = int(os.getenv('MAIL_SSL_PORT', 465))

# флаги протоколов для включения
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'

# SMTP аутентификация и отправитель
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_APP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
# лог
print(f"Using MAIL_PORT: {app.config['MAIL_PORT']}, USE_TLS: {app.config['MAIL_USE_TLS']}, USE_SSL: {app.config['MAIL_USE_SSL']}")

mail = Mail(app)

verification_codes = {}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#avatrki
app.config['AVATAR_UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'avatars')
app.config['AVATAR_ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
#новости картинки
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['NEWS_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'news_images')
os.makedirs(app.config['NEWS_UPLOAD_FOLDER'], exist_ok=True)
#Уведомления о GET
# @app.before_request
# def log_request():
#     print("Получен запрос на:", request.path)
#парамс
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        cursor_factory=RealDictCursor
    )
def ensure_upload_folder():
    if not os.path.exists(app.config['NEWS_UPLOAD_FOLDER']):
        os.makedirs(app.config['NEWS_UPLOAD_FOLDER'])
        print(f"Создана папка: {app.config['NEWS_UPLOAD_FOLDER']}")

def shorten_text(text, max_words=15):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return text

#РАСПИСАНИЕ И ВСЕ С НИМ СВЯЗУЮЩЕЕ --------------------------------------------------------------------------------------------------------
# обновление расписании
@app.route('/archive', methods=['GET'])
def view_archive():
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, group_number, day, subject, start_time, end_time, created_at 
            FROM schedule_archive
            ORDER BY created_at DESC;
        """)
        archive_data = cur.fetchall()

        # Лог данных на этапе извлечения
        print("Данные из архива (fetchall):", archive_data)

        if not archive_data:
            print("Архив пуст!")
        else:
            print("Архив содержит записи:", archive_data)

        # Преобразование данных списка
        columns = [desc[0] for desc in cur.description]
        archive_data = [dict(zip(columns, row)) for row in archive_data]

        print("Преобразованные данные архива:", archive_data)

        return render_template('archive.html', archive_data=archive_data)

    except Exception as e:
        # add_notification(f'Ошибка при загрузке архива: {str(e)}', 'error')
        return redirect(url_for('schedule'))

    finally:
        cur.close()
        conn.close()




@app.route('/restore/<int:archive_id>', methods=['POST'])
def restore_schedule(archive_id):
    """Восстановление записи из архива в основное расписание"""
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('view_archive'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # перенос записи из schedule_archive в schedule
        cur.execute("""
            INSERT INTO schedule (group_number, day, subject, start_time, end_time, created_at)
            SELECT group_number, day, subject, start_time, end_time, created_at
            FROM schedule_archive
            WHERE id = %s
            RETURNING id;
        """, (archive_id,))

        restored_id = cur.fetchone()

        # удаление записи
        cur.execute("DELETE FROM schedule_archive WHERE id = %s;", (archive_id,))
        conn.commit()

        if restored_id:
            add_notification('Запись успешно восстановлена.', 'success')
        else:
            add_notification('Ошибка при восстановлении записи.', 'error')

    except Exception as e:
        conn.rollback()
        add_notification(f'Ошибка при восстановлении записи: {str(e)}', 'error')

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('view_archive'))



@app.route('/delete_forever/<int:archive_id>', methods=['POST'])
def delete_forever(archive_id):
    """Полное удаление записи из архива"""
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('view_archive'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Полное удаление записи
        cur.execute("DELETE FROM schedule_archive WHERE id = %s;", (archive_id,))
        conn.commit()

        add_notification('Запись успешно удалена навсегда.', 'success')

    except Exception as e:
        conn.rollback()
        add_notification(f'Ошибка при удалении записи: {str(e)}', 'error')

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('view_archive'))

#инициализация расписания из бд
def initialize_schedule():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Очистка таблицы перед вставкой (опционально)
        cur.execute("TRUNCATE TABLE schedule RESTART IDENTITY;")

        # Подготовка данных для вставки
        schedule_data = []

        # Группы с утренним расписанием (2301-2305)
        morning_groups = ['2301', '2302', '2303', '2304', '2305']
        morning_schedule = [
            ('database', '8:00', '9:30', 'Понедельник'),
            ('chemistry', '9:50', '11:20', 'Понедельник'),
            ('information communication technology', '11:30', '13:00', 'Понедельник'),
            ('physical education', '8:00', '9:30', 'Вторник'),
            ('social education', '9:50', '11:20', 'Вторник'),
            ('programm enginering', '11:30', '13:00', 'Вторник'),
            ('history', '8:00', '9:30', 'Среда'),
            ('python', '9:50', '11:20', 'Среда'),
            ('database', '11:30', '13:00', 'Среда'),
            ('database', '8:00', '9:30', 'Четверг'),
            ('information communication technology', '9:50', '11:20', 'Четверг'),
            ('python', '11:30', '13:00', 'Четверг'),
            ('english', '8:00', '9:30', 'Пятница'),
            ('python', '9:50', '11:20', 'Пятница'),
            ('economy', '11:30', '13:00', 'Пятница')
        ]

        # Группы с дневным расписанием (2306-2310)
        afternoon_groups = ['2306', '2307', '2308', '2309', '2310']
        afternoon_schedule = [
            ('database', '13:30', '15:00', 'Понедельник'),
            ('chemistry', '15:20', '16:50', 'Понедельник'),
            ('information communication technology', '17:00', '18:30', 'Понедельник'),
            ('physical education', '13:30', '15:00', 'Вторник'),
            ('social education', '15:20', '16:50', 'Вторник'),
            ('programm enginering', '17:00', '18:30', 'Вторник'),
            ('history', '13:30', '15:00', 'Среда'),
            ('python', '15:20', '16:50', 'Среда'),
            ('database', '17:00', '18:30', 'Среда'),
            ('database', '13:30', '15:00', 'Четверг'),
            ('information communication technology', '15:20', '16:50', 'Четверг'),
            ('python', '17:00', '18:30', 'Четверг'),
            ('english', '13:30', '15:00', 'Пятница'),
            ('python', '15:20', '16:50', 'Пятница'),
            ('economy', '17:00', '18:30', 'Пятница')
        ]

        # Формирование списка всех записей
        for group in morning_groups:
            for subj, start, end, day in morning_schedule:
                schedule_data.append((group, subj, start, end, day))

        for group in afternoon_groups:
            for subj, start, end, day in afternoon_schedule:
                schedule_data.append((group, subj, start, end, day))

        # Массовая вставка данных
        cur.executemany("""
            INSERT INTO schedule (group_number, subject, start_time, end_time, day)
            VALUES (%s, %s, %s::time, %s::time, %s)
        """, schedule_data)

        conn.commit()
        print("Расписание успешно инициализировано")

    except Exception as e:
        print(f"Ошибка при инициализации расписания: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

# Добавления расписания то есть новой записи
@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    # Проверяем, авторизован ли пользователь и является ли он администратором
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))

    try:
        # Получаем данные из формы
        group = request.form.get('group_number', '').strip()
        day = request.form.get('day', '').strip()
        subject = request.form.get('subject', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()

        app.logger.info(f"Полученные данные: group_number={group}, day={day}, subject={subject}, start_time={start_time}, end_time={end_time}")

        # Проверяем, что все обязательные поля заполнены
        if not all([group, day, subject, start_time, end_time]):
            app.logger.error("Не все поля заполнены.")
            add_notification('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('schedule'))

        # Проверяем корректность номера группы
        valid_groups = {'2301', '2302', '2303', '2304', '2305', '2306', '2307', '2308', '2309', '2310'}
        if group not in valid_groups:
            app.logger.error("Некорректный номер группы.")
            add_notification('Некорректный номер группы.', 'error')
            return redirect(url_for('schedule'))

        # Проверяем корректность дня недели
        valid_days = {'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'}
        if day not in valid_days:
            app.logger.error("Некорректный день недели.")
            add_notification('Некорректный день недели.', 'error')
            return redirect(url_for('schedule'))

        # Проверяем формат времени
        try:
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            app.logger.error("Некорректный формат времени.")
            add_notification('Некорректный формат времени. Используйте HH:MM.', 'error')
            return redirect(url_for('schedule'))

        # Проверяем, что время начала меньше времени окончания
        if start_time >= end_time:
            app.logger.error("Время начала должно быть меньше времени окончания.")
            add_notification('Время начала должно быть меньше времени окончания.', 'error')
            return redirect(url_for('schedule'))

        # Подключаемся к базе данных
        conn = get_db_connection()
        cur = conn.cursor()

        # Проверяем наличие конфликта расписания
        cur.execute(
            """
            SELECT COUNT(*) 
            FROM schedule 
            WHERE group_number = %s 
            AND day = %s 
            AND ((start_time <= %s AND end_time > %s) 
                OR (start_time < %s AND end_time >= %s)
                OR (start_time >= %s AND end_time <= %s))
            """,
            (group, day, start_time, start_time, end_time, end_time, start_time, end_time)
        )

        result = cur.fetchone()

        # Если результат словарь, обращаемся к ключу
        if result and ('count' in result and result['count'] > 0):  # для DictCursor
            app.logger.error("Конфликт времени: в это время уже есть занятие.")
            add_notification('Конфликт времени: в это время уже есть занятие.', 'error')
            return redirect(url_for('schedule'))

        # Если результат кортеж, обращаемся по индексу
        if result and isinstance(result, tuple) and result[0] > 0:
            app.logger.error("Конфликт времени: в это время уже есть занятие.")
            add_notification('Конфликт времени: в это время уже есть занятие.', 'error')
            return redirect(url_for('schedule'))



        # Вставляем новое расписание
        cur.execute(
            """
            INSERT INTO schedule (group_number, day, subject, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (group, day, subject, start_time, end_time)
        )

        if cur.rowcount == 0:
            app.logger.error("Запись не была добавлена. Проверьте запрос и данные.")
            add_notification('Не удалось добавить расписание.', 'error')
        else:
            conn.commit()
            app.logger.info("Добавлена новая запись расписания.")
            add_notification('Расписание успешно добавлено.', 'success')

    except Exception as e:
        app.logger.error(f"Ошибка при добавлении расписания: {str(e)}", exc_info=True)
        if 'conn' in locals():
            conn.rollback()
        add_notification(f'Ошибка при добавлении расписания: {str(e)}', 'error')

    finally:
        if 'conn' in locals():
            conn.close()

    return redirect(url_for('schedule'))

@app.route('/start', methods=['GET'])
def start():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT title, content, image FROM news ORDER BY created_at DESC LIMIT 5")
        latest_news = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('start.html', latest_news=latest_news)
    except Exception as e:
        print(traceback.format_exc())
        return render_template('start.html', latest_news=[])


#удаление расп
@app.route('/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO schedule_archive (group_number, day, subject, start_time, end_time, created_at)
            SELECT group_number, day, subject, start_time, end_time, created_at
            FROM schedule
            WHERE id = %s;
        """, (schedule_id,))


        # Удаление записи из основной таблицы
        cur.execute("DELETE FROM schedule WHERE id = %s;", (schedule_id,))
        conn.commit()

        add_notification('Запись успешно перемещена в архив.', 'success')
    except Exception as e:
        conn.rollback()
        add_notification(f'Ошибка при удалении записи: {str(e)}', 'error')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('schedule'))


#добавление группы расписания
@app.route('/add_group_schedule', methods=['POST'])
def add_group_schedule():
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))
    
    try:
        # получении из бд
        group = request.form.get('group')
        day = request.form.get('day')
        subject = request.form.get('subject')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if not all([group, day, subject, start_time, end_time]):
            add_notification('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('schedule'))

        valid_groups = ['2301', '2302', '2303', '2304', '2305', '2306', '2307', '2308', '2309', '2310']
        if group not in valid_groups:
            add_notification('Некорректный номер группы.', 'error')
            return redirect(url_for('schedule'))

        valid_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        if day not in valid_days:
            add_notification('Некорректный день недели.', 'error')
            return redirect(url_for('schedule'))

        conn = get_db_connection()
        cur = conn.cursor()
        
        # проверка временных конфликтов
        cur.execute("""
            SELECT * FROM schedule 
            WHERE group_number = %s 
            AND day = %s 
            AND ((start_time <= %s AND end_time >= %s) 
                OR (start_time <= %s AND end_time >= %s));
        """, (group, day, start_time, start_time, end_time, end_time))
        
        if cur.fetchone():
            add_notification('Конфликт времени для данной группы.', 'error')
            return redirect(url_for('schedule'))

        # ввод новых расписаний
        cur.execute("""
            INSERT INTO schedule (group_number, day, subject, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (group, day, subject, start_time, end_time))
        
        new_schedule_id = cur.fetchone()['id']
        conn.commit()
        
        add_notification('Расписание успешно добавлено.', 'success')
        return redirect(url_for('schedule'))

    except psycopg2.Error as e:
        if 'conn' in locals():
            conn.rollback()
        add_notification(f'Ошибка базы данных: {str(e)}', 'error')
        return redirect(url_for('schedule'))
    
    except Exception as e:
        add_notification(f'Произошла ошибка: {str(e)}', 'error')
        return redirect(url_for('schedule'))
    
    finally:
        if 'conn' in locals():
            conn.close()

# редакт расписания
@app.route('/edit_schedule/<int:schedule_id>', methods=['POST'])
def edit_schedule(schedule_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))
    
    try:
        group = request.form.get('group')
        day = request.form.get('day')
        subject = request.form.get('subject')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if not all([group, day, subject, start_time, end_time]):
            add_notification('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('schedule'))

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM schedule 
            WHERE group_number = %s 
            AND day = %s 
            AND id != %s
            AND ((start_time <= %s AND end_time >= %s) 
                OR (start_time <= %s AND end_time >= %s));
        """, (group, day, schedule_id, start_time, start_time, end_time, end_time))
        
        if cur.fetchone():
            add_notification('Конфликт времени для данной группы.', 'error')
            return redirect(url_for('schedule'))

        cur.execute("""
            UPDATE schedule 
            SET group_number = %s, day = %s, subject = %s, start_time = %s, end_time = %s
            WHERE id = %s;
        """, (group, day, subject, start_time, end_time, schedule_id))
        
        conn.commit()
        add_notification('Расписание успешно обновлено.', 'success')
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        add_notification(f'Ошибка при обновлении расписания: {str(e)}', 'error')
    
    finally:
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('schedule'))

#Само расписание то есть видимая часть
@app.route('/schedule')
def schedule():
    if 'user_id' not in session:
        add_notification('Пожалуйста, войдите в систему для доступа к расписанию.', 'error')
        return redirect(url_for('login'))

    grouped_schedule = {}  # иниц. переменной
    user_group = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем группу пользователя
        cur.execute("SELECT grup FROM users WHERE user_id = %s", (session['user_id'],))
        user_data = cur.fetchone()
        user_group = user_data['grup'] if user_data else None
        # админ панель 
        if session.get('role') == 'admin':
            cur.execute(""" 
                SELECT id, group_number, day, subject,  
                       to_char(start_time, 'HH24:MI') as start_time,  
                       to_char(end_time, 'HH24:MI') as end_time 
                FROM schedule 
                ORDER BY 
                    CASE  
                        WHEN day = 'Понедельник' THEN 1  
                        WHEN day = 'Вторник' THEN 2  
                        WHEN day = 'Среда' THEN 3  
                        WHEN day = 'Четверг' THEN 4  
                        WHEN day = 'Пятница' THEN 5  
                    END, 
                    group_number, 
                    start_time; 
            """) 
        else: 
            cur.execute(""" 
                SELECT id, group_number, day, subject,  
                       to_char(start_time, 'HH24:MI') as start_time,  
                       to_char(end_time, 'HH24:MI') as end_time 
                FROM schedule 
                WHERE group_number = %s 
                ORDER BY 
                    CASE  
                        WHEN day = 'Понедельник' THEN 1  
                        WHEN day = 'Вторник' THEN 2  
                        WHEN day = 'Среда' THEN 3  
                        WHEN day = 'Четверг' THEN 4  
                        WHEN day = 'Пятница' THEN 5  
                    END, 
                    start_time; 
            """, (user_group,))

        schedule_data = cur.fetchall()

        # Группировка данных по дням
        grouped_schedule = {}
        for record in schedule_data:
            day = record['day']
            if day not in grouped_schedule:
                grouped_schedule[day] = []
            grouped_schedule[day].append(record)
        # Получаем данные из архива
        cur.execute("""
            SELECT id, group_number, day, subject, start_time, end_time, created_at
            FROM schedule_archive
            ORDER BY created_at DESC;
        """)
        archive_data = cur.fetchall()

        # return render_template('schedule.html', schedule_data=schedule_data, archive_data=archive_data)
    except Exception as e:
        add_notification(f'Ошибка при загрузке расписания: {str(e)}', 'error')
    finally:
        if 'conn' in locals():
            conn.close()

    # Передача данных в шаблон
    return render_template('schedule.html', grouped_schedule=grouped_schedule,user_group=user_group,archive_data=archive_data)

#добавление группы еще одно
@app.route('/add_group_schedule_new', methods=['POST'])
def add_group_schedule_new():
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))
    
    try:
        group = request.form.get('group')
        day = request.form.get('day')
        subject = request.form.get('subject')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if not all([group, day, subject, start_time, end_time]):
            add_notification('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('schedule'))

        valid_groups = ['2301', '2302', '2303', '2304', '2305', '2306', '2307', '2308', '2309', '2310']
        if group not in valid_groups:
            add_notification('Некорректный номер группы.', 'error')
            return redirect(url_for('schedule'))

        # Connect to database and insert schedule
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO schedule (group_number, day, subject, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (group, day, subject, start_time, end_time))
        
        schedule_id = cur.fetchone()['id']
        conn.commit()
        
        add_notification('Расписание успешно добавлено.', 'success')
        return redirect(url_for('schedule'))

    except psycopg2.Error as e:
        conn.rollback()
        add_notification(f'Ошибка базы данных: {str(e)}', 'error')
        return redirect(url_for('schedule'))
    
    except Exception as e:
        add_notification(f'Произошла ошибка: {str(e)}', 'error')
        return redirect(url_for('schedule'))
    
    finally:
        if 'conn' in locals():
            conn.close()
#Удаление групп
@app.route('/delete_group_schedule/<int:schedule_id>/<string:group>', methods=['POST'])
def delete_group_schedule(schedule_id, group):
    # Отладочный print
    print(f"Delete request received: schedule_id={schedule_id}, group={group}")
    
    # Проверка прав
    if 'user_id' not in session or session.get('role') != 'admin':
        print("Unauthorized access attempt")
        return jsonify({'error': 'У вас нет прав'}), 403

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверка существования записи
        cur.execute("SELECT * FROM schedule WHERE id = %s AND group_number = %s;", (schedule_id, group))
        existing_record = cur.fetchone()
        
        if not existing_record:
            print(f"No record found for id {schedule_id} in group {group}")
            return jsonify({'error': 'Запись не найдена'}), 404

        # Удаление записи
        cur.execute("DELETE FROM schedule WHERE id = %s AND group_number = %s;", (schedule_id, group))
        conn.commit()
        
        print(f"Successfully deleted schedule item {schedule_id} for group {group}")
        return jsonify({'message': 'Расписание успешно удалено'}), 200
    
    except Exception as e:
        print(f"Error deleting schedule: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

#получения группы расписания
@app.route('/get_group_schedule', methods=['POST'])
def get_group_schedule():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    group = request.form.get('group')
    if not group:
        return jsonify({'error': 'Group is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, day, subject, 
                   to_char(start_time, 'HH24:MI') as start_time, 
                   to_char(end_time, 'HH24:MI') as end_time 
            FROM schedule 
            WHERE group_number = %s 
            ORDER BY 
                CASE 
                    WHEN day = 'monday' THEN 1 
                    WHEN day = 'tuesday' THEN 2 
                    WHEN day = 'wednesday' THEN 3 
                    WHEN day = 'thursday' THEN 4 
                    WHEN day = 'friday' THEN 5 
                END,
                start_time;
        """, (group,))
        
        schedule_data = cur.fetchall()
        
        # Добавляем кнопки действий для администратора
        if session.get('role') == 'admin':
            for item in schedule_data:
                item['actions'] = f"""
                    <td class="border border-gray-700 px-4 py-2">
                        <form action="/delete_group_schedule/{item['id']}/{group}" method="post" class="inline-block">
                            <button type="submit" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 transition">
                                Удалить
                            </button>
                        </form>
                    </td>
                """
        
        return jsonify(schedule_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'conn' in locals():
            conn.close()

#обновление расписания
@app.route('/initialize_schedule', methods=['POST'])
def init_schedule_route():
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('schedule'))
    
    try:
        initialize_schedule()
        add_notification('Расписание успешно инициализировано.', 'success')
    except Exception as e:
        add_notification(f'Ошибка при инициализации расписания: {str(e)}', 'error')
    
    return redirect(url_for('schedule'))
#КОНЕЦ РАСПИСАНИЯ И ВСЕГО СВЯЗУЮЩЕГО С НИМ -------------------------------------------------------------------------------------------------------------

# файлы
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['AVATAR_ALLOWED_EXTENSIONS']
# главн. стра
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Новости для главной страницы (без картинок)
        cur.execute("SELECT id, title, content, created_at FROM news WHERE image IS NULL ORDER BY created_at DESC LIMIT 5")  # Только 5 новостей
        home_news = cur.fetchall()
        for news in home_news:
            news['short_content'] = shorten_text(news['content'])
            if news['created_at']:
                news['formatted_date'] = news['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cur.close()
        conn.close()
        return render_template('start.html', latest_news=home_news)  # Передаем новости в шаблон
    except Exception as e:
        print(traceback.format_exc())
        return "Ошибка при получении данных о новостях", 500

#уведы
@app.route('/get_notifications')
def get_notifications():
    notifications = session.pop('notifications', [])
    return jsonify(notifications)

def add_notification(message, category='info'):
    if 'notifications' not in session:
        session['notifications'] = []
    session['notifications'].append({'message': message, 'category': category})

#регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        group = request.form.get('group')

        # Валидация полей
        if not username or not email or not password or not group:
            add_notification('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('register'))

        # проверка совпадений паролей
        if password != confirm_password:
            add_notification('Пароли не совпадают.', 'error')
            return redirect(url_for('register'))

        # длина символов
        if len(password) < 6:
            add_notification('Пароль должен содержать не менее 6 символов.', 'error')
            return redirect(url_for('register'))

        # группа
        valid_groups = ['2301', '2302', '2303', '2304', '2305', '2306', '2307', '2308', '2309', '2310']
        if group not in valid_groups:
            add_notification('Пожалуйста, выберите корректную группу.', 'error')
            return redirect(url_for('register'))

        # хаширование
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # проверка одинаковых почт
            cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
            user = cur.fetchone()
            if user:
                add_notification('Пользователь с таким email уже существует.', 'error')
                return redirect(url_for('register'))

            # вставка в бд пользователя
            cur.execute("""
                INSERT INTO users (username, email, password, role, grup)
                VALUES (%s, %s, %s, 'customer', %s);
            """, (username, email, hashed_password, group))

            conn.commit()
            add_notification('Регистрация успешна. Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))

        except psycopg2.Error as e:
            conn.rollback()
            add_notification(f'Ошибка базы данных: {str(e)}', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('login.html')

#логин 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        add_notification('Вы уже вошли в систему.', 'info')
        return redirect(url_for('profile'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            add_notification(f'Добро пожаловать, {user["username"]}!', 'success')
            return redirect(url_for('home'))
        else:
            add_notification('Неверный email или пароль.', 'error')
    return render_template('login.html')

#выход
@app.route('/logout')
def logout():
    session.clear()
    add_notification('Вы вышли из системы.', 'success')
    return redirect(url_for('home'))

#О нас страничкаа
@app.route('/about')
def about():
    return render_template('about.html')
#новости
@app.route('/news', methods=['GET', 'POST'])
def news():
    if request.method == 'POST':
        if session.get('role') != 'admin':
            add_notification('У вас нет прав на добавление новостей.', 'error')
            return redirect(url_for('news'))
        try:
            # Получение данных из формы
            title = request.form['title']
            content = request.form['content']
            image_filename = None

            # Проверяем, загрузил ли пользователь файл
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):  # Проверяем, допустим ли формат файла
                    filename = secure_filename(file.filename)  # Преобразуем имя файла
                    file.save(os.path.join(app.config['NEWS_UPLOAD_FOLDER'], filename))  # Сохраняем файл
                    image_filename = filename

            # Подключаемся к базе данных и добавляем новость
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                INSERT INTO news (title, content, image)
                VALUES (%s, %s, %s)
            """, (title, content, image_filename))
            conn.commit()
            cur.close()
            conn.close()

            add_notification('Новость успешно добавлена!', 'success')
            return redirect(url_for('news'))

        except Exception as e:
            print(traceback.format_exc())  # Логируем ошибку для отладки
            add_notification('Произошла ошибка при добавлении новости.', 'error')
            return redirect(url_for('news'))

    # Если метод GET, просто отображаем список новостей
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT *, created_at FROM news ORDER BY created_at DESC")
        news_list = cur.fetchall()
        # Форматируем дату перед отправкой в шаблон
        for news in news_list:
            if news['created_at']:
                news['formatted_date'] = news['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        cur.close()
        conn.close()
        return render_template('news.html', news_list=news_list)
    except Exception as e:
        print(traceback.format_exc())
        add_notification('Ошибка при загрузке новостей.', 'error')
        return render_template('news.html', news_list=[])

#удаление новостей
@app.route('/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    # Проверяем, является ли пользователь администратором
    if session.get('role') != 'admin':
        add_notification('У вас нет прав для удаления новостей.', 'error')
        return jsonify({'success': False, 'message': 'Недостаточно прав'}), 403

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Получаем информацию о новости, чтобы удалить её изображение (если есть)
        cur.execute("SELECT image FROM news WHERE id = %s", (news_id,))
        news = cur.fetchone()

        if news and news['image'] and news['image'].strip():
            # Удаляем файл изображения
            image_path = os.path.join(app.config['NEWS_UPLOAD_FOLDER'], news['image'])
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(traceback.format_exc())
                add_notification('Ошибка при удалении изображения.', 'error')
                return jsonify({'success': False, 'message': f'Ошибка при удалении изображения: {e}'}), 500

        # Удаляем новость из базы данных
        cur.execute("DELETE FROM news WHERE id = %s", (news_id,))
        conn.commit()

        cur.close()
        conn.close()

        add_notification('Новость успешно удалена.', 'success')
        return jsonify({'success': True, 'message': 'Новость успешно удалена'})
    except Exception as e:
        print(traceback.format_exc())
        add_notification('Ошибка при удалении новости.', 'error')
        return jsonify({'success': False, 'message': f'Ошибка при удалении новости: {e}'}), 500

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT *, created_at FROM news WHERE id = %s", (news_id,))
        news = cur.fetchone()
        cur.close()
        conn.close()

        if not news:
            add_notification('Новость не найдена.', 'error')
            return redirect(url_for('news'))

        # Форматируем дату перед отправкой в шаблон
        if news and news['created_at']:
            news['formatted_date'] = news['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            news['formatted_date'] = 'Дата отсутствует'

        return render_template('news_detail.html', news=news)

    except Exception as e:
        print(traceback.format_exc())
        add_notification('Ошибка при загрузке новости.', 'error')
        return redirect(url_for('news'))

#профиль
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        add_notification('Пожалуйста, войдите в систему для доступа к профилю.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    # Задаем фиксированную папку для загрузки
    upload_folder = os.path.join(app.root_path, 'static', 'avatars')  # Папка для аватаров
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Убедимся, что папка существует

    if request.method == 'POST':
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar and allowed_file(avatar.filename):  # Проверяем допустимость файла
                filename = secure_filename(avatar.filename)  # Безопасное имя файла
                avatar_path = os.path.join(upload_folder, filename)  # Путь к сохранению

                try:
                    # Сохраняем файл в заданную папку
                    avatar.save(avatar_path)

                    # Обновляем запись в базе данных
                    cur.execute("""
                        UPDATE users 
                        SET avatar = %s 
                        WHERE user_id = %s
                    """, (filename, user_id))
                    conn.commit()
                    add_notification('Аватар успешно обновлен.', 'success')
                except Exception as e:
                    conn.rollback()
                    add_notification(f'Ошибка при сохранении аватара: {str(e)}', 'error')
            else:
                add_notification('Недопустимый тип файла. Разрешены только изображения.', 'error')

    # Получаем данные пользователя
    cur.execute("""
        SELECT username, email, role, created_at, avatar, grup, is_verified 
        FROM users 
        WHERE user_id = %s;
    """, (user_id,))
    user = cur.fetchone()

    if not user:
        add_notification('Пользователь не найден.', 'error')
        return redirect(url_for('logout'))

    all_users = []
    if session.get('role') == 'admin':
        cur.execute("SELECT user_id, username, email, role FROM users;")
        all_users = cur.fetchall()

    conn.close()
    return render_template('profile.html', user=user, all_users=all_users)


# верификация
@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    email = request.json.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email не указан.'}), 400

    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    verification_codes[email] = verification_code

    try:
        msg = Message('Код подтверждения', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Ваш код подтверждения: {verification_code}'
        mail.send(msg)
        logger.debug(f"Email sent to {email} with code {verification_code}")
        return jsonify({'status': 'success', 'message': 'Код подтверждения отправлен.'})
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Ошибка отправки email: {str(e)}'}), 500

# подтверждение
@app.route('/verify_code', methods=['POST'])
def verify_code():
    email = request.json.get('email')
    input_code = request.json.get('code')

    if not email or not input_code:
        return jsonify({'status': 'error', 'message': 'Email и код обязательны.'}), 400

    # Проверка кода
    if email in verification_codes and verification_codes[email] == input_code:
        try:
            with psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE users 
                        SET is_verified = true 
                        WHERE email = %s
                    """, (email,))
                    connection.commit()
            
            del verification_codes[email]  # Удаление кода после подтверждения
            return jsonify({'status': 'success', 'message': 'Email успешно подтвержден.'})
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса верификации: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Ошибка при обновлении статуса.'}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Неверный код.'}), 400

#замена роли
@app.route('/change_role/<int:user_id>', methods=['POST'])
def change_role(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('profile'))

    new_role = request.form.get('role')
    if new_role not in ['admin', 'customer']:
        add_notification('Недопустимая роль.', 'error')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = %s WHERE user_id = %s;", (new_role, user_id))
    conn.commit()
    conn.close()
    add_notification('Роль успешно обновлена.', 'success')
    return redirect(url_for('profile'))

#удаление пользователя
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        add_notification('У вас нет прав для выполнения этого действия.', 'error')
        return redirect(url_for('profile'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
    conn.commit()
    conn.close()
    add_notification('Пользователь успешно удален.', 'success')
    return redirect(url_for('profile'))


@app.route('/api/news', methods=['GET'])
def api_news():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # cur.execute("SELECT id, title, content, created_at FROM news WHERE image IS NULL ORDER BY created_at DESC LIMIT 5")
        cur.execute("SELECT id, title, content, image, created_at FROM news ORDER BY created_at DESC LIMIT 1")  # Только 5 новостей
        home_news = cur.fetchall()
        for news in home_news:
            news['short_content'] = shorten_text(news['content'])
            if news['created_at']:
                news['formatted_date'] = news['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if news['image']:  # Добавляем полный путь
                news['image'] = f"/static/news_images/{news['image']}"
        cur.close()
        conn.close()

        return jsonify(home_news)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify([]), 500


# уведы 
@app.route('/get_notifications', methods=['GET'])
def retrieve_notifications():  # Changed function name
    if 'user_id' not in session:
        return jsonify([])
    
    # Retrieve and clear notifications for the current user
    notifications = session.get('notifications', [])
    session['notifications'] = []
    return jsonify(notifications)

def add_notification(message, category='info'):
    """
    Helper function to add notifications to the user's session
    
    Args:
        message (str): Notification message
        category (str, optional): Notification type (info, success, error, warning)
    """
    if 'notifications' not in session:
        session['notifications'] = []
    
    session['notifications'].append({
        'message': message,
        'category': category
    })
    session.modified = True

@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    # Get the SQL query from the form
    sql_query = request.form.get('sql_query')
    
    if not sql_query:
        flash('SQL query cannot be empty', 'error')
        return redirect(url_for('home'))  # Or any other page where you want to show the form
    
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the SQL query
        cursor.execute(sql_query)
        
        # Commit if the query is an insert/update/delete
        if sql_query.strip().lower().startswith(('insert', 'update', 'delete')):
            conn.commit()
            flash('SQL query executed successfully', 'success')
        else:
            # Fetch the result of the query if it's a select
            result = cursor.fetchall()
            conn.commit()
            return render_template('result.html', result=result)  # You may need to create a `result.html` template
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        flash('Error executing SQL query', 'error')
        traceback.print_exc()  # To log detailed error information
        return redirect(url_for('home'))  # Or the page with the SQL form


if __name__ == '__main__':
    app.run(debug=True)

#404 ошибка
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == '__main__':
    app.run(debug=True)
