import sys
import os
import json
import argparse

sys.path.append('src')
from supper_app import SupperApp as WOW
from config import Config
from logger import logger
from utill import Utill
from browser import Browser
from game import RaidShooter

class Main:
	"""Main class"""

	def __init__(self, config_file='config.js', force_secondary_config=False, update_token=False):
		
		self.configObj = Config(config_file)
		self.config = self.configObj.load(force_secondary_config)
		
		self.utill  = Utill(self)
		self.wow = WOW(self)

		logger.info("==================================================")

		if update_token:
			self.getAccessToken()
	
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
		r = self.wow.checkout()
		if r == None:
			exit()

		elif 'statusCode' in r:
			logger.debug(r)
		else:
			logger.error("Unknown")
			exit()

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

		self.raidShooter = RaidShooter(self, self.currentGame)
		self.raidShooter.getInfo()
		
		while True:
			self.raidShooter.randomGifts()
			self.raidShooter.getInfo()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="MeagaRun II Client")
	parser.add_argument("--config", "-c", type=str, default='config.js', help="Specify the path to the configuration file.")

	parser.add_argument("--secondary-config", action="store_true", help="Force load secondary configuration.")
	parser.add_argument("--update-token", action="store_true", help="Update authentication token.")

	args = parser.parse_args()
	main = Main(config_file=args.config, force_secondary_config=args.secondary_config, update_token=args.update_token)
	
	try:
		main.start()
	except KeyboardInterrupt as e:
		exit()
	
