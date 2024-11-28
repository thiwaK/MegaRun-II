import sys
import os
import json
import argparse

from colorama import Fore, Style, Back, init
from box import Box
import time
import threading
import logging

sys.path.append('src')
from supper_app import SupperApp as WOW
# from supper_app import Signin
from config import Config
from logger import logger
from utill import Utill
from browser import Browser
from game import RaidShooter
from game import FoodBlocks

"""
TODO
- add average reward for a win
- add override option for no chances left
- add override option for continue play on browser
- fix version checking
"""

class CLUI:

	def __init__(self, instance):
		init()
		self.data = instance.config.printx
		logHandler = CustomLogHandler(instance)
		logHandler.setFormatter(CustomFormatter())
		logger.addHandler(logHandler)

	def eraseLines(self, n):
		for _ in range(n):
			print("\033[F\033[K", end="")

	def printx(self):
		
		data = self.data
		width, height = 110, 17
		ratio_top = 0.30  # Ratio for the top section

		symbol_game = " ⌬ "
		symbol_gift = " ◈ "
		symbol_log  = " ⎆ "
		symbol_stat = " ⌗ "
		game = data.game
		gift = data.gift
		log  = data.log
		stat = data.stat

		RESET = Style.RESET_ALL
		OWNER = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
		BORDER = Fore.LIGHTBLACK_EX + Back.BLACK
		SECTION_NAME = Fore.LIGHTBLACK_EX + Back.BLACK

		SYMBOL_GAME = Fore.LIGHTBLUE_EX 
		HEADER_GAME = Fore.LIGHTWHITE_EX
		TEXT_GAME   = Fore.LIGHTMAGENTA_EX

		SYMBOL_GIFT = Fore.LIGHTRED_EX
		HEADER_GIFT = Fore.LIGHTWHITE_EX
		TEXT_GIFT   = Fore.LIGHTGREEN_EX

		SYMBOL_LOG  = Fore.LIGHTYELLOW_EX
		TEXT_LOG    = Fore.LIGHTWHITE_EX

		SYMBOL_STAT = Fore.LIGHTRED_EX
		HEADER_STAT = Fore.LIGHTWHITE_EX
		TEXT_STAT   = Fore.LIGHTGREEN_EX

		text_1 = [
			SYMBOL_GAME + symbol_game + HEADER_GAME + "Name: " + TEXT_GAME + game.name, 
			SYMBOL_GAME + symbol_game + HEADER_GAME + "UUID: " + TEXT_GAME + game.uuid, 
			SYMBOL_GAME + symbol_game + HEADER_GAME + "SID : " + TEXT_GAME + game.session]
		text_2 = [
			SYMBOL_GIFT + symbol_gift + HEADER_GIFT + "Total  : " + TEXT_GIFT + gift.total, 
			SYMBOL_GIFT + symbol_gift + HEADER_GIFT + "Remains: " + TEXT_GIFT + gift.remains, 
			SYMBOL_GIFT + symbol_gift + HEADER_GIFT + "History: " + TEXT_GIFT + gift.history,
			SYMBOL_GIFT + symbol_gift + HEADER_GIFT + "Next in: " + TEXT_GIFT + gift.next]
		text_3 = [
			SYMBOL_LOG + symbol_log + TEXT_LOG + x for x in log]
		text_4 = [
			SYMBOL_STAT + symbol_stat + HEADER_STAT + "Total gift req: " + TEXT_STAT + stat.total_gift_req,
			SYMBOL_STAT + symbol_stat + HEADER_STAT + "Total run time: " + TEXT_STAT + stat.total_run_time,
			SYMBOL_STAT + symbol_stat + HEADER_STAT + "Failed gift req: " + TEXT_STAT + stat.failed_gift_req
			]

		# Calculate row counts for each section based on the ratio
		top_section_height = int(height * ratio_top)
		bottom_section_height = height - top_section_height - 2
		
		# Borders and empty rows with selective colors
		reset = Style.RESET_ALL
		top_border = (
			BORDER + "┏" + "━" * (width // 2 - 8) + SECTION_NAME + " Game " +
			BORDER + "━┳" + "━" * (width // 2 - 8) + SECTION_NAME + " Gift " +
			BORDER + "━┓" + reset
		)
		mid_horizontal = (
			BORDER + "┣" + "━" * (width // 2 - 7) + " Log " +  "━╋" +
			"━" * (width // 2 - 8) + SECTION_NAME + " Stat " +
			BORDER + "━┫" + reset
		)
		bottom_border = (
			BORDER + "┗" + "━" * (width // 2 - 1) + "┻" + 
			"━" * (width // 2 - 10) + 
			" thiwaK " + BORDER + "━┛" + reset + "\n")
		
		empty_row_upper = BORDER + "┃" + reset + " " * (width // 2 - 1) + BORDER + "┃" + reset + " " * (width // 2 - 1) + BORDER + "┃" + reset
		empty_row_lower = BORDER + "┃" + reset + " " * (width - 1) + BORDER + "┃" + reset
		
		# Build the bordered output
		output = []
		output.append(top_border)
		
		# Add rows for the upper section (with a horizontal split in the middle)
		for i in range(top_section_height):
			t1_rows = text_1[:top_section_height - 1]
			t2_rows = text_2[:top_section_height - 1]

			# Match row counts for t1_rows and t2_rows
			if len(t1_rows) != len(t2_rows) and max(len(t1_rows), len(t2_rows)) > i:
				if len(t1_rows) > len(t2_rows):
					t2_rows += [Back.BLACK*3 + " " for _ in range(len(t1_rows) - len(t2_rows))]
				else:
					t1_rows += [Back.BLACK*3 + " " for _ in range(len(t2_rows) - len(t1_rows))]

			if len(t1_rows) == len(t2_rows) and max(len(t1_rows), len(t2_rows)) > i:
				parta = BORDER + "┃" + reset + t1_rows[i].ljust(width // 2 - 1 + 15) + BORDER + "┃" + reset
				partb = t2_rows[i].ljust(width // 2 - 1 + 15) + BORDER + "┃" + reset
				output.append(parta + partb)
				continue
			output.append(empty_row_upper)
		
		# Horizontal split for the upper part
		output.append(mid_horizontal)
		
		# Add rows for the lower section (without any split)
		for i in range(bottom_section_height):
			t3_rows = text_3
			t4_rows = text_4

			# Match row counts for t3_rows and t4_rows
			if len(t3_rows) != len(t4_rows) and max(len(t3_rows), len(t4_rows)) > i:
				if len(t3_rows) > len(t4_rows):
					t4_rows += [Back.BLACK*3 + " " for _ in range(len(t3_rows) - len(t4_rows))]
				else:
					t3_rows += [Back.BLACK*3 + " " for _ in range(len(t4_rows) - len(t3_rows))]

			if len(t3_rows) == len(t4_rows) and max(len(t3_rows), len(t4_rows)) > i:
				parta = BORDER + "┃" + reset + t3_rows[i].ljust(width // 2 - 1 + 10) + BORDER + "┃" + reset
				partb = t4_rows[i].ljust(width // 2 - 1 + 15) + BORDER + "┃" + reset
				output.append(parta + partb)
				continue

			output.append(empty_row_upper)
		
		output.append(bottom_border)
		
		# Print the result
		for line in output:
			print(line)

	def printx_call(self):
		while True:
			self.printx()
			time.sleep(1)
			self.eraseLines(19)

class CustomFormatter(logging.Formatter):
	def format(self, record):
		timestamp = str(time.time_ns() // 1000000)
		event = record.levelname
		message = record.getMessage()
		return f"[{timestamp}] [{event[0]}] {message}"

class CustomLogHandler(logging.Handler):
	def __init__(self, instance):
		super().__init__(logging.INFO)  # Only handle INFO level and above
		self.instance = instance

	def emit(self, record):
		# Only append INFO level logs to self.data.log
		if record.levelno == logging.INFO:
			log_message = self.format(record)
			self.instance.config.printx.log.append(log_message)

class Main:
	"""Main class"""

	def __init__(self, config_file='config.js', force_secondary_config=False, update_token=False,
		skip_warn=False, keep_play_in_browser=False, continue_on_chances_over=False):
		self.configObj = Config(config_file)
		self.config = self.configObj.load(force_secondary_config)
		self.config.file = config_file
		self.config['skip_warn'] = skip_warn
		self.config['keep_play_in_browser'] = keep_play_in_browser
		self.config['continue_on_chances_over'] = continue_on_chances_over
		self.ui = CLUI(self)
		self.utill  = Utill(self)
		self.wow = WOW(self)

		if os.name != 'nt':
			logger.error("Unsupported Opertating System. Only works with NT systems.")
			sys.exit(1)

		logger.info("==================================================")

		# ui_thread = threading.Thread(target=self.ui.printx_call, daemon=True)
		# ui_thread.start()

		if update_token:
			self.getAccessToken()


		# s = Signin(self)
		# s.start()
	
	# Kind a mess. Should be cleard
	def checkToken(self):
		logger.info(":checkToken:")

		r = self.utill.validateJWT(self.config.refreshCode)
		if r == 400:
			logger.warning("Refresh token expired. Update manually.")
			exit()
		elif r == 200:
			logger.debug("Refresh token OK")
		else:
			logger.error("Unknown")
			exit()


		r = self.utill.validateJWT(self.config.accessToken)
		if r == 400:
			logger.info("Updating access token")
			r = self.getAccessToken()

			if r == 403:
				logger.warning("Unauthorized. Manual investigation required")
				exit()

			elif r == 200:
				logger.info("Access token updated")
				
			else:
				logger.error("Unknown")
				exit()
		elif r == 200:
			logger.debug("Access token OK")
		else:
			logger.error("Unknown", r)
			exit()

	def checkout(self):
		#stage 1
		r = self.wow.checkout()
		if r == None:
			exit()

		elif 'statusCode' in r:
			logger.debug(r)
		else:
			logger.error("Unknown")
			exit()

		# stage 2
		r = self.wow.checkUpdates()
		if r == None:
			logger.warning("Unable to get update info")
		else:
			if self.config.appVersion != r.version:
				logger.warning("New update avilable")
				tmp_ = f"\n  Current version: {self.config.appVersion}"
				tmp_ += f"\n  Avilable version: {r.version}"
				tmp_ += f"\n  Last update: {r.date}"
				tmp_ += f"\n  Message: {r.message}"
				tmp_ += f"\n"

				print(tmp_)
				if not self.config.skip_warn: exit()


	def getMegaWasana(self):
		if not self.wow.getMegaWasana():
			logger.error("Unknown")
			exit()

	def getUserPrimaryInfo(self):
		r = self.wow.getUserPrimaryInfo()
		if r == None:
			logger.error("Unknown")
			exit()

		rr = self.utill.decrypt(r, self.config.encryptionKey)
		if rr != None:
			logger.debug(rr)
		else:
			logger.error("Unknown")
			logger.error(rr)
			exit()

	def getUserInfo(self):
		r = self.wow.getUserInfo()
		if r == None:
			logger.error("Unknown")
			exit()

		rr = self.utill.decrypt(r, self.config.encryptionKey)
		if rr != None:
			logger.debug(rr)
		else:
			logger.error("Unknown")
			logger.error(r)
			exit()

	def getBanners(self):
		r = self.wow.getBanners()
		if r == None:
			logger.error("Unknown")
			exit()

	def authorizeMegaApp(self):
		r = self.wow.authorizeMegaApp()
		if r == None:
			logger.error("Unknown")
			exit()

		if r['statusCode'] != 200:
			logger.error("Unknown")
			exit()

		rr = self.utill.decrypt(r['data'], self.config.encryptionKey)
		if rr != None:
			rr = json.loads(rr)
			logger.debug(rr)
			self.GAME_LAUNCHER_URL = rr['redirectUrl']
			self.GAME_LAUNCHER_TOKEN = rr['token']
		else:
			logger.error("Unknown")
			logger.error(r)
			exit()

	def getAccessToken(self):
		r = self.wow.getAccessToken()
		if r == None:
			exit()

		elif r['statusCode'] == 200:
			data = r['data']['data']
			self.configObj.update("refreshCode", data['refreshCode'])
			self.configObj.update("accessToken", data['accessToken'])
			# self.configObj.update("accessTokenExp", data['exp'])
			# self.configObj.update("refreshCodeExp", data['refreshCodeExp'])

		else:
			logger.error("Unknown")
			exit()

	def userUpdate(self):
		r = self.wow.userUpdate()
		if r == None:
			logger.error("Unknown")
			exit()

	def updateFCMToken(self):
		r = self.api.supperApp.updateFCMToken()
		if r == None:
			logger.error("Unknown")
			exit()

		rr = self.utill.decrypt(r, self.config.encryptionKey)
		if rr == None:
			logger.error("Unknown")
			exit()

		logger.debug(rr)
		rr = self.utill.decrypt(json.loads(rr)['fcmToken'], self.config.config_Key)
		if rr == None:
			logger.error("Unknown")
			exit()
		
		self.configObj.update("fcmToken", rr)

	def start(self):
		self.checkToken()
		self.checkout()
		self.getMegaWasana()
		self.getUserPrimaryInfo()
		self.getUserInfo()
		self.getBanners()
		self.authorizeMegaApp()
	
		self.browser = Browser(self.GAME_LAUNCHER_URL, self.GAME_LAUNCHER_TOKEN, self)
		self.gameArenaConfig, self.currentGame = self.browser.launch()
		self.gamePlaying = None

		if self.currentGame.game.name == "Raid Shooter":
			self.gamePlaying = RaidShooter(self, self.currentGame)
			self.gamePlaying.getInfo()
			
		elif self.currentGame.game.name == "Food Blocks":
			self.gamePlaying = FoodBlocks(self, self.currentGame)
			self.gamePlaying.getInfo()

		while self.gamePlaying != None:
			self.gamePlaying.randomGifts()
			self.gamePlaying.getInfo()
			self.gamePlaying.printx()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="MeagaRun II Client")
	parser.add_argument("--config", "-c", type=str, default='config.js', help="Specify the path to the configuration file.")
	parser.add_argument("--secondary-config", "-c2", action="store_true", help="Force load secondary configuration.")
	parser.add_argument("--update-token", action="store_true", help="Update authentication token.")
	parser.add_argument("--skip-warn", action="store_true", help="Force contune in warning situation.")

	args = parser.parse_args()
	main = Main(config_file=args.config, force_secondary_config=args.secondary_config, update_token=args.update_token,
		skip_warn=args.skip_warn)
	
	try:
		main.start()
	except KeyboardInterrupt as e:
		exit()
	
