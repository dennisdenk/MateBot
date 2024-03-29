from config import config
from state import getOrCreateUser, findUserByNick

def parseAmount(text, min=0, max=config["max-amount"]):
	try:
		if text.find(",") != -1:
			text = text.replace(",", ".")
		val = float(text)
		if val < 0:
			return None, "less than zero"
		elif val == 0:
			return None, "zero"
		elif val > max:
			return None, "larger than the maximum allowed amount"
		elif int(val * 100) / float(100) != val:
			return None, "too precise ({} would turn into {})" \
				.format(val, int(val * 100) / float(100))
		else:
			return int(val * 100), None
	except:
		return None, "not a number"

ARG_TEXT = 0
ARG_INT = 1
ARG_AMOUNT = 2
ARG_USER = 3
ARG_REST = 4
def parseArgs(msg, argDef, defaults, usage=""):
	split = msg.text.split(" ")
	result = []
	error = None

	offset = len(split[0]) + 1
	split = split[1 : ]

	for i, expected in enumerate(argDef):
		if i < len(split):
			arg = split[i]
		elif i < len(defaults) and defaults[i] is not None:
			result.append(defaults[i])
			continue
		else:
			error = "Argument {} not specified".format(i)
			break

		if expected == ARG_TEXT:
			result.append(arg)
		elif expected == ARG_INT:
			try:
				val = int(arg)
				result.append(val)
			except:
				error = "Argument {} should be an int but is '{}'".format(i, arg)
				break
		elif expected == ARG_AMOUNT:
			val, error = parseAmount(arg)
			if val is None:
				error = "Argument {} should be an amount but is {}".format(i, error)
				break
			result.append(val)
		elif expected == ARG_USER:
			user = None
			for entity in msg.entities:
				if entity.offset == offset:
					if entity.type == "mention":
						user = findUserByNick(arg[1 : ])
						break
					elif entity.type == "text_mention":
						user = getOrCreateUser(entity.user)
						break

			if user is None:
				error = "Argument {} should be an user but is '{}'".format(i, arg)
				break

			result.append(user)
		elif expected == ARG_REST:
			result.append(" ".join(split[i : ]))
			break

		offset = offset + len(arg) + 1

	if error is None:
		return result
	else:
		error = error + usage
		msg.reply_text(error)
		raise Exception(error)
