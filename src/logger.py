import logging
import time
from datetime import datetime
import random

from props import Color

logger = logging.getLogger(__name__)

class CustomFileFormatter(logging.Formatter):
	def format(self, record):
		now = datetime.now()
		formatted_time = now.strftime("%y/%m/%d %H:%M:%S")
		event = record.levelname
		message = record.getMessage()
		return f"[{formatted_time}] [{event}] {message}"

class CustomFormatter(logging.Formatter):
	def format(self, record):
		timestamp = str(time.time_ns() // 1000000)
		event = record.levelname
		message = record.getMessage()
		now = datetime.now()
		formatted_time = now.strftime("%H:%M:%S")

		f_color = Color.F_LOG_DEFAULT
		f_color2 = Color.F_LOG_DEFAULT
		b_color = Color.B_BLACK
		if event[0] == "I":
			f_color = Color.F_LOG_INFO
			f_color2 = Color.F_BLUE
			b_color = Color.B_LOG_INFO
		elif event[0] == "W":
			f_color = Color.F_LOG_WARN
			f_color2 = Color.F_YELLOW
			b_color = Color.B_LOG_WARN
		elif event[0] == "E":
			f_color = Color.F_LOG_ERROR
			f_color2 = Color.F_RED
			b_color = Color.B_LOG_ERROR

		b_color = ""
		
		return f"{b_color}{Color.F_GRAY}[{Color.F_LIGHT_BLCK}{formatted_time}{Color.F_GRAY}]{f_color2}[{event[0]}]{Color.B_BLACK} {f_color}{message}"

class CustomFormatterUI(logging.Formatter):
	def format(self, record):
		timestamp = str(time.time_ns() // 1000000)
		event = record.levelname
		message = record.getMessage()
		now = datetime.now()
		formatted_time = now.strftime("%H:%M:%S")

		f_color = Color.F_LOG_DEFAULT
		f_color2 = Color.F_LOG_DEFAULT
		b_color = Color.B_BLACK
		if event[0] == "I":
			f_color = Color.F_LOG_INFO
			f_color2 = Color.F_BLUE
			b_color = Color.B_LOG_INFO
		elif event[0] == "W":
			f_color = Color.F_LOG_WARN
			f_color2 = Color.F_YELLOW
			b_color = Color.B_LOG_WARN
		elif event[0] == "E":
			f_color = Color.F_LOG_ERROR
			f_color2 = Color.F_RED
			b_color = Color.B_LOG_ERROR

		b_color = ""
		
		return f"{b_color}{Color.F_GRAY}[{Color.F_LIGHT_BLCK}{formatted_time}{Color.F_GRAY}]{f_color2}[{event[0]}]{Color.B_BLACK} {f_color}{message}"

class CustomLogHandlerUI(logging.Handler):
	def __init__(self, instance):
		super().__init__(logging.INFO)
		self.instance = instance

	def emit(self, record):
		log_message = self.format(record)
		self.instance.data.Log.update({str(time.time_ns() + random.randint(0,999)): log_message})

class Logger:

	def __init__(self):
		super(Logger, self).__init__()

	@staticmethod
	def getLogger():

		logger.setLevel(logging.DEBUG)

		logFile = logging.FileHandler("megarun_2.log")
		logFile.setLevel(logging.DEBUG)
		logFile.setFormatter(CustomFileFormatter())
		logger.addHandler(logFile)

		return logger
	
	@staticmethod
	def getUILogger():
		return Logger.getLogger()

	@staticmethod
	def getConsoleLogger():
		logger = Logger.getLogger()
		consoleHandler = logging.StreamHandler()
		consoleHandler.setLevel(logging.INFO)
		consoleHandler.setFormatter(CustomFormatter())
		logger.addHandler(consoleHandler)

		return logger


