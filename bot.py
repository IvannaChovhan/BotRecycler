import telebot
from telebot import types
from data import *

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Hello!')