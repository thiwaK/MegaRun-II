from box import Box
import httpx
import json
from logger import logger


class SupperApp:

	def __init__(self, instance):

		self.config = instance.config
		self.utill = instance.utill
		self.conn = httpx.Client(base_url='https://api.wow.lk', http2=True)
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
		body = self.utill.encrypt(body, self.config.encryptionKey)

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

		body = self.utill.encrypt(body.replace('\n', ''), self.config.encryptionKey).replace('\n', '')
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
			"fcmToken": self.utill.encrypt(self.config.fcmToken, configKey),
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
	