import jwt
import subprocess
import os
from logger import logger
import datetime
import base64

class Utill:
	"""
	Utility container
	"""

	def __init__(self, instance):
		self.binary = instance.config.crypto_binary
		self.JWTAlgo = instance.config.JWT_algo
		self.encryptCMD = instance.config.encrypt_command
		self.decryptCMD = instance.config.decrypt_command

	def encrypt(self, text: str, password: str) -> str:
		"""
		encrypt the input text using the input password
		
		:param      text:      The text
		:type       text:      str
		:param      password:  The password
		:type       password:  str
		
		:returns:   encrypted text as b64
		:rtype:     str
		"""
		logger.debug(":encrypt:")
		try:
			cmd = self.encryptCMD
			cmd = cmd.format(text=text, binary=self.binary, password=password)
			process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = process.communicate()
			return stdout.decode().strip()

		except subprocess.CalledProcessError as e:
			logger.error(e)
			return None

		except UnicodeDecodeError as e:
			logger.error(e)
			return None


	def decrypt(self, encoded_text: str, password: str) -> str:
		"""
		decrypt the input b64 text using input password
		
		:param      encoded_text:  The encoded text
		:type       encoded_text:  str
		:param      password:      The password
		:type       password:      str
		
		:returns:   decrypted value as text
		:rtype:     str
		"""
		logger.debug(":decrypt:")
		temp_file = "temp.bin"
		try:
			with open(temp_file, "wb") as f:
				f.write(base64.b64decode(encoded_text))

			cmd = self.decryptCMD
			cmd = cmd.format(text=encoded_text, binary=self.binary, password=password, temp_file=temp_file)
			process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = process.communicate()
			return stdout.decode().strip()

		except subprocess.CalledProcessError as e:
			logger.error(e)
			return None

		except UnicodeDecodeError as e:
			logger.error(e)
			return None

		finally:
			if os.path.isfile(temp_file):
				os.remove(temp_file)

	def validateJWT(self, token: str) -> int:
		"""
		check the expire status of the input Java Web Token
		
		:param      token:  The token
		:type       token:  str
		
		:returns:   validity or error encounter as an int
		:rtype:     int
		"""
		try:
			decoded_token = jwt.decode(token, algorithms=[self.JWTAlgo], options={"verify_signature": False})
			exp = decoded_token.get("exp")

			if exp:
				logger.debug(f"{datetime.datetime.utcnow().timestamp()} > {exp}")
				is_expired = int(datetime.datetime.utcnow().timestamp()) > exp
				logger.debug(f"Token expired: {is_expired}")
				if not is_expired:
					return 200
				return 400
			else:
				logger.error("Token does not contain an expiration ('exp') field.")
				return 300
		except jwt.exceptions.InvalidTokenError as e:
			logger.error(f"Invalid token: {e}")
			return 100
		except:
			logger.error("Unknown")
			return 999
	
