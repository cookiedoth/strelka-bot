#!/usr/bin/python3

import requests
import json
import unicodedata
import time
import sys
from tokens import *
from common import *
from api import *

class chat_with_bot:

	def __init__(self, _id):
		self.id = _id
		self.cardnum = ""
		self.balance = 0

	def setparams(self, string):
		dict_version = from_json(string)
		self.cardnum = dict_version['cardnum']
		self.balance = dict_version['balance']

	def __str__(self):
		dict_version = {'cardnum' : self.cardnum, 'balance' : self.balance}
		return str(dict_version)

class telegram_bot:

	def load_from_file(self):
		try:
			f = open(self.name + ".botconfig", 'r')
		except:
			return
		x = readlines(f)

		try:
			self.last_update = int(x[1])
			chats_cnt = int(x[2])
			pos = 3
			for i in range(chats_cnt):
				chat_id = int(x[pos])
				bot_chat = chat_with_bot(chat_id)
				bot_chat.setparams(x[pos + 1])
				self.chats[chat_id] = bot_chat
				pos += 2
		except:
			print("Error while reading config")
			sys.exit(1)

	def __init__(self, _token, _name):
		self.token = _token
		self.name = _name
		self.url = "https://api.telegram.org/bot" + self.token + "/"
		self.chats = {}
		self.last_update = -1
		self.load_from_file()

	def get_updates(self):
		if (self.last_update == -1):
			data = {'timeout' : 5}
		else:
			data = {'timeout' : 5, 'offset' : self.last_update + 1}
		response = requests.get(self.url + "getUpdates", params = data)
		return response.json()['result']

	def send_command(self, response_element, chat_id):
		if (chat_id < 0):
			return
		command = response_element['command']
		response_element.pop('command')
		params = response_element
		params['chat_id'] = chat_id
		requests.post(self.url + command, data = params)

	def get_new_messages(self):
		upd = self.get_updates()
		res = []
		for i in range(1, len(upd) + 1):
			if (upd[-i]['update_id'] > self.last_update):
				if ('message' in upd[-i]):
					message = upd[-i]['message']
					chat_id = message['chat']['id']
					if (chat_id >= 0):
						res.append(message)
						if (chat_id not in self.chats):
							self.chats[chat_id] = chat_with_bot(chat_id)
			else:
				break
		if (len(upd) > 0):
			self.last_update = upd[-1]['update_id']
		return res



	def handle_message(self, message):
		print("got message")
		chat_id = message['chat']['id']
		player = self.chats[chat_id]

		if ('text' in message):
			text = message['text']
			command = get_command(text)

			if (command == '/start'):
				self.send_command(markdown_message('Я - бот, следящий за балансом на твоей карте "Стрелка". Напиши /help, чтобы посмотреть список коамнд'), chat_id)

			if (command == '/help'):
				self.send_command(markdown_message('Хелп'), chat_id)

			if (command == '/link'):
				cardnum = numeric_parameter(text, '/link')
				if (cardnum == -1):
					self.send_command(markdown_message("Напиши так: /link номер"), chat_id)
				else:
					new_cardnum = get_params(text, '/link')[0]
					if (get_balance(new_cardnum) == -1):
						self.send_command(markdown_message("Карта не существует"), chat_id)
					else:
						player.cardnum = new_cardnum
						player.balance = get_balance(player.cardnum)
						self.send_command(markdown_message("Карта " + new_cardnum + " привязана"), chat_id)

			if (command == '/reset'):
				player.cardnum = ""
				player.balance = 0
				self.send_command(markdown_message("Настройки сброшены"), chat_id)

			if (command == '/cardnum'):
				if (player.cardnum == ""):
					self.send_command(markdown_message("Карта не привязана"), chat_id)
				else:
					self.send_command(markdown_message("Текущая карта " + str(player.cardnum)), chat_id)

			if (command == '/check'):
				if (player.cardnum == ""):
					self.send_command(markdown_message("Сначала надо привязать карту"), chat_id)
				else:
					balance = get_balance(player.cardnum)
					if (balance == -1):
						print("Incorrect card", chat_id)
					else:
						self.send_command(markdown_message("Баланс " + process_balance(balance)), chat_id)

	def update(self):
		print("updating bot...", int(time.time()))
		messages = self.get_new_messages()[::-1]
		for msg in messages:
			self.handle_message(msg)

		for chat_id, player in self.chats.items():
			if (player.cardnum != ""):
				new_balance = get_balance(player.cardnum)
				if (new_balance != player.balance):
					self.send_command(markdown_message("Изменение баланса: " + process_balance(player.balance) + " > " + process_balance(new_balance)), chat_id)
					player.balance = new_balance


	def save_to_file(self):
		f = open(self.name + ".botconfig", 'w')
		f.write("Configuration to bot " + self.name + "\n")
		f.write(str(self.last_update) + "\n")
		f.write(str(len(self.chats)) + "\n")
		for key, value in self.chats.items():
			f.write(str(key) + "\n")
			f.write(str(value) + "\n")

bot = telegram_bot(TOKEN, BOT_NAME)

while (True):
	try:
		bot.update()
		bot.save_to_file()
	except KeyboardInterrupt:
		break