import telebot
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor
import threading
import logging
from telebot import types

# Bot configuration
token = "7833173236:AAGkABoJfwrTBSvl7HN1nmhYE7E_EdDfBTE"
admin_chat_id = "809505217"

db_config = {
    "dbname": "schedulehah",
    "user": "postgres",
    "password": "123",
    "host": "localhost",
    "port": "5432"
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(token)

group_subscribers = {}

def setup_db_trigger():
    """Ensure the trigger for schedule changes exists."""
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                DROP TRIGGER IF EXISTS schedule_changes_trigger ON schedule;
                """)
                # Create the notification function for schedule changes
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION notify_schedule_changes()
                    RETURNS TRIGGER AS $$
                    DECLARE
                        change_type TEXT;
                        schedule_info TEXT;
                    BEGIN
                        IF (TG_OP = 'INSERT') THEN
                            change_type = 'INSERT';
                            schedule_info = format(
                                'Новая запись в расписании: группа %s, предмет %s, день %s, время %s-%s',
                                NEW.group_number,
                                NEW.subject,
                                NEW.day,
                                NEW.start_time,
                                NEW.end_time
                            );
                        ELSIF (TG_OP = 'UPDATE') THEN
                            change_type = 'UPDATE';
                            schedule_info = format(
                                'Обновление расписания: группа %s, предмет %s, день %s, время %s-%s',
                                NEW.group_number,
                                NEW.subject,
                                NEW.day,
                                NEW.start_time,
                                NEW.end_time
                            );
                        ELSIF (TG_OP = 'DELETE') THEN
                            change_type = 'DELETE';
                            schedule_info = format(
                                'Удаление из расписания: группа %s, предмет %s, день %s, время %s-%s',
                                OLD.group_number,
                                OLD.subject,
                                OLD.day,
                                OLD.start_time,
                                OLD.end_time
                            );
                        END IF;
                        PERFORM pg_notify('schedule_changes', schedule_info);
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)

                # Create the trigger
                cursor.execute("""
                    CREATE TRIGGER schedule_changes_trigger
                    AFTER INSERT OR UPDATE OR DELETE ON schedule
                    FOR EACH ROW EXECUTE FUNCTION notify_schedule_changes();
                """)
                conn.commit()
        logger.info("Триггер для изменений расписания настроен.")
    except Exception as e:
        logger.error(f"Ошибка настройки триггера: {e}")
        raise
setup_db_trigger()

def load_group_subscribers():
    """Load group subscribers from the database"""
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS group_subscribers (
                        group_number VARCHAR(10),
                        chat_id VARCHAR(50),
                        PRIMARY KEY (group_number, chat_id)
                    )
                """)
                cursor.execute("SELECT group_number, chat_id FROM group_subscribers")
                subscribers = cursor.fetchall()
                
                for group, chat_id in subscribers:
                    if group not in group_subscribers:
                        group_subscribers[group] = set()
                    group_subscribers[group].add(chat_id)
                
                return group_subscribers
    except Exception as e:
        logger.error(f"Error loading group subscribers: {e}")
        return {}

def add_group_subscriber(group, chat_id):
    """Add a subscriber for a specific group"""
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                chat_id_str = str(chat_id)
                
                cursor.execute("""
                    INSERT INTO group_subscribers (group_number, chat_id)
                    VALUES (%s, %s)
                    ON CONFLICT (group_number, chat_id) DO NOTHING
                """, (group, chat_id_str))
                conn.commit()
        
        if group not in group_subscribers:
            group_subscribers[group] = set()
        group_subscribers[group].add(chat_id_str)
        
        return True
    except Exception as e:
        logger.error(f"Error adding group subscriber: {e}")
        return False

def remove_group_subscriber(group, chat_id):
    """Remove a subscriber for a specific group"""
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                chat_id_str = str(chat_id)
                
                cursor.execute("""
                    DELETE FROM group_subscribers 
                    WHERE group_number = %s AND chat_id = %s
                """, (group, chat_id_str))
                conn.commit()
        
        if group in group_subscribers and chat_id_str in group_subscribers[group]:
            group_subscribers[group].remove(chat_id_str)
        
        return True
    except Exception as e:
        logger.error(f"Error removing group subscriber: {e}")
        return False

def get_schedule(group):
    """Retrieve schedule for a specific group"""
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = """
                SELECT day, start_time, subject
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
                """
                cursor.execute(query, (group,))
                rows = cursor.fetchall()

        if not rows:
            return "Расписание отсутствует."

        schedule = {}
        for row in rows:
            day_name = row['day']
            if day_name not in schedule:
                schedule[day_name] = []
            schedule[day_name].append(
                f"Время: {row['start_time'].strftime('%H:%M')}, Предмет: {row['subject']}"
            )

        result = ""
        for day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']:
            if day in schedule:
                result += f"\n{day}:\n" + "\n".join(schedule[day])

        return result.strip() or "Расписание отсутствует."
    except Exception as e:
        logger.error(f"Ошибка получения расписания: {e}")
        return f"Ошибка получения расписания: {e}"

def monitor_schedule_changes():
    """Monitor database for schedule changes and send notifications"""
    try:
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        cursor.execute("LISTEN schedule_changes;")
        
        logger.info("Started monitoring schedule changes...")
        
        while True:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                logger.info(f"Received notification: {notify.payload}")
                
                try:
                    parts = notify.payload.split(", ")
                    group = parts[0].split()[-1]
                    
                    if group in group_subscribers:
                        for chat_id in group_subscribers[group]:
                            try:
                                bot.send_message(
                                    chat_id, 
                                    f"Изменение в расписании группы {group}:\n{notify.payload}"
                                )
                            except Exception as send_error:
                                logger.error(f"Не удалось отправить уведомление в Telegram для {chat_id}: {send_error}")
                    
                    bot.send_message(
                        admin_chat_id, 
                        f"Изменение в расписании:\n{notify.payload}"
                    )
                
                except Exception as send_error:
                    logger.error(f"Не удалось обработать уведомление: {send_error}")
    
    except Exception as e:
        logger.error(f"Ошибка при прослушивании изменений: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# Inline keyboard for interaction
def get_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    schedule_button = types.InlineKeyboardButton("Получить расписание", callback_data="schedule")
    subscribe_button = types.InlineKeyboardButton("Подписаться на уведомления", callback_data="subscribe")
    unsubscribe_button = types.InlineKeyboardButton("Отписаться от уведомлений", callback_data="unsubscribe")
    keyboard.add(schedule_button, subscribe_button, unsubscribe_button)
    return keyboard

# Save user state for pending action (schedule, subscribe, unsubscribe)
user_state = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте! Я бот для расписания.\n"
                           "/schedule <группа> - получить расписание\n"
                           "/subscribe <группа> - подписаться на уведомления\n"
                           "/unsubscribe <группа> - отписаться от уведомлений",
                           reply_markup=get_inline_keyboard())

@bot.callback_query_handler(func=lambda call: call.data in ['schedule', 'subscribe', 'unsubscribe'])
def handle_callback(call):
    action = call.data  # Action (schedule, subscribe, unsubscribe)
    user_state[call.message.chat.id] = action  # Store the action in user state
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Пожалуйста, введите номер группы:")

@bot.message_handler(func=lambda message: message.chat.id in user_state)
def handle_group_input(message):
    group = message.text.strip()  # Get group number from the user input
    action = user_state.pop(message.chat.id, None)  # Retrieve action from user state

    if not action:
        return  # If no action is found, do nothing

    if action == 'schedule':
        schedule = get_schedule(group)
        bot.send_message(message.chat.id, schedule, reply_markup=get_inline_keyboard())
    elif action == 'subscribe':
        if add_group_subscriber(group, message.chat.id):
            bot.send_message(message.chat.id, f"Вы подписались на уведомления для группы {group}.", reply_markup=get_inline_keyboard())
        else:
            bot.send_message(message.chat.id, "Ошибка подписки.", reply_markup=get_inline_keyboard())
    elif action == 'unsubscribe':
        if remove_group_subscriber(group, message.chat.id):
            bot.send_message(message.chat.id, f"Вы отписались от уведомлений для группы {group}.", reply_markup=get_inline_keyboard())
        else:
            bot.send_message(message.chat.id, "Ошибка отписки.", reply_markup=get_inline_keyboard())

if __name__ == "__main__":
    # Initialize subscribers on startup
    group_subscribers = load_group_subscribers()
    
    # Start monitoring schedule changes
    threading.Thread(target=monitor_schedule_changes, daemon=True).start()
    
    # Start bot polling
    bot.polling(non_stop=True)