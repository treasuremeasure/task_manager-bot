
from datetime import datetime, timedelta
from telebot import TeleBot, types
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

user_tasks = {}
bot_state = None

bot = TeleBot(token='8190046178:AAH8fqaC9QE_F91MNE332VKUBe-KEUhGcBM')  #нужно засунуть в окружение переменных
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_callback = CallbackData("calendar", "action", "year", "month", "day")  # CallbackData для календаря

@bot.message_handler(commands=['start'])
def wake_up(message):  # первый ответ бота
    user_name = message.from_user.first_name
    response = f'''Добрый день, {user_name}!
Я ваш персональный таск-менеджер. Вы можете в меня грузить ваши задачи, а я буду стараться за ними следить и напоминать о дедлайнах!'''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text='Создать задачу')
    keyboard.add(button)

    bot.send_message(message.chat.id, response, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Создать задачу')
def give_name_to_the_task(message): 
    global bot_state
    response = 'Напиши название задачи 🚀'
    remove_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, response, reply_markup=remove_keyboard)
    bot_state = 'wait_for_task_name'
    print(bot_state)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
def handle_calendar_callback(call: CallbackQuery):
    global bot_state
    # Обработка выбора даты
    name, action, year, month, day = call.data.split(calendar_callback.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Выбранная дата {date.strftime('%d.%m.%Y')}. Принято ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_callback}: Day: {date.strftime('%d.%m.%Y')}")
        user_tasks[call.from_user.id]["Дедлайн"] = date.strftime('%d.%m.%Y') 
        task_name = user_tasks.get(call.from_user.id, {}).get("Название", "Название не указано") 
        task_description = user_tasks.get(call.from_user.id, {}).get("Описание", "Описание нет")
        task_deadline = user_tasks.get(call.from_user.id, {}).get("Дедлайн", "Дедлайна нет")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton(text='Да')
        button_2 = types.KeyboardButton(text='Нет')
        keyboard.row(button_1, button_2)
        bot.send_message(chat_id=call.from_user.id, reply_markup=keyboard, text = 
        
    
    f'''
    Задача 
    
Название: {task_name}
Описание: {task_description}
Дедлайн: {task_deadline}
        
Подтверждаете?
    
    '''
    
    )
        
        print(user_tasks)

        if bot_state == 'wait_for_new_deadline':
            new_deadline = date.strftime('%d.%m.%Y')
            user_tasks[call.from_user.id]["Дедлайн"] = new_deadline
            task_name = user_tasks[call.from_user.id].get("Название", "Название не указано")
            task_description = user_tasks[call.from_user.id].get("Описание", "Описание не указано")
            
            # Клавиатура для подтверждения
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_yes = types.KeyboardButton(text='Да')
            button_no = types.KeyboardButton(text='Нет')
            keyboard.row(button_yes, button_no)
            
            # Отправка подтверждения с обновленным дедлайном
            bot.send_message(call.from_user.id, text=f'''
    Задача 

Название: {task_name}
Описание: {task_description}
Дедлайн: {new_deadline}

Подтверждаете?
            ''', reply_markup=keyboard)
            
            # Переключаемся на состояние ожидания подтверждения
            bot_state = 'wait_for_approval'
    
    elif action == "CANCEL":  
        bot.send_message(
            chat_id=call.from_user.id,
            text="Отмена выбора даты",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_callback}: Cancellation")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    
    global bot_state, user_tasks

    if bot_state == 'wait_for_task_name':
        response = 'Принято! Напиши описание задачи 🚀'
        bot.send_message(message.chat.id, response)
        user_tasks[message.chat.id] = {"Название": message.text}
        bot_state = 'wait_for_description'
        print(bot_state)

    elif bot_state == 'wait_for_description':
        response = 'Принято! Задай дедлайн задачке 🕓'
        now = datetime.now()
        calendar_markup = calendar.create_calendar(name=calendar_callback.prefix, year=now.year, month=now.month)
        bot.send_message(message.chat.id, response, reply_markup=calendar_markup)
        user_tasks[message.chat.id]["Описание"] = message.text
        bot_state = 'wait_for_approval'
        print(bot_state)

    elif bot_state == 'wait_for_approval':
        if message.text == 'Да':
            remove_keyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, text='Отлично! Я вам напомню о задаче ближе к дедлайну', reply_markup=remove_keyboard)
            bot_state = 'send_notification_about_task_deadline'
            task_name = user_tasks[message.chat.id]["Название"]
            deadline = user_tasks[message.chat.id]["Дедлайн"]
            schedule_reminders(message.chat.id, task_name, deadline)
        elif message.text == 'Нет':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_1 = types.KeyboardButton(text='Название')
            button_2 = types.KeyboardButton(text='Описание')
            button_3 = types.KeyboardButton(text='Дедлайн')
            keyboard.row(button_1, button_2, button_3)
            bot.send_message(message.chat.id, reply_markup=keyboard, text='Что бы вы хотели изменить?')
            bot_state = 'smth_needs_to_be_changed_in_the_task'

    elif bot_state == 'smth_needs_to_be_changed_in_the_task':
        if message.text == 'Название':
            remove_keyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, text = 'Задайте новое название 🤓', reply_markup=remove_keyboard)
            bot_state = 'wait_for_new_task_name'
        if message.text == 'Описание':
            remove_keyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, text = 'Задайте новое описание 🤓', reply_markup=remove_keyboard)
            bot_state = 'wait_for_new_description'
        if message.text == 'Дедлайн':
            now = datetime.datetime.now()
            calendar_markup = calendar.create_calendar(name=calendar_callback.prefix, year=now.year, month=now.month)
            bot.send_message(message.chat.id, text = 'Задайте новый дедлайн 🤓', reply_markup=calendar_markup)
            bot_state = 'wait_for_new_deadline'

    elif bot_state == 'wait_for_new_task_name':
        new_task_name = message.text
        task_description = user_tasks[message.chat.id].get('Описание')
        task_deadline = user_tasks[message.chat.id].get('Дедлайн')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_4 = types.KeyboardButton(text='Да')
        button_5 = types.KeyboardButton(text = 'Нет')
        keyboard.row(button_4, button_5)
        bot.send_message(message.chat.id, reply_markup=keyboard, text = 
        
        f'''
    Задача 
    
Название: {new_task_name}
Описание: {task_description}
Дедлайн: {task_deadline}
        
Подтверждаете?
    
    '''
        
        
        )        

        bot_state = 'wait_for_approval'           
        
    elif bot_state == 'wait_for_new_description':
        new_task_description = message.text
        task_name = user_tasks[message.chat.id].get('Название')
        task_deadline = user_tasks[message.chat.id].get('Дедлайн')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_6 = types.KeyboardButton(text='Да')
        button_7 = types.KeyboardButton(text = 'Нет')
        keyboard.row(button_6, button_7)
        bot.send_message(message.chat.id, reply_markup=keyboard,  text = 
        
        f'''
    Задача 
    
Название: {task_name}
Описание: {new_task_description}
Дедлайн: {task_deadline}
        
Подтверждаете?
    
    '''
        
        )              
        
        bot_state = 'wait_for_approval'


    elif bot_state == 'wait_for_new_deadline':
        new_task_deadline = message.text
        task_name = user_tasks[message.chat.id].get('Название')
        task_deadline = user_tasks[message.chat.id].get('Дедлайн')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_6 = types.KeyboardButton(text='Да')
        button_7 = types.KeyboardButton(text = 'Нет')
        keyboard.row(button_6, button_7)
        bot.send_message(message.chat.id, reply_markup=keyboard,  text = 
        
        f'''
    Задача 
    
Название: {task_name}
Описание: {task_description}
Дедлайн: {task_deadline}
        
Подтверждаете?
    
    '''
        
        )              
        
        bot_state = 'wait_for_approval'

        #код с обработкой нового дедлайна находится в callback_query_handler (if bot_state = wait_for_new_deadline)


def send_reminder(chat_id, task_name, days_left):
    message_text = f"⚠️ Напоминание!\nДо дедлайна задачи '{task_name}' осталось {days_left} дней!"
    bot.send_message(chat_id=chat_id, text=message_text)

# Функция для планирования напоминаний
def schedule_reminders(chat_id, task_name, deadline_str):
    # Преобразование строки дедлайна в datetime
    deadline_date = datetime.strptime(deadline_str, '%d.%m.%Y')

    scheduled_dates = []
    
    # Планируем напоминания за 3, 2 и 1 день
    for days in [3, 2, 1]:
        reminder_date = deadline_date - timedelta(days=days)
        if reminder_date > datetime.now():
            scheduler.add_job(
                send_reminder,
                'date',
                run_date=reminder_date,
                args=[chat_id, task_name, days]
            )
            scheduled_dates.append(reminder_date.strftime('%d.%m.%Y'))
    
    if scheduled_dates:
        confirmation_message = f"✅ Напоминания запланированы на следующие даты:\n{', '.join(scheduled_dates)}"
    else:
        confirmation_message = "⚠️ Напоминания не были запланированы, так как дата дедлайна слишком близко"
    
    bot.send_message(chat_id=chat_id, text=confirmation_message)

bot.polling()