from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumwire.request import Response
from seleniumwire.request import Request
from seleniumwire.utils import decode
from seleniumwire import webdriver

from box import Box
import json
import os
import time
import re
import hashlib
import psutil

class Browser:
	"""Browser manipulation"""

	
	
	def __init__(self, instance) -> None:

		self.RAID_SHOOTER_V = 20
		self.RAID_SHOOTER_GAME_ID = "9482808f-72c3-43a5-96c4-38c3d3a7673e"
		self.FOOD_BLOCKS_V = 24
		self.FOOD_BLOCKS_GAME_ID = "907bd637-30c0-435c-af6a-ee2efc4c115a"

		self.config          = instance.config
		self.url             = self.config.GAME_LAUNCHER_URL
		self.token           = self.config.GAME_LAUNCHER_TOKEN
		self.LOOP            = True
		self.gameURLList     = {}
		self.ui              = instance.ui
		self.logger          = instance.logger

		self.config.gameArena   = None
		self.config.currentGame = Box({})
		
		self.driver_process = None
		self.logExcludeExt      = self.config.ext_to_exclude_log_req
		self.chromeDriverBinary = self.config.chrome_driver
		self.userAgent          = self.config.user_agent
		self.hosts_404          = self.config.hosts_to_abort

		if not 'hash_table' in self.config:
			self.config['hash_table'] = {}

		self.replaceRespData = Box({
			'/games/9482808f-72c3-43a5-96c4-38c3d3a7673e/build/v20/bundle.js':{
				'headers': {'Content-Type': 'application/javascript'},
				'status_code': 200,
				'file': 'bundle_raidshooter_debug_v20.js',
				'read_mode': 'r'
			},

			'/games/907bd637-30c0-435c-af6a-ee2efc4c115a/build/v24/bundle.js':{
				'headers': {'Content-Type': 'application/javascript'},
				'status_code': 200,
				'file': 'bundle_foodblocks_debug.js',
				'read_mode': 'r'
			},

			# 'guage.webp':{
			# 	'headers': {'Content-Type': 'binary/octet-stream', 'accept-ranges':'bytes'},
			# 	'status_code': 200,
			# 	'file': r"RaidShooter\guage.png",
			# 	'read_mode': 'rb'
			# },

			# 'hitboard.webp':{
			# 	'headers': {'Content-Type': 'binary/octet-stream', 'accept-ranges':'bytes'},
			# 	'status_code': 200,
			# 	'file': r"RaidShooter\hitboard.png",
			# 	'read_mode': 'rb'
			# }

		})

		capabilities = DesiredCapabilities.CHROME
		capabilities['goog:loggingPrefs'] = {'browser': 'OFF'} 

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--disable-application-cache")
		chrome_options.add_argument("--disable-infobars")
		chrome_options.add_argument("--no-sandbox")
		chrome_options.add_argument("--ignore-certificate-errors")
		chrome_options.add_argument("--log-level=3")  # Suppress driver logs
		chrome_options.add_argument("--silent")       # Silent mode
		chrome_options.add_argument("--disable-logging")
		chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
		self.chrome_options = chrome_options

	def logResponse(self, request:Request) -> None:
		"""
		Logs a response.
		
		:param      request:  The request
		:type       request:  Request
		
		:returns:   None
		:rtype:     None
		"""

		ext = '.' + request.path.split('.')[-1]
		if not ext in self.logExcludeExt:		
			formatted_request = {
				"url": request.url,
				"method": request.method,
				"date": request.date.strftime("%Y-%m-%d %H:%M:%S.%f"),
				"querystring": request.querystring,
				"params": request.params,
				"body": request.body.decode('utf-8'),
			}
			self.logger.debug(json.dumps(formatted_request, indent=2))

	def hashTable(self, request, response) -> None:
		
		file_name = request.url.split("/")[-1]
		if file_name.endswith('.js') or file_name.endswith('.html'):
			data_byte = response.body
			self.logger.debug(data_byte)
			hex_hash = hashlib.sha256(data_byte).hexdigest()
			self.logger.debug(f"{file_name}:{hex_hash}")

			if file_name in self.config.hash_table:
				if hex_hash != self.config.hash_table[file_name]:
					self.logger.warning("Hash mismatch!")
			else:	
				self.config.hash_table[file_name] = hex_hash

	def quit(self) -> None:
		"""
		quit browser
		
		:returns:   None
		:rtype:     None
		"""
		self.LOOP = False

	def injectHeaders(self, request:Request, headers:dict) -> None:
		"""
		inject headers into request
		
		:param      request:  The request
		:type       request:  Request
		:param      headers:  The headers
		:type       headers:  dict
		
		:returns:   None
		:rtype:     None
		"""
		for k,v in headers.items():
			del request.headers[k]
			request.headers[k] = v


	def killIt(self):
		try:
			for child in self.driver_process.children(recursive=True):
				child.kill()
			self.driver_process.kill()

		except Exception as e:
			print(e)
	

	def varifyKeygenFunc(self, response):

		import subprocess
		import gzip
		from io import BytesIO

		if response.body is None:
			raise ValueError("No content in the response.")

		content_type = response.headers.get('Content-Type', '')
		encoding = response.headers.get('Content-Encoding', '')
		body = None

		if encoding == 'gzip':
			with gzip.GzipFile(fileobj=BytesIO(response.body)) as f:
				body = f.read().decode('utf-8')
		else:
			raise RuntimeError("Undefined encoding")

		if body is None:
			raise ValueError("No content in the body.")

		def find_function_scope(data, pattern):

			match = re.search(pattern, data)
			if not match:
				raise ValueError("Pattern not found in the data.")

			match_start = match.start()
			
			brace_stack = 0
			func_start = None
			func_end = None
			
			for i in range(match_start, -1, -1):
				if data[i:i+9] == ',function':
					func_start = i
					brace_stack = 1
					break
			
			if func_start is None:
				raise ValueError("No function declaration found.")
			
			found_call = False
			for i in range(func_start, len(data)):
				
				if not found_call and data[i:i+6] == '.call(':
					found_call = True
					func_end = i + 6
				elif found_call and data[i:i+2] == '},':
					func_end = i + 2
					break

			if func_end is None:
				raise ValueError("Matching closing brace not found for the function.")

			return data[func_start:func_end]

		def extract_functions(data, start, end):

			fun_end = 0
			fun_start = 0
			caller_ = None
			for x in re.finditer(end, data):
				fun_end = x.start()
				caller_ = x.group(1)

			for x in re.finditer(start, data):
				fun_start = x.start() + len(start)

			functions_ = data[fun_start:fun_end]
			return caller_, functions_


		inner_fun_scope = find_function_scope(body, self.config.key_caller_pattern)
		caller, prog  = extract_functions(inner_fun_scope, self.config.key_scope_start, self.config.key_scope_end)

		prog += f'''
		console.log({caller}(0,0,0))
		'''

		with open(r'bin\prog.js', 'w') as f:
			f.write(prog)


		command = ["node", r"bin\keygen.js", '0', '0', '0', '0', '0']
		result = subprocess.run(command, capture_output=True, text=True, shell=True).stdout.strip()

		command2 = ["node", r"bin\prog.js"]
		result2 = subprocess.run(command2, capture_output=True, text=True, shell=True).stdout.strip()

		if result != result2:
			self.logger.error(f"Keygen failed! {result} != {result2}")
			self.logger.error("Unable to continue. Terminating...")
			self.killIt()
			exit()
		else:
			self.logger.info(f"Keygen passed {result} == {result2}")


	def modifyResponse(self, file:str, headers:dict, status_code:int, read_mode:str, request) -> None:
		"""
		craft custom reponse with custom content for the request
		
		:param      file:         The file
		:type       file:         str
		:param      headers:      The headers
		:type       headers:      dict
		:param      status_code:  The status code
		:type       status_code:  int
		:param      read_mode:    The read mode
		:type       read_mode:    str
		
		:returns:   None
		:rtype:     None
		"""
		if os.path.isfile(file):
			new_body = ""
			with open(file, read_mode) as f:
				new_body = f.read()

			request.create_response(
				status_code=status_code,
				headers=headers,
				body=new_body
			)
		else:
			self.logger.warning("File not found")

	def requestInterceptor(self, request:Request) -> None:
			"""
			intercept requests
			
			:param      request:  The request
			:type       request:  Request
			
			:returns:   None
			:rtype:     None
			"""
			self.injectHeaders(request, self.headers_to_inject)

			if request.host in self.hosts_404:
				self.logger.debug(f"Aborted: {request.url}")
				request.abort()
			else:
				self.logResponse(request)

			if '/api/game/v1/game-session/random-gift/' in request.path:
				self.logger.info("Random gift request detected")

				pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
				match = re.search(pattern, request.path)

				if match:
					sessionId = match.group(0)
					self.logger.info("Session Id: " + sessionId)
					if sessionId == None or sessionId == "":
						self.logger.error("Unable to continue")
						self.killIt()
						exit()

					self.config.currentGame['sessionId'] = sessionId
					
					if not self.config.keep_play_in_browser: 
						self.quit()
				else:
					self.logger.info("No Session Id found.")
					self.logger.error("Unable to continue")
					request.killIt()
					exit()

				self.config.currentGame['score'] = json.loads(request.body)['score']

				___x = f"{request.headers['Idempotency-Key']} {self.config.currentGame['score']} {int(time.time())}"
				self.logger.debug(___x)



			for k,v in self.replaceRespData.items():
				if request.path.endswith(k):
					self.logger.info("Replace response content")
					self.logger.debug(f"URL: {request.url}")
					self.modifyResponse(v.file, v.headers, v.status_code, v.read_mode, request)


			for item in self.gameURLList:
				if item in request.url or request.url == item:
					self.logger.info("New game init detected")

					game = Box(self.gameURLList[item])
					gameID = game.id
					gameName = game.name
					gameDescription = game.description
					gameThumbnail = game.thumbnail
					gamePublished = game.published
					gameURL = game.url
					gameUUID = game.uuid
					gameStateCount = game.stateCount
					gameMax_difficulty_level = game.max_difficulty_level

					__tmp__ = f"\n==========[Initiating New Game]==========\n\tGame:{gameName}\n\tID:{gameID}\n\tUUID:{gameUUID}\n\tState Count:{gameStateCount}\n\tPublished:{gamePublished}"
					self.logger.debug(__tmp__)

					self.config.currentGame['game'] = game

					if not self.config.minimal_ui: self.ui.data["Game Info"]["Name   "] = game.name
		
	def responseInterceptor(self, request:Request, response:Response) -> None:
		"""
		intercept responses
		
		:param      request:   The request
		:type       request:   Request
		:param      response:  The response
		:type       response:  Response
		
		:returns:   None
		:rtype:     None
		"""

		self.hashTable(request, response)

		if f'/api/user/v1/access-token/{self.token}' in request.path:
			
			js_ = json.loads(response.body)
			if js_['statusInfo'] == 'OK' and js_['success']:
				self.logger.info("Game arena configuration loaded")
				self.config.gameArena = Box(js_)

				for item in self.config.gameArena.data.game_list:
					if item.url not in self.gameURLList:
						self.gameURLList[item.url] = item

				self.config.currentGame['access_token'] = self.config.gameArena.data.access_token
				self.config.currentGame['refresh_token'] = self.config.gameArena.data.refresh_token

				self.logger.debug("gameURLList")
				self.logger.debug(self.gameURLList)

			else:
				self.logger.error("gameArenaConfig: Unknown")
				self.logger.error(json.dumps(js_, indent=2))
				driver.quit()
				exit()

		if f'/games/{self.FOOD_BLOCKS_GAME_ID}/build' in request.path and request.path.endswith('bundle.js'):
			self.logger.info("FoodBlocks game JS request destected")
			if request.path.split("/")[-2] != f"v{self.FOOD_BLOCKS_V}":
				self.logger.warning(f"Supported version: v{self.FOOD_BLOCKS_V}, but detected {request.path.split('/')[-2]}")
				self.varifyKeygenFunc(response)

				if not self.config.skip_warn:
					self.killIt()
					exit()


		elif f'/games/{self.RAID_SHOOTER_GAME_ID}/build' in request.path and request.path.endswith('bundle.js'):
			self.logger.info("RaidShooter game JS request destected")
			if request.path.split("/")[-2] != f"v{self.RAID_SHOOTER_V}":
				self.logger.warning(f"Supported version: v{self.RAID_SHOOTER_V}, but detected {request.path.split('/')[-2]}")
				self.varifyKeygenFunc(response)

				if not self.config.skip_warn:
					self.killIt()
					exit()


		# 'abort', 'body', 'cert', 'create_response', 'date', 'headers'
		# 'host', 'id', 'method', 'params', 'path', 'querystring', 'response', 'url', 'ws_messages'

	def launch(self) -> tuple:
		"""
		launch the browser
		
		:returns:   None
		:rtype:     None
		"""
		self.logger.info("Launching browser")

		url = f"{self.url}?token={self.token}"

		self.headers_to_inject = {
			'Referer':url,
			'sec-ch-ua-platform':'"Android"',
			'X-Requested-With':'lk.wow.superman',
			'sec-ch-ua':'"Chromium";v="130", "Android WebView";v="130", "Not?A_Brand";v="99"',
			'User-Agent':self.config.user_agent,
		}

		service = Service(self.chromeDriverBinary)
		driver = webdriver.Chrome(service=service, options=self.chrome_options, seleniumwire_options={})
		self.driver_process = psutil.Process(driver.service.process.pid)


		driver.request_interceptor = self.requestInterceptor
		driver.response_interceptor = self.responseInterceptor

		self.logger.debug("URL: " + url)
		driver.get(url)

		

		# input()
		while self.LOOP:
			if not self.driver_process.is_running() or len(self.driver_process.children(recursive=True)) == 0:
				self.logger.warning("No browser processess found.")
				self.logger.info("Terminating...")
				driver.quit()
				exit()
			time.sleep(1)

		self.logger.info("Leaving browser")
		driver.quit()
		
		return self.config


