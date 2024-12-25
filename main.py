import sys
import os
import json
import argparse

from box import Box
import time
from datetime import datetime
import threading
import logging
import re
import random

import ctypes, struct
from rich.console import Console
from rich.text import Text

sys.path.append('src')
from ui import CLUI
from wow import SupperApp as WOW
# from supper_app import Signin
from config import Config
# from logger import logger
from utils import Utils
from browser import Browser
from game import RaidShooter
from game import FoodBlocks




"""
TODO
- add stat section
"""


class Main:
	"""Main class"""

	version_support = "1.8.6"

	def __init__(self, config_file='config.js', force_secondary_config=False, update_token=False,
		skip_warn=False, keep_play_in_browser=False, continue_on_chances_over=False, minimal_ui=False):
		self.configObject = Config(config_file)
		self.config = self.configObject.load(force_secondary_config)
		self.config.file = config_file
		self.config.skip_warn = skip_warn
		self.config.keep_play_in_browser = keep_play_in_browser
		self.config.continue_on_chances_over = continue_on_chances_over
		self.config.minimal_ui = minimal_ui
		if not minimal_ui:
			self.ui = CLUI(self)

		else:
			class UI:
				def __init__(self, instance):
					from logger import Logger
					instance.logger = Logger.getConsoleLogger()
			
			self.ui = UI(self)


		self.utils  = Utils(self)
		self.wow = WOW(self)

		if os.name != 'nt':
			self.logger.error("Unsupported Opertating System. Only works with NT systems.")
			sys.exit(1)

		if not simple_ui:
			ui_thread = threading.Thread(target=self.ui.show, daemon=True)
			ui_thread.start()
			time.sleep(0.1)

		self.logger.info("==================================================")		

		if update_token:
			self.getAccessToken()


		# s = Signin(self)
		# s.start()
	
	# Kind a mess. Should be cleard
	def checkToken(self):
		self.logger.info(":checkToken:")

		r = self.utils.validateJWT(self.config.refreshCode)
		if r == 400:
			self.logger.warning("Refresh token expired. Update manually.")
			exit()
		elif r == 200:
			self.logger.debug("Refresh token OK")
		else:
			self.logger.error("Unknown")
			exit()


		r = self.utils.validateJWT(self.config.accessToken)
		if r == 400:
			self.logger.info("Updating access token")
			r = self.getAccessToken()

			if r == 403:
				self.logger.warning("Unauthorized. Manual investigation required")
				exit()

			elif r == 200:
				self.logger.info("Access token updated")
				
			else:
				self.logger.error("Unknown")
				exit()
		elif r == 200:
			self.logger.debug("Access token OK")
		else:
			self.logger.error("Unknown", r)
			exit()

	def checkout(self):
		#stage 1
		r = self.wow.checkout()
		if r == None:
			exit()

		elif 'statusCode' in r:
			self.logger.debug(r)
		else:
			self.logger.error("Unknown")
			exit()

		# stage 2
		r = self.wow.checkUpdates()
		if r == None:
			self.logger.warning("Unable to get update info")
		else:
			if self.version_support != r.version:
				self.logger.warning("New update avilable")
				tmp_ = f"\n  Current version: {self.config.appVersion}"
				tmp_ += f"\n  Avilable version: {r.version}"
				tmp_ += f"\n  Last update: {r.date}"
				tmp_ += f"\n  Message: {r.message}"
				tmp_ += f"\n"

				self.logger.debug(tmp_)
				if not self.config.skip_warn: exit()


	def getMegaWasana(self):
		r = self.wow.getMegaWasana()
		if not r:
			self.logger.error("Unknown")
			exit()

		if r['statusCode'] != 200:
			self.logger.error("Unknown")
			exit()

		for item in r['data']['reward']['breackDown']:
			account = item['account']
			chances = item['chances']

			if chances > 0:
				self.logger.info(f"{account} got {chances} chances")

	def getUserPrimaryInfo(self):
		r = self.wow.getUserPrimaryInfo()
		if r == None:
			self.logger.error("Unknown")
			exit()

		rr = self.utils.decrypt(r, self.config.encryptionKey)
		if rr != None:
			self.logger.debug(rr)
		else:
			self.logger.error("Unknown")
			self.logger.error(rr)
			exit()

	def getUserInfo(self):
		r = self.wow.getUserInfo()
		if r == None:
			self.logger.error("Unknown")
			exit()

		rr = self.utils.decrypt(r, self.config.encryptionKey)
		if rr != None:
			self.logger.debug(rr)
		else:
			self.logger.error("Unknown")
			self.logger.error(r)
			exit()


	def getBanners(self):
		r = self.wow.getBanners()
		if r == None:
			self.logger.error("Unknown")
			exit()

		for item in r:
			image = item['image']
			link = item['link']
			startDate = item['startDate']
			endDate = item['endDate']
			
			self.logger.debug({'image':image, 'link':link, 'startDate':startDate, 'endDate':endDate})
			

	def authorizeMegaApp(self):
		r = self.wow.authorizeMegaApp()
		if r == None:
			self.logger.error("Unknown")
			exit()

		if r['statusCode'] != 200:
			self.logger.error("Unknown")
			exit()

		rr = self.utils.decrypt(r['data'], self.config.encryptionKey)
		if rr != None:
			rr = json.loads(rr)
			self.logger.debug(rr)
			self.config.GAME_LAUNCHER_URL = rr['redirectUrl']
			self.config.GAME_LAUNCHER_TOKEN = rr['token']
		else:
			self.logger.error("Unknown")
			self.logger.error(r)
			exit()

	def getAccessToken(self):
		r = self.wow.getAccessToken()
		if r == None:
			exit()

		elif r['statusCode'] == 200:
			data = r['data']['data']
			self.configObject.update("refreshCode", data['refreshCode'])
			self.configObject.update("accessToken", data['accessToken'])
			# self.configObj.update("accessTokenExp", data['exp'])
			# self.configObj.update("refreshCodeExp", data['refreshCodeExp'])

		else:
			self.logger.error("Unknown")
			exit()

	def userUpdate(self):
		r = self.wow.userUpdate()
		if r == None:
			self.logger.error("Unknown")
			exit()

	def updateFCMToken(self):
		r = self.api.supperApp.updateFCMToken()
		if r == None:
			self.logger.error("Unknown")
			exit()

		rr = self.utils.decrypt(r, self.config.encryptionKey)
		if rr == None:
			self.logger.error("Unknown")
			exit()

		self.logger.debug(rr)
		rr = self.utils.decrypt(json.loads(rr)['fcmToken'], self.config.config_Key)
		if rr == None:
			self.logger.error("Unknown")
			exit()
		
		self.configObject.update("fcmToken", rr)

	def start(self):
		self.checkToken()
		# time.sleep(1)
		# exit()
		self.checkout()
		self.getMegaWasana()
		self.getUserPrimaryInfo()
		self.getUserInfo()
		self.getBanners()
		self.authorizeMegaApp()
	
		self.browser = Browser(self)
		browserOut = self.browser.launch()
		if self.config != browserOut:
			self.config.update(browserOut)

		self.gamePlaying = None

		if self.config.currentGame.game.name == "Raid Shooter":
			self.gamePlaying = RaidShooter(self)
			self.gamePlaying.getInfo()
			
		elif self.config.currentGame.game.name == "Food Blocks":
			self.gamePlaying = FoodBlocks(self)
			self.gamePlaying.getInfo()

		while self.gamePlaying != None:
			self.gamePlaying.randomGifts()
			self.gamePlaying.getInfo()
			# self.gamePlaying.printx()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="MeagaRun II Client")
	parser.add_argument("--config", "-c", type=str, default='config.js', help="Specify the path to the configuration file.")
	parser.add_argument("--secondary-config", "-c2", action="store_true", help="Force load secondary configuration.")
	parser.add_argument("--update-token", action="store_true", help="Update authentication token.")
	parser.add_argument("--skip-warn", action="store_true", help="Force contune in warning situation.")
	parser.add_argument("--ignore-chances-limit", action="store_true", help="Prevent the app from auto-terminating when chances are over.")
	parser.add_argument("--browser-mode", action="store_true", help="Allow gameplay to continue in the browser.")
	parser.add_argument("--minimal-ui", action="store_true", help="Show minimal UI.")

	args = parser.parse_args()
	main = Main(config_file=args.config, force_secondary_config=args.secondary_config, update_token=args.update_token,
		skip_warn=args.skip_warn, keep_play_in_browser=args.browser_mode, continue_on_chances_over=args.ignore_chances_limit,
		minimal_ui=args.minimal_ui)
	
	try:
		main.start()
		print("\033[0m")
	except KeyboardInterrupt as e:
		print("\033[0m")
		exit()
	
