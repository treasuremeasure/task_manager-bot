import datetime
from telebot import TeleBot, types
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery

global user_state
global user_tasks

bot = TeleBot(token='8190046178:AAH8fqaC9QE_F91MNE332VKUBe-KEUhGcBM')  #нужно засунуть в окружение переменных
user_state = None
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_callback = CallbackData("calendar", "action", "year", "month", "day")  # CallbackData для календаря

@bot.message_handler(commands=['start'])
def wake_up(message):  # первый ответ бота
    user_state = 'wait_for_task_name'
    user_name = message.from_user.first_name
    response = f'''Добрый день, {user_name}!
Я ваш персональный таск-менеджер. Вы можете в меня грузить ваши задачи, а я буду стараться за ними следить и напоминать о дедлайнах!'''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text='Создать задачу')
    keyboard.add(button)

    bot.send_message(message.chat.id, response, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Создать задачу')
def give_name_to_the_task(message): 
    global user_state
    response = 'Напиши название задачи 🚀'
    bot.send_message(message.chat.id, response)
    user_state = 'wait_for_description'

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global user_tasks
    global user_state
    if user_state == 'wait_for_description':
        response = 'Принято! Напиши описание задачи 🚀'
        bot.send_message(message.chat.id, response)
        user_tasks = { 
            message.chat.id:{
                "Название":message.text
            }
        }
        user_state = 'wait_for_deadline'
    elif user_state == 'wait_for_deadline':
        response = 'Принято! Задай дедлайн задачке 🕓'
        now = datetime.datetime.now()
        calendar_markup = calendar.create_calendar(name=calendar_callback.prefix, year=now.year, month=now.month)
        bot.send_message(message.chat.id, response, reply_markup=calendar_markup)
        user_tasks[message.chat.id]["Описание"] = message.text
        user_state = 'wait_for_approval'
        print(user_state)

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
def handle_calendar_callback(call: CallbackQuery):
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
    
    elif action == "CANCEL":  
        bot.send_message(
            chat_id=call.from_user.id,
            text="Отмена выбора даты",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_callback}: Cancellation")

@bot.message_handler(content_types=['text'])
def approval_of_task_or_not(message):
    global user_state
    if user_state == 'wait_for_approval':
        if message.text == 'Да':
            bot.send_message(message.chat.id, text = 'Отлично! Я вам напомню о задаче ближе к дедлайну')
        elif message.text == 'Нет':
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text='Название')
            button_2 = types.KeyboardButton(text='Описание')
            button_3 = types.KeyboardButton(text='Дедлайн')
            keyboard.row(button_1, button_2, button_3)
            bot.send_message(message.chat.id, reply_markup = keyboard, text = 'Что бы вы хотели изменить?')
    else:
        None

bot.polling()
