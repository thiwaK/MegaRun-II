from box import Box
import httpx
import json
import random

from urllib.parse import urlencode

from selenium.webdriver.chrome.service import Service
from seleniumwire.request import Response
from seleniumwire.request import Request
from seleniumwire.utils import decode
from seleniumwire import webdriver

from logger import logger

class Signin:

	def __init__(self, instance):
		

		self.config = instance.config
		self.utils = instance.utils

		self.chromeDriverBinary = self.config.chrome_driver
		self.userAgent          = self.config.user_agent

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--disable-application-cache")
		chrome_options.add_argument("--disable-infobars")
		chrome_options.add_argument("--no-sandbox")
		chrome_options.add_argument("--enable-logging")
		chrome_options.add_argument("--log-level=0")
		chrome_options.add_argument("--ignore-certificate-errors")
		self.chrome_options = chrome_options

	def start(self) -> tuple:
		"""
		launch the browser
		
		:returns:   None
		:rtype:     None
		"""

		logger.info("Launching browser")

		params = {
		    "redirect_uri": "lk.wow.superman:/callback",
		    "client_id": "qH9pNK62W8XtInwq1i1mvuYUUJEa", #hard coded
		    "response_type": "code",
		    "state": f"state{random.randint(10785393, 76848154)}" ,
		    "nonce": f"nonce{random.randint(20521935, 96918322)}_17a337b6-3290-4330-9586-e38c4f9495e4",
		    "scope": "openid",
		    "mode": "login",
		    "locale": "EN"
		}

		url = 'https://did.dialog.lk/authproxy/oauth2/authorize/operator/spark'

		full_url = f"{url}?{urlencode(params)}"

		self.headers_to_inject = {
			"sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
			"sec-ch-ua-mobile": "?1",
			"sec-ch-ua-platform": "Android",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": self.config.user_agent,
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
			"Sec-Fetch-Site": "cross-site",
			"Sec-Fetch-Mode": "navigate",
			"Sec-Fetch-Dest": "document",
			"Referer": "android-app://lk.wow.superman/",
			"Accept-Encoding": "gzip, deflate, br, zstd",
			"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
		}

		service = Service(self.chromeDriverBinary)
		driver = webdriver.Chrome(service=service, options=self.chrome_options, seleniumwire_options={})
		driver.request_interceptor = self.requestInterceptor
		driver.response_interceptor = self.responseInterceptor

		logger.debug("URL: " + full_url)
		driver.get(full_url)

		input("Waiting...")

		driver.quit()
		logger.info("Leaving browser")

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

	def logResponse(self, request:Request) -> None:
		"""
		Logs a response.
		
		:param      request:  The request
		:type       request:  Request
		
		:returns:   None
		:rtype:     None
		"""

		ext = '.' + request.path.split('.')[-1]
		formatted_request = {
			"url": request.url,
			"method": request.method,
			"date": request.date.strftime("%Y-%m-%d %H:%M:%S.%f"),
			"querystring": request.querystring,
			"params": request.params,
			"body": request.body.decode('utf-8'),
		}
		logger.debug(json.dumps(formatted_request, indent=2))

	def requestInterceptor(self, request:Request) -> None:
			"""
			intercept requests
			
			:param      request:  The request
			:type       request:  Request
			
			:returns:   None
			:rtype:     None
			"""
			abort = ["googleapis.com", "googletagmanager.com"]
			for host in abort:
				if host in request.host:
					logger.debug(f"Aborted: {request.url}")
					request.abort()

			self.injectHeaders(request, self.headers_to_inject)
			self.logResponse(request)			
		
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
		pass


		# 'abort', 'body', 'cert', 'create_response', 'date', 'headers'
		# 'host', 'id', 'method', 'params', 'path', 'querystring', 'response', 'url', 'ws_messages'

class AppStatus:

	def __init__(self, instance):

		self.config = instance.config
		self.utils = instance.utill
		timeout = httpx.Timeout(10.0)
		self.conn = httpx.Client(base_url='https://codepush.appcenter.ms', http2=False, timeout=timeout)
		self.headers = {
			'accept': 'application/json',
			'x-codepush-plugin-name': 'react-native-code-push',
			'x-codepush-plugin-version': '7.1.0',
			'x-codepush-sdk-version': '^4.1.0',
			'Content-Type': 'application/json',
			'Accept-Encoding': 'gzip',
			'User-Agent': 'okhttp/4.9.2'
		}

	def reportDepolyement(self):
		
		body = {
			"app_version":"1.8.4",
			"deployment_key":"QrJg_N-BG6brUCYRK1dEB3BH20nbW7aN6oBN2",
			"client_unique_id":"899d13eb06cd2e4f",
			"previous_deployment_key":"QrJg_N-BG6brUCYRK1dEB3BH20nbW7aN6oBN2"
		}
		body = json.dumps(body)

		headers = self.headers

		resp = self.conn.request(method='POST', url='/superapp-user-profile-service/user/authenticate', data=body, headers=headers)
		js = self.validateResponse(resp)
		print(js)

class SupperApp:

	def __init__(self, instance):

		adapter_ip = "NeoAdapter_VPN127"

		self.config = instance.config
		self.utils = instance.utils
		timeout = httpx.Timeout(10.0)
		self.conn = httpx.Client(
			base_url='https://api.wow.lk', 
			http2=True, 
			timeout=timeout,
			transport=httpx.HTTPTransport(local_address=adapter_ip))
		self.headers = {
			"accept": "application/json, text/plain, */*",
			"accept-encoding": "gzip",
			"accept-language": "en",
			"authorization": "Bearer " + self.config.accessToken,
			"content-type": "application/json",
			"user-agent": "okhttp/4.9.2",
			"x-device-id": instance.config.x_device_id
		}

	def validateResponse(self, response):
		if int(response.status_code) in [201, 200]:
			res = response.text
			js = json.loads(res)
			logger.debug(js)
			return Box(js)

		elif int(response.status_code) == 403:
			logger.error("403:Forbidden")
			return None

		elif int(response.status_code) == 401:
			logger.error("401:Unauthorized")
			logger.info("Retry with --update-token")
			return None
		else:
			logger.error("Unknown")
			logger.debug(response.status_code)
			logger.debug(response.text)
			return None

	# /superapp-user-profile-service/user/authenticate
	def getAccessToken(self):
		logger.info(":getAccessToken:")
		body = {
			"refreshCode": self.config.refreshCode,	"platform": "MOBILE", "mobileOS": "android",
			"grantType": "refresh", "msisdn": self.config.mobileNumber,	"integrityToken": ""
		}
		body = json.dumps(body)

		headers = self.headers
		headers.update({'authorization': 'Bearer undefined'})

		resp = self.conn.request(method='POST', url='/superapp-user-profile-service/user/authenticate', data=body, headers=headers)
		js = self.validateResponse(resp)
		
		if js:
			if js['statusCode'] == 200 and js['data']['statusCode'] == 200:
				data = js['data']['data']
				self.headers['authorization'] = "Bearer " + data['accessToken']
				return js

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None

	# /superapp-user-profile-service/v2/user/update/0777123456
	def userUpdate(self):
		logger.info(":userUpdate:")
		body = json.dumps({"msisdn":self.config.mobileNumber, "defaultLanguage":self.config.language})
		body = self.utils.encrypt(body, self.config.encryptionKey)

		resp = self.conn.request(method='PUT', url='/superapp-user-profile-service/v2/user/update/' + self.config.mobileNumber, data=body, headers=self.headers)
		js = self.validateResponse(resp)
		
		if js:
			data = js['data']
			# print(js['statusCode'])
			# print(js['friendlyMessage'])
			# print(data['accessToken'])
			# print(data['refreshCode'])
			# print(data['exp'])
			# print(data['refreshCodeExp'])
			# print(data['msisdn'])

			return data

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None

	# /superapp-user-profile-service/userPrimary/info/0777123456
	def getUserPrimaryInfo(self):
		logger.info(":getUserPrimaryInfo:")

		resp = self.conn.request(method='GET', url='/superapp-user-profile-service/userPrimary/info/' + self.config.mobileNumber, headers=self.headers)
		js = self.validateResponse(resp)

		if js:
			if js['statusCode'] == 200:
				return js['data']

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None

	# /superapp-user-profile-service/v2/user/0777123456
	def getUserInfo(self):
		logger.info(":getUserInfo:")

		resp = self.conn.request(method='GET', url='/superapp-user-profile-service/v2/user/' + self.config.mobileNumber, headers=self.headers)
		js = self.validateResponse(resp)

		if js:
			if js['statusCode'] == 200:
				return js['data']

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None


	# superapp-common-checkout-service/cart/0777123456
	def checkout(self):
		logger.info(":checkout:")

		self.headers['authorization'] = "Bearer " + self.config.accessToken
		resp = self.conn.request(method='GET', url='/superapp-common-checkout-service/cart/' + self.config.mobileNumber, headers=self.headers)

		js = self.validateResponse(resp)
		if js:
			return js
		
		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None


	# /superapp-admin-portal-service/banner/get-mobile
	def getBanners(self):
		logger.info(":getBanners:")

		body = json.dumps({
			"bannerType": "SUPPER_APP",
			"landingPageLocation": "GAMING_ARENA",
			"personas": ["bank_user","social_media_user","interest_in_higher_education","eat_out_seeker",
					 "whatsapp","selfcare_app_user","youtube_user","email_user","ussd_user","complainer",
					 "ott_user","data_user","data_4g_user"]})

		resp = self.conn.request(method='POST', url='/superapp-admin-portal-service/banner/get-mobile',
			data=body, headers=self.headers)

		js = self.validateResponse(resp)
		if js:
			return js['data']

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return False


	# /superapp-mega-wasana-midend-service/dashboard
	def getMegaWasana(self):
		logger.info(":getMegaWasana:")


		resp = self.conn.request(method='POST', url='/superapp-mega-wasana-midend-service/dashboard', data=None, headers=self.headers)

		js = self.validateResponse(resp)
		if js:
			if js['statusCode'] == 200:
				return js

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None


	# /superapp-mini-app-authentication-service/v3/application/authentication
	def authorizeMegaApp(self):
		logger.info(":authorizeMegaApp:")

		body = json.dumps({
			"appId":"GAMING_ARENA","msisdn":self.config.mobileNumber,"deviceId":self.config.device_id, "extraData":{
				"mdm":"miniAppOpen","cmpID":"PLAY_MINIAPP","dstn":"PLMA"
			},"isAuthenticated":False
		})
		body = json.dumps({"appId":"MEGA_GAMES","msisdn":self.config.mobileNumber,"deviceId":self.config.device_id,
			"extraData":{"mdm":None,"cmpID":None,"dstn":None},"isAuthenticated":True})

		body = self.utils.encrypt(body.replace('\n', ''), self.config.encryptionKey).replace('\n', '')
		body = {"data": body}

		self.headers.update({'ect': 'true'})

		resp = self.conn.request(method='POST',
			url='/superapp-mini-app-authentication-service/v3/application/authentication',
			json=body, headers=self.headers)

		js = self.validateResponse(resp)
		self.headers.pop('ect')

		if js:
			if js['statusCode'] == 200:
				return js
			return None

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None


	# /superapp-notification-service/v2/fcmToken/storeMobileNumber
	def updateFCMToken(self):
		logger.info(":updateFCMToken:")

		body = json.dumps({
			"fcmToken": self.utils.encrypt(self.config.fcmToken, configKey),
			"msisdn": self.config.mobileNumber
		})
		resp = self.conn.request(method='POST', url='/superapp-notification-service/v2/fcmToken/storeMobileNumber', data=body, headers=self.headers)

		js = self.validateResponse(resp)
		if js:
			if js['statusCode'] == 200:
				return js['data']

			logger.debug(resp.text)
			return None

		logger.debug(resp.status_code)
		logger.debug(resp.headers)
		logger.debug(resp.text)
		return None

	def checkUpdates(self):
		logger.info(":checkUpdates:")

		try:
			resp = self.conn.request(method='GET', url='https://api.playstore.rajkumaar.co.in/json?id=lk.wow.superman', headers=self.headers)
		except httpx.ReadTimeout as e:
			logger.debug("Read Timeout")
			return Box({'date':"", 'message':"", 'version':""})
		except httpx.ConnectError:
			logger.debug("Connect Error")
			return Box({'date':"", 'message':"", 'version':""})
		except httpx.ConnectTimeout:
			logger.debug("Connect Timeout")
			return Box({'date':"", 'message':"", 'version':""})

		js = self.validateResponse(resp)

		msg = js.latestUpdateMessage
		date = js.lastUpdated
		version = js.version

		return Box({'date':date, 'message':msg, 'version':version})
	

