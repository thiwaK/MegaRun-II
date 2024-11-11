import logging
import time

logger = logging.getLogger(__name__)
class CustomFormatter(logging.Formatter):
	def format(self, record):
		timestamp = str(time.time_ns() // 1000000)
		event = record.levelname
		message = record.getMessage()
		return f"[{timestamp}] [{event}] {message}"

logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(CustomFormatter())
logger.addHandler(consoleHandler)

logFile = logging.FileHandler("megarun_2.log")
logFile.setLevel(logging.DEBUG)
logFile.setFormatter(CustomFormatter())
logger.addHandler(logFile)
