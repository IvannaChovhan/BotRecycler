import telebot
from telebot import types
from data import *
import recyclers
import database
import re

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
	if message.chat.type != 'private':
		bot.send_message(message.chat.id, 'Я працюю лише в особистих повідомленнях!')
		return
	user = database.get_user(message.chat.id)
	if user:
		text = 'Здається, ти вже зареєстрований! '
		if user['state'] == 'init':
			text += "Надішли мені своє ім'я, щоб я знав, як до тебе звертатися."
		elif user['state'] == 'waiting_for_phone':
			text += 'Надішли мені свій номер телефону (або 0, якщо не хочеш давати його) щоб наші оператори могли з тобою зв\'язатися.'
		else:
			text += 'Натисни /help, щоб побачити список доступних команд.'
		bot.send_message(message.chat.id, text)
		return
	bot.send_message(message.chat.id, 'Привіт!')
	bot.send_message(message.chat.id, 'Тобі необхідно пройти короткий процес реєстрації.')
	bot.send_message(message.chat.id, 'Не хвилюйся, це тільки один раз, а всі дані ти зможеш змінити в будь-який момент.')
	bot.send_message(message.chat.id, 'Як мені до тебе звертатися?')
	database.init_user(message.chat.id)


@bot.message_handler(commands=['menu'])
def menu(message):
	if not user_check_routine(message):
		return
	# TODO проверка на state - если не меню, прибить старый диалог или спросить, убивать ли старый диалог
	send_menu_message(message)


@bot.message_handler(commands=['change_name'])
def change_name(message):
	if not user_check_routine(message):
		return
	bot.send_message(message.chat.id, 'Як ти хочеш, щоб я тебе називав?')
	database.update_state(message.chat.id, 'change_name')


@bot.message_handler(commands=['change_phone'])
def change_phone(message):
	if not user_check_routine(message):
		return
	bot.send_message(message.chat.id, 'Надішли мені новий номер телефону або 0, якщо не хочеш давати його.')
	database.update_state(message.chat.id, 'change_phone')


@bot.message_handler(commands=['help'])
def help_message(message):
	text = '/menu - почати користування ботом\n'
	text += '/start - перевірити, чи ви зареєстровані\n'
	text += '/current_requests - перевірити свої заявки на вивіз сміття\n'
	text += '/change_name - змінити своє ім\'я в базі\n'
	text += '/change_phone - змінити свій номер телефону\n'
	text += '/help - переглянути цей список'
	bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['current_requests'])
def current_requests(message):
	if not user_check_routine(message):
		return
	requests = database.get_user_requests(message.chat.id)
	text = '\n'.join([elem['type'] + ', ' + elem['amount'] for elem in requests])
	bot.send_message(message.chat.id, 'Ваші заявки:\n' + text)


@bot.callback_query_handler(func=lambda c: True)
def query_handler(c):
	m_id = c.message.chat.id
	user = database.get_user(m_id)
	if not user:
		return
	if c.data == 'find_closest_init':
		database.update_state(m_id, 'find_closest_init')
		delete_menu(m_id)
		bot.send_message(m_id, 'Надішли мені свою геопозицію за допомогою скріпки знизу.')
		return
	elif c.data == 'leave_request_init':
		types = recyclers.get_types()
		delete_menu(m_id)
		bot.send_message(m_id, '\n'.join(types))
		bot.send_message(m_id, 'Вибери тип сміття зі списку вище.')
		database.update_state(m_id, 'leave_request_type')


@bot.message_handler(content_types=['text'])
def text_handler(message):
	if message.chat.type != 'private':
		bot.send_message(message.chat.id, 'Я працюю лише в особистих повідомленнях!')
		return
	user = database.get_user(message.chat.id)
	if not user:
		bot.send_message(message.chat.id, 'Натисни /start, щоб почати.')
		return
	if user['state'] == 'init':
		database.update_user(message.chat.id, 'user_name', message.text)
		database.update_state(message.chat.id, 'waiting_for_phone')
		bot.send_message(message.chat.id, 'Приємно познайомитись, ' + message.text + '! Тепер надішли мені свій номер телефону (або 0, якщо не хочеш давати його) щоб наші оператори могли з тобою зв\'язатися.')
		return
	elif user['state'] == 'waiting_for_phone':
		if message.text == '0':
			database.update_state(message.chat.id, 'menu')
			bot.send_message(message.chat.id, 'Не проблема. Список команд знайдеш за допомогою /help.')
			send_menu_message(message)
			return
		if not check_number(message.text):
			bot.send_message(message.chat.id, 'Формат номеру має відповідати одному з двох:\n1. +380XXXXXXXXX\n2. 0XXXXXXXXX')
			return
		database.update_user(message.chat.id, 'user_phone', message.text) # TODO валидация
		database.update_state(message.chat.id, 'menu')
		bot.send_message(message.chat.id, 'Дякую! Список команд ти можеш знайти за допомогою /help.')
		send_menu_message(message)
		return
	elif user['state'] == 'change_name':
		text = 'Дуже добре, ' + message.text + '.'
		database.update_state(message.chat.id, 'menu')
		database.update_user(message.chat.id, 'user_name', message.text)
		bot.send_message(message.chat.id, text)
		send_menu_message(message)
		return
	elif user['state'] == 'change_phone':
		if message.text == '0':
			database.update_state(message.chat.id, 'menu')
			database.update_user(message.chat.id, 'user_phone', '0')
			bot.send_message(message.chat.id, 'Не проблема. Твій номер видалено з бази. Список команд знайдеш за допомогою /help.')
			send_menu_message(message)
			return
		if not check_number(message.text):
			bot.send_message(message.chat.id, 'Формат номеру має відповідати одному з двох:\n1. +380XXXXXXXXX\n2. 0XXXXXXXXX')
			return
		text = 'Тепер твій номер - ' + message.text + '.'
		database.update_state(message.chat.id, 'menu')
		database.update_user(message.chat.id, 'user_phone', message.text) # TODO валидация
		bot.send_message(message.chat.id, text)
		send_menu_message(message)
		return
	elif user['state'] == 'find_closest_type':
		types = recyclers.get_types()
		if message.text not in types:
			bot.send_message(message.chat.id, 'Вибери тип зі списку вище, будь-ласка.')
			return
		closest = recyclers.get_closest((user['pos_lon'], user['pos_lat']), message.text, 10)
		text = '\n'.join([str(elem[0]) + ', ' + str(elem[1]) for elem in closest])
		bot.send_message(message.chat.id, 'Найближчі до вас пункти:\n' + text)
		return
	elif user['state'] == 'leave_request_type':
		types = recyclers.get_types()
		if message.text not in types:
			bot.send_message(message.chat.id, 'Вибери тип зі списку вище, будь-ласка.')
			return
		database.init_request(message.chat.id)
		database.update_request(message.chat.id, 'type', message.text)
		database.update_state(message.chat.id, 'leave_request_amount')
		bot.send_message(message.chat.id, 'Чудово! Тепер назви обсяги разом із одиницями вимірювання. Наприклад, 12кг.')
		return
	elif user['state'] == 'leave_request_amount':
		database.update_request(message.chat.id, 'amount', message.text)
		database.update_state(message.chat.id, 'leave_request_location')
		bot.send_message(message.chat.id, 'А тепер надішли мені свою геопозицію за допомогою скріпки знизу.')
		return
	else:
		bot.send_message(message.chat.id, 'Натисни /menu для того, щоб почати, або /help, щоб побачити всі доступні команди.')
		return


@bot.message_handler(content_types=['location'])
def location_handler(message):
	if not user_check_routine(message):
		return
	user = database.get_user(message.chat.id)
	if user['state'] == 'find_closest_init':
		database.update_state(message.chat.id, 'find_closest_type')
		print(message.location.longitude, message.location.latitude)
		database.update_user(message.chat.id, 'pos_lon', message.location.longitude)
		database.update_user(message.chat.id, 'pos_lat', message.location.latitude)
		types = recyclers.get_types()
		bot.send_message(message.chat.id, '\n'.join(types))
		bot.send_message(message.chat.id, 'Вибери тип сміття зі списку вище. Можеш вибирати скільки завгодно, а потім просто повернутися в /menu.')
	if user['state'] == 'leave_request_location':
		database.update_state(message.chat.id, 'menu')
		print(message.location.longitude, message.location.latitude)
		database.update_request(message.chat.id, 'pos_lon', message.location.longitude)
		database.update_request(message.chat.id, 'pos_lat', message.location.latitude)
		bot.send_message(message.chat.id, 'Чудово! Оператор зв\'яжеться й домовиться з ваи про усе інше. Список ваших заявок можна побачити за допомогою /current_requests.')
		send_menu_message(message)


def send_menu_message(message):
	user = database.get_user(message.chat.id)
	delete_menu(message.chat.id)
	text = user['user_name'] + ', ви хочете знайти найближчий пункт переробки чи залишити заявку на вивіз сміття?'
	kb = types.InlineKeyboardMarkup()
	kb.row(types.InlineKeyboardButton(text='Найближчий пункт', callback_data='find_closest_init'))
	kb.row(types.InlineKeyboardButton(text='Заявка на вивіз', callback_data='leave_request_init'))
	m = bot.send_message(message.chat.id, text, reply_markup=kb)
	database.update_state(message.chat.id, 'menu')
	database.update_user(message.chat.id, 'menu_message', m.message_id)


def delete_menu(m_id):
	user = database.get_user(m_id)
	if not user:
		bot.send_message(m_id, 'Натисни /start, щоб почати.')
		return
	if int(user['menu_message']):
		bot.delete_message(m_id, int(user['menu_message']))
	database.update_user(m_id, 'menu_message', '0')


def user_check_routine(message):
	if message.chat.type != 'private':
		bot.send_message(message.chat.id, 'Я працюю лише в особистих повідомленнях!')
		return False
	user = database.get_user(message.chat.id)
	if not user:
		bot.send_message(message.chat.id, 'Натисни /start, щоб почати.')
		return False
	if user['state'] == 'init':
		text = "Реєстрацію ще не завершено! Надішли мені своє ім'я, щоб я знав, як до тебе звертатися."
		bot.send_message(message.chat.id, text)
		return False
	if user['state'] == 'waiting_for_phone':
		text = "Реєстрацію ще не завершено! Надішли мені свій номер телефону (або 0, якщо не хочеш давати його) щоб наші оператори могли з тобою зв'язатися."
		bot.send_message(message.chat.id, text)
		return False
	if user['state'] == 'change_name':
		text = 'Спочатку потрібно закінчити зміну імені. Як до тебе звертатися?'
		bot.send_message(message.chat.id, text)
		return False
	if user['state'] == 'change_phone':
		text = 'Спочатку потрібно закінчити зміну номеру. Надішли мені номер телефону або 0, якщо не хочеш давати його.'
		bot.send_message(message.chat.id, text)
		return False
	return True


def check_number(number:str):
    return bool(re.match(r'^\+38?1?\d{10}$', number)) if number.startswith('+') else bool(re.match(r'\d{10}$', number))


bot.polling()