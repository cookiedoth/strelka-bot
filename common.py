import json
import unicodedata

def from_json(s):
	s = s.replace("'", "\"")
	return json.loads(s)

def get_params(s, command):
	pos = s.find(command) + len(command)
	s = s[pos:]
	return s.split()

def get_command(s):
	pos = s.find("/") + 1
	if (pos == 0):
		return ""
	res = "/"
	while (pos < len(s) and unicodedata.category(s[pos]) in ('Ll', 'Pc')):
		res += s[pos]
		pos += 1
	return res

def markdown_message(text):
	return {'command' : 'sendMessage', 'parse_mode' : 'Markdown', 'text' : text}

def suffix(s, command):
	pos = s.find(command) + len(command)
	return s[min(pos + 1, len(s)):]

def get_name(user):
	if ('username' in user):
		return user['username']
	else:
		return user['first_name'] + " " + user['last_name']

def correct(s):
	for c in s:
		cat = unicodedata.category(c)
		if cat not in ('Ll', 'Lu', 'Lo', 'Nd', 'Zs'):
			return 0
	return 1

def is_int(s):
	try:
		val = int(s)
	except ValueError:
		return 0
	return 1

def all_ints(arr):
	for x in arr:
		if (not is_int(x)):
			return 0
	return 1

def readlines(f):
	res = f.readlines()
	for i in range(len(res)):
		res[i] = res[i][:len(res[i]) - 1]
	return res

def numeric_parameter(text, command):
	params = get_params(text, command)
	if ((len(params) == 0) or params[0].isdigit() == 0):
		return -1
	else:
		return int(params[0])
