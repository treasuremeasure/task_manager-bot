from telebot import TeleBot, types
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery

bot = TeleBot(token = '8190046178:AAH8fqaC9QE_F91MNE332VKUBe-KEUhGcBM')
user_state = None
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")

@bot.message_handler(commands=['start'])
def wake_up(message):  #первый ответ бота
    
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
    user_state = 'wait_for_task_name'
    response = 'Напиши название задачи 🚀'
    bot.send_message(message.chat.id, response)
    user_state = 'wait_for_description'

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global user_state
    response = 'Принято! Напиши описание задачи 🚀'
    if user_state == 'wait_for_description':
        bot.send_message(message.chat.id, response)
        user_state = 'wait_for_deadline'

    else:
        response = 'Принято! Задай дедлайн задачке 🕓'
        calendar_markup = calendar.create_calendar(name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,)
        bot.send_message(message.chat.id, response, reply_markup=calendar_markup)
        user_state = None

bot.polling()