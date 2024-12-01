from box import Box
import xml.etree.ElementTree as ET
import json
import os
from logger import logger
from utils import Utils

class Config:
	"""Configuration handler"""
		
	def __init__(self, file_name):
		self.configFile        = file_name
		self.secondaryConfig   = None
		self.config            = None
		self.excludeFromConfig = None
		

		self.load(False)

	def update(self, key: str, value: str) -> Box:
		"""
		update configuration including file
		
		:param      key:    The key
		:type       key:    str
		:param      value:  The value
		:type       value:  str
		
		:returns:   updated configuration object
		:rtype:     Box
		"""
		if key == None:
			return

		self.config[key] = value
		
		with open(self.configFile, 'w') as file:
			json.dump(self.config, file, indent=4)

		logger.debug(f"Updated {key}: {value}")
		return self.config

	def load(self, forceReadSecondary=False) -> Box:
		"""
		load configuration from file
		
		:param      forceReadSecondary:  The force read secondary configuration
		:type       forceReadSecondary:  bool
		
		:returns:   configuration object
		:rtype:     Box
		"""
		data_sec = {}
		data_pri = {}
		data_out = {}

		printx = {"printx": {
			"game": {
				"name":"None",
				"uuid":"None",
				"session":"None",
			},
			"gift": {
				"remains":"None",
				"total":"None",
				"history":"None",
				"next": "None"
			},
			"log": [
			
			],
			"stat": {
				"total_gift_req":"100",
				"failed_gift_req":"10",
				"total_run_time": "00:05:00"
			}
		}}

		if os.path.isfile(self.configFile):
			with open(self.configFile, 'r') as file:
				data_pri = json.load(file)
				data_pri.update(printx)
				self.config = Box(data_pri)

		if 'secondary_config' in data_pri:
			self.utils = Utils(self)
			self.secondaryConfig = data_pri['secondary_config']

			if os.path.isfile(self.secondaryConfig):
				tree = ET.parse(self.secondaryConfig)
				root = tree.getroot()
				for child in root:
					d = self.utils.decrypt(child.text, self.config.config_key)#encryptionKey
					if d:
						data_sec[child.attrib['name']] = d[1:-1]
					else:
						data_sec[child.attrib['name']] = child.text

		if forceReadSecondary:
			data_pri.update(data_sec)
			data_out = data_pri
			logger.warning("Force loading secondary config")
		else:
			data_sec.update(data_pri)
			data_out = data_sec
		
		if 'exclude_from_config' in data_out:
			self.excludeFromConfig = data_out['exclude_from_config']
			for item in self.excludeFromConfig:
				if item in data_out: data_out.pop(item)

		self.config = Box(data_out)
		return self.config

		