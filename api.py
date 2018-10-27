import requests
import json

url = "http://strelkacard.ru/api/cards/status/"
CARD_TYPE_ID = '3ae427a1-0f17-4524-acb1-a3f50090a8f3'
defalut = {'cardtypeid': CARD_TYPE_ID}

def get_balance(cardnum):
	params = defalut
	params['cardnum'] = cardnum
	response = requests.get(url, params = params).json()
	if ('balance' in response):
		return response['balance']
	else:
		return -1

def process_balance(balance):
	return str(balance / 100) + " ₽"