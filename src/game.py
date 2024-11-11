from box import Box
import httpx
import json
from logger import logger
import time
import random

class Game:
	"""Games"""

	def __init__(self, instance, game_config):
		self.config = instance.config
		self.gameConfig = game_config

	def highScore(self):
		
		logger.info(":highScore:")
		headers = self.headers

		resp = self.conn.request(method='GET', url=f'/api/game/v1/leaderboard/global/high-score/{self.gameConfig.game.uuid}', headers=headers)
		if int(resp.status_code) == 200:
			res = resp.read()
			js = json.loads(res)
			if js['statusInfo'] == "OK":
				logger.debug(js['data'])
		else:
			print(resp.status_code)
			print(resp.read())

	def assets(self):
		
		logger.info(":assets:")
		headers = self.headers

		resp = self.conn.request(method='GET', url=f'/api/game/v1/asset/{self.gameConfig.game.uuid}', headers=headers)
		if int(resp.status_code) == 200:
			res = resp.read()
			js = json.loads(res)
			if js['statusInfo'] == "OK":
				logger.debug(js['data'])
		else:
			print(resp.status_code)
			print(resp.read())

	def getInfo(self):

		logger.info(":getInfo:")
		headers = self.headers

		resp = self.conn.request(method='GET', url=f'api/game/v1/profile/data', headers=headers)
		if int(resp.status_code) == 200:
			res = resp.read()
			js = Box(json.loads(res))
			if js['statusInfo'] == "OK":
				logger.debug(js.data)

				if js.data.consumed_chances >= js.data.daily_winning_chances:
					logger.info("No chances avilable")
					logger.warning("Terminating")
					exit()

				logger.info(f"Chances {js.data.consumed_chances}/{js.data.daily_winning_chances} Data {js.data.won_data}/{js.data.remaining_data}")
		else:
			print(resp.status_code)
			print(resp.read())


class RaidShooter(Game):
	"""RaidShooter"""

	def __init__(self, instance, game_config):
		super().__init__(instance, game_config)

		self.config = instance.config
		self.gameConfig = game_config

		self.previous_gift = time.time()
		self.conn = httpx.Client(base_url='https://dshl99o7otw46.cloudfront.net', http2=True)
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

		self.SCORE = self.gameConfig.score
		self.BULLS_EYE = 20
		self.RED_ZONE = 10
		self.BLACK_ZONE = 5
		# OUTER_ZONE = 0
		# MISS_TARGET = None

	def randomGifts(self):
		logger.info(":randomGifts:")

		waiting_time = [random.randint(3, 10) for _ in range(7)]
		logger.info(f"Waiting time {waiting_time}")
		time.sleep(sum(waiting_time))

		values = [self.BULLS_EYE, self.RED_ZONE, self.BLACK_ZONE]
		random_scores = [random.choice(values) for _ in range(7)]
		logger.info(f"Random score {random_scores}")

		self.SCORE += sum(random_scores)
		logger.info(f"Total score {self.SCORE}")

		body = {'score':self.SCORE}
		body = json.dumps(body)

		headers = self.headers
		headers.update({'Idempotency-Key': random.choice(self.config.idempotency_keys),
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
		logger.debug(f"Time diff: {time_diff}")

		if random.randint(0, 1) == 0:
			return

		self.previous_gift = time.time()
		resp = self.conn.request(method='POST', url=f'/api/game/v1/game-session/random-gift/{self.gameConfig.sessionId}/1', data=body, headers=headers)
		if int(resp.status_code) == 200:
			res = resp.read()
			js = json.loads(res)
			if js['statusInfo'] == "OK":
				logger.debug(js['data'])
		else:
			logger.debug(resp.status_code)
			logger.debug(resp.read())

		
