from box import Box
import httpx
import json
# from logger import logger
import time
import random
import subprocess
import os

class Game:
	"""Games"""

	def __init__(self, instance):
		self.ui = instance.ui
		self.logger = instance.logger
		self.config = instance.config
		self.gameConfig = instance.config.currentGame
		self.noGiftsWarnLimit = 15
		self.lastGifts = ['*' for x in range(self.noGiftsWarnLimit)]

		self.chances_got = 0
		self.chances_left = 0
		self.data_got = 0
		self.data_left = 0
		self.past_gifts = ""

		self.staticNumber = random.randint(1, 9)
		self.giftCount = 1

		self.firstPrint = True

		timeout = httpx.Timeout(10.0)
		self.conn = httpx.Client(base_url='https://dshl99o7otw46.cloudfront.net', http2=True, timeout=timeout)
		self.headers = {
			'Referer': self.gameConfig.game.url + '?platform=pwa&version=200',
			'sec-ch-ua-platform': "Android",
			'sec-ch-ua': '"Chromium";v="130", "Android WebView";v="130", "Not?A_Brand";v="99"',
			'Sec-Fetch-Site': 'same-origin',
			'Sec-Fetch-Mode': 'cors',
			'Sec-Fetch-Dest': 'empty',
			"accept": "application/json, text/plain, */*",
			"content-type": "application/json",
			'Accept-Encoding': 'gzip, deflate, br, zstd',
			'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
			"user-agent": self.config.user_agent
		}
		self.headers.update({'authorization': 'Bearer ' + self.gameConfig.access_token})

	def highScore(self):
		
		self.self.logger.info(":highScore:")
		headers = self.headers

		try:
			resp = self.conn.request(method='GET', url=f'/api/game/v1/leaderboard/global/high-score/{self.gameConfig.game.uuid}', headers=headers)
		except httpx.ConnectError:
			self.self.logger.debug("Connect Error")
			return
		except httpx.ReadTimeout as e:
			self.self.logger.debug("Read Timeout")
			return


		if int(resp.status_code) == 200:
			res = resp.read()
			js = json.loads(res)
			if js['statusInfo'] == "OK":
				self.self.logger.debug(js['data'])
		else:
			self.self.logger.error(resp.status_code)
			self.self.logger.error(resp.read())
		
	def assets(self):
		
		self.logger.info(":assets:")
		headers = self.headers

		try:
			resp = self.conn.request(method='GET', url=f'/api/game/v1/asset/{self.gameConfig.game.uuid}', headers=headers)
		except httpx.ConnectError:
			self.logger.debug("Connect Error")
			return
		except httpx.ReadTimeout as e:
			self.logger.debug("Read Timeout")
			return
		except httpx.ConnectTimeout:
			self.logger.debug("Connect Timeout")
			return
		

		if int(resp.status_code) == 200:
			res = resp.read()
			js = json.loads(res)
			if js['statusInfo'] == "OK":
				self.logger.debug(js['data'])
		else:
			self.logger.error(resp.status_code)
			self.logger.error(resp.read())
		
	def getInfo(self):

		self.logger.debug(":getInfo:")
		headers = self.headers
		try:
			resp = self.conn.request(method='GET', url=f'api/game/v1/profile/data', headers=headers)
		except httpx.ReadTimeout as e:
			self.logger.debug("Read Timeout")
			return
		except httpx.ConnectError:
			self.logger.debug("Connect Error")
			return
		except httpx.ConnectTimeout:
			self.logger.debug("Connect Timeout")
			return
		
		if int(resp.status_code) == 200:
			res = resp.read()
			js = Box(json.loads(res))
			if js['statusInfo'] == "OK":
				self.logger.debug(js.data)
				
				self.chances_got = js.data.consumed_chances
				self.chances_left = js.data.daily_winning_chances
				self.data_got = js.data.won_data
				self.data_left = js.data.remaining_data
				self.past_gifts = " ".join([str(x) for x in self.lastGifts])

				self.ui.data["Game Info"]["Chances"] = f"{self.chances_got} ({self.chances_left})"
				self.ui.data["Game Info"]["Reward "] = f"{self.data_got} ({int(self.data_left) + int(self.data_got)})"

				self.logger.debug(f"Chances {js.data.consumed_chances}/{js.data.daily_winning_chances} Data {js.data.won_data}/{js.data.remaining_data}")
		
				if (not self.config.continue_on_chances_over) and js.data.consumed_chances >= js.data.daily_winning_chances:
					self.logger.info("No chances left")
					self.logger.warning("Self terminating")
					exit()
				

		elif int(resp.status_code) == 502:
			self.logger.warning("Bad Gateway")
			return
		else:
			self.logger.error(resp.status_code)
			self.logger.error(resp.read())

	def printx(self):

		def eraseLines(n):
			for _ in range(n):
				print("\033[F\033[K", end="")

		msg =   f'Chances : {self.chances_got} out of {self.chances_left}\n'
		msg +=  f'Data    : {self.data_got} out of {int(self.data_left) + int(self.data_got)}\n'
		msg +=  f'Gifts   : [{self.past_gifts}]\n'

		if self.firstPrint:
			self.firstPrint = False
			print(f"{msg}", end="")
		else:
			eraseLines(4)
			print(f"{msg}", end="", flush=True)

	def giftResponseParser(self, response):

		msg = ""
		if int(response.status_code) == 200:
			res = response.read()
			js = json.loads(res)
			if js['statusInfo'] == "OK":
				self.logger.debug(js['data'])

				self.lastGifts = self.lastGifts[1:]
				self.lastGifts.append(str(js['data']['amount']))

				self.ui.gift_history.append(str(js['data']['amount']))

				if self.lastGifts.count('*') == 0 and sum([int(str(x)) for x in self.lastGifts if str(x).isdecimal()]) < 1:
					self.logger.warning(f"No gifts for last {self.noGiftsWarnLimit} requests")
		
		elif int(response.status_code) == 502:
			self.logger.warning("Bad Gateway")
			self.lastGifts.append('@')
			return
		else:
			self.logger.debug(response.status_code)
			self.logger.debug(response.read())
			exit()

	def getRandomGift(self, body, headers):
		try:
			resp = self.conn.request(method='POST', url=f'/api/game/v1/game-session/random-gift/{self.gameConfig.sessionId}/1', data=body, headers=headers)
		except httpx.ReadTimeout as e:
			self.logger.debug("Read Timeout")
			self.lastGifts.append('#')
			return
		except httpx.ConnectTimeout:
			self.logger.debug("Connect Timeout")
			self.lastGifts.append('#')
			return
		except httpx.ConnectError:
			self.logger.debug("Connect Error")
			self.lastGifts.append('#')
			return

		self.giftResponseParser(resp)

	def getGiftKey(self):
		game = None
		if self.gameConfig.game.name == "Raid Shooter": game = "RS"
		elif self.gameConfig.game.name == "Food Blocks": game = "FB"
		elif self.gameConfig.game.name == "Ghost Hunter": game = "FB"
		elif self.gameConfig.game.name == "Cake Zone": game = "FB"
		elif self.gameConfig.game.name == "Mega Run 2": game = "MR"
		else: 
			self.logger.error(f"Invalid game: {self.gameConfig.game.name}")
			exit()
		try:
			command = ["node", r"bin\keygen.js", str(self.staticNumber),
			str(self.giftCount), game]
			result = subprocess.run(command, capture_output=True, text=True, shell=True)
			output = result.stdout.strip()
			error = result.stderr.strip()

			if error:
				self.logger.error("subprocess error: " + error)
			if output:
				key = output

			self.logger.debug(f"gift key: {self.staticNumber} {self.giftCount} {game} -> {key}")
			return key

		except subprocess.CalledProcessError as e:
			self.logger.error(e)
			return None

		except UnicodeDecodeError as e:
			self.logger.error(e)
			return None

class RaidShooter(Game):
	"""Raid Shooter"""

	def __init__(self, instance):
		super().__init__(instance)

		self.config = instance.config
		self.gameConfig = instance.config.currentGame

		self.previous_gift = time.time()
		self.SCORE = self.gameConfig.score
		self.MAX_SHOTS = 7
		self.BULLS_EYE = 20
		self.RED_ZONE = 10
		self.BLACK_ZONE = 5
		# OUTER_ZONE = 0
		# MISS_TARGET = None
		
		self.MAX_BLACK_ZONE = 1
		self.MAX_RED_ZONE = 3

		self.MAX_WAITING_TIME = 5
		self.MIN_WAITING_TIME = 2

	def randomGifts(self):
		self.logger.debug(":randomGifts:")

		self.giftCount += 1

		waiting_time = [random.randint(self.MIN_WAITING_TIME, self.MAX_WAITING_TIME) for _ in range(self.MAX_SHOTS)]
		self.ui.next_beginning = int(time.time())
		self.ui.next_end = int(time.time()) + sum(waiting_time)

		self.logger.debug(f"Waiting time {waiting_time}")
		time.sleep(sum(waiting_time))

		black = [self.BLACK_ZONE for _ in range(self.MAX_BLACK_ZONE)]
		red = [self.RED_ZONE for _ in range(self.MAX_RED_ZONE)]
		eye = [self.BULLS_EYE for _ in range(self.MAX_SHOTS - (len(black) + len(red)))] 
		values = eye + red + black

		random_scores = [random.choice(values) for _ in range(self.MAX_SHOTS)]
		self.logger.debug(f"Random score {random_scores}")

		self.SCORE += sum(random_scores)
		self.logger.debug(f"Total score {self.SCORE}")

		body = {'score':self.SCORE}
		body = json.dumps(body)

		headers = self.headers
		giftKey = self.getGiftKey()
		if giftKey == None:
			self.logger.error(f"Invalid giftKey: {giftKey}")
			exit()
		headers.update({'Idempotency-Key': giftKey,
		'Content-Type': 'application/json',
		'sec-ch-ua-mobile': '?1',
		'Accept': '*/*',
		'Origin': 'https://dshl99o7otw46.cloudfront.net',
		'X-Requested-With': 'lk.wow.superman',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Cookie': '_ga=GA1.1.182677110.1730624223; _ga_1DWHZJ5VCF=GS1.1.1730624223.1.1.1730624622.40.0.1890109501'})

		time_diff = time.time() - self.previous_gift
		self.logger.debug(f"Time diff: {time_diff}")

		# if random.randint(0, 1) == 0:
		# 	return

		self.previous_gift = time.time()
		
		self.getRandomGift(body, headers)

class FoodBlocks(Game):
	"""Food Blocks"""

	def __init__(self, instance):
		super().__init__(instance)

		self.config = instance.config
		self.ui = instance.ui
		self.gameConfig = instance.config.currentGame

		self.previous_gift = time.time()
		self.SCORE = self.gameConfig.score
		self.MAX_WAITING_TIME = 23
		self.MIN_WAITING_TIME = 13
		self.MAX_SCORE = 40
		self.MIN_SCORE = 20

	def map_score_to_time(self, score):

		if score < self.MIN_SCORE or score > self.MAX_SCORE:
			raise ValueError("Score is out of range: " + str(score))

		# Linear interpolation formula
		waiting_time = self.MIN_WAITING_TIME + (
			(score - self.MIN_SCORE) / (self.MAX_SCORE - self.MIN_SCORE)
		) * (self.MAX_WAITING_TIME - self.MIN_WAITING_TIME)

		if waiting_time < self.MIN_WAITING_TIME or waiting_time > self.MAX_WAITING_TIME:
			raise ValueError("Waiting time is out of range: " + str(waiting_time))

		return waiting_time

	def randomGifts(self):
		self.logger.debug(":randomGifts:")

		self.giftCount += 1

		random_score = random.randint(self.MIN_SCORE, self.MAX_SCORE)
		waiting_time = self.map_score_to_time(random_score)

		self.logger.debug(f"Waiting time {waiting_time}")

		self.ui.next_beginning = int(time.time())
		self.ui.next_end = int(time.time()) + waiting_time
		time.sleep(waiting_time)
		self.logger.debug(f"Random score {random_score}")


		self.SCORE += random_score
		self.logger.debug(f"Total score {self.SCORE}")

		body = {'score':self.SCORE}
		body = json.dumps(body)

		headers = self.headers
		giftKey = self.getGiftKey()
		if giftKey == None:
			self.logger.error(f"Invalid giftKey: {giftKey}")
			exit()

		headers.update({'Idempotency-Key': giftKey,
		'Content-Type': 'application/json',
		'sec-ch-ua-mobile': '?1',
		'Accept': '*/*',
		'Origin': 'https://dshl99o7otw46.cloudfront.net',
		'X-Requested-With': 'lk.wow.superman',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Cookie': '_ga=GA1.1.182677110.1730624223; _ga_1DWHZJ5VCF=GS1.1.1730624223.1.1.1730624622.40.0.1890109501'})

		time_diff = time.time() - self.previous_gift
		self.logger.debug(f"Time diff: {time_diff}")

		# if random.randint(0, 1) == 0:
		# 	return

		self.previous_gift = time.time()

		self.getRandomGift(body, headers)

		

		

