import sys
import os
import json
import argparse

from colorama import Fore, Style, Back
from box import Box
import time
from datetime import datetime
import threading
import logging
import re

import ctypes, struct
from rich.console import Console
from rich.text import Text

sys.path.append('src')
from supper_app import SupperApp as WOW
# from supper_app import Signin
from config import Config
from logger import logger
from utils import Utils
from browser import Browser
from game import RaidShooter
from game import FoodBlocks



"""
TODO
- add average reward for a win
- add option for response replecer. input: json
"""

class Color:

	RESET = Style.RESET_ALL
	
	OWNER = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
	BORDER = Fore.LIGHTBLACK_EX + Back.BLACK
	SECTION_NAME = Fore.LIGHTBLACK_EX + Back.BLACK

	SYMBOL_SEC_A = Fore.LIGHTBLUE_EX
	HEADER_SEC_A = Fore.LIGHTWHITE_EX
	TEXT_SEC_A = Fore.LIGHTMAGENTA_EX

	SYMBOL_SEC_B = Fore.LIGHTRED_EX
	HEADER_SEC_B = Fore.LIGHTWHITE_EX
	TEXT_SEC_B = Fore.LIGHTGREEN_EX

	SYMBOL_SEC_C = Fore.LIGHTMAGENTA_EX
	HEADER_SEC_C = Fore.LIGHTWHITE_EX
	TEXT_SEC_C   = Fore.LIGHTGREEN_EX

	SYMBOL_SEC_D = Fore.LIGHTGREEN_EX
	HEADER_SEC_D = Fore.LIGHTWHITE_EX
	TEXT_SEC_D = Fore.LIGHTBLUE_EX

class Border:

	TOP_LEFT = Color.BORDER +    "╓" #"╔" #"┏"
	TOP_RIGHT =                  "╖" #"╗" #"┓"
	BOTTOM_LEFT = Color.BORDER + "╙" #"╚" #"┗"
	BOTTOM_RIGHT =               "╜" #"╝" #"┛"
	HORIZONTAL = "─" #"━"
	VERTICAL = Color.BORDER + "║" #"┃"
	TOP_SPLIT = "╥" #"┳" 
	BOTTOM_SPLIT = "╨" #"┻"
	LEFT_SPLIT = Color.BORDER + "╟" #"┣"
	RIGHT_SPLIT = "╢" #"┫"
	CROSS = "╫" #"╋"
	HEADER_LEFT = "┨" #"▐"
	HEADER_RIGHT = "┠" #"▌"

class Symbol:
	loading = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
	loading = ['⌜', '⌝', '⌟', '⌞']
	loading = ['◜', '◝', '◞', '◟']
	gift_animation = ['◈', ' ', ' ', '◈']
	gift_animation = ['⁘', ' ',	' ', '⁘']
	banner_animation = ['⁖', ' ', ' ', ' ', '⁖']
	SYMBOL_SEC_A = " ⌬ "
	SYMBOL_SEC_B = " ◈ "
	SYMBOL_SEC_C = " ⎆ "
	SYMBOL_SEC_D = " ⌗ "
	SYMBOL_PROGRESS = "■"

class CustomFormatter(logging.Formatter):
	def format(self, record):
		timestamp = str(time.time_ns() // 1000000)
		event = record.levelname
		message = record.getMessage()
		now = datetime.now()
		formatted_time = now.strftime("%H:%M:%S")
		color = Fore.LIGHTWHITE_EX
		if event[0] == "I":
			color = Fore.LIGHTCYAN_EX
		elif event[0] == "W":
			color = Fore.LIGHTYELLOW_EX
		elif event[0] == "E":
			color = Fore.LIGHTRED_EX
		
		return f"{Fore.GREEN}[{Fore.LIGHTBLACK_EX}{formatted_time}{Fore.GREEN}] {color}[{event[0]}] {message}"

class CustomLogHandler(logging.Handler):
	def __init__(self, instance):
		super().__init__(logging.INFO)
		self.instance = instance

	def emit(self, record):
		log_message = self.format(record)
		self.instance.data.Log.update({str(time.time()): log_message})

class CLUI:

	width, height = 110, 17
	ratio_top = 0.36  # Ratio for the top section

	def __init__(self, instance):


		self.data = Box({
			"Game Info": {
				"show_symbol": True,
				"section_symbol":"",
				"show_header": True,
				"Name   ": "None",
				"Chances": "None",
				"Reward ": "None",
				"Next   ": "[" + ' '*39 + "]"
			},
			"Gift History": {
				"show_symbol": False,
				"section_symbol":"",
				"show_header": False,
			},
			"Log": {
				"show_symbol": False,
				"section_symbol":"",
				"show_header": False,
			},
			"Stat": {
				"show_symbol": True,
				"section_symbol":"",
				"show_header": True
			}
		})
		logHandler = CustomLogHandler(self)
		logHandler.setFormatter(CustomFormatter())
		logger.addHandler(logHandler)

		os.system('cls')

		instance.logger = logger
		self.bar_width = 39
		self.next_end = time.time()
		self.next_beginning = time.time() + 1
		self.gift_history = []

	def update(self, game=None, gift=None, log=None, stat=None):
		if game:
			self.data.game += game

		if gift:
			self.data.gift += gift

		if log:
			self.data.Log.update(log)

		if stat:
			self.data.stat += stat

	def eraseLines(self):
		'''
			'\033[<L>;<C>H'	Positions the cursor. Puts the cursor at line L and column C.
			'\033[<N>A'	Move the cursor up by N lines.
			'\033[<N>B'	Move the cursor down by N lines.
			'\033[<N>C'	Move the cursor forward by N columns.
			'\033[<N>D'	Move the cursor backward by N columns.
			'\033[2J'	Clear the screen, move to (0,0)
			'\033[K'	Erase the end of line.
			'\033[F'    Move up one line
			'\x1b[2K'   Line clear
		'''		
		
		sys.stdout.write(f'\033[{self.msg_row_count}A')
		sys.stdout.flush()
		

		# stdout_handle = ctypes.windll.kernel32.GetStdHandle(-11)
		# position = (0 << 16) | 0
		# ctypes.windll.kernel32.SetConsoleCursorPosition(stdout_handle, position)

	def __addBorders__(self):

		sec_a_title, sec_b_title, sec_c_title, sec_d_title = self.data.keys()

		# Borders and empty rows with selective colors
		self.top_border = (
			Border.TOP_LEFT   + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_a_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_a_title + Border.HEADER_RIGHT +
			Border.HORIZONTAL + Border.TOP_SPLIT + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_b_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_b_title + Border.HEADER_RIGHT +
			Border.HORIZONTAL + Border.TOP_RIGHT + Color.RESET
		)
		self.mid_horizontal = (
			Border.LEFT_SPLIT + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_c_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_c_title + Border.HEADER_RIGHT  + 
			Border.HORIZONTAL + Border.CROSS + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_d_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_d_title + Border.HEADER_RIGHT +
			Border.HORIZONTAL + Border.RIGHT_SPLIT + Color.RESET
		)
		self.bottom_border = (
			Border.BOTTOM_LEFT + Border.HORIZONTAL * (self.width // 2 - 1) + Border.BOTTOM_SPLIT +
			Border.HORIZONTAL * (self.width // 2 - 10) +
			" thiwaK " + Color.BORDER + Border.HORIZONTAL + Border.BOTTOM_RIGHT + Color.RESET + ""
		)

		self.empty_row_upper = (
			Border.VERTICAL + 
			Color.RESET + " " * (self.width // 2 - 1) + 
			Border.VERTICAL + 
			Color.RESET + " " * (self.width // 2 - 1) + Border.VERTICAL
			)
		self.empty_row_lower = Border.VERTICAL + Color.RESET + " " * (self.width - 1) + Border.VERTICAL + Color.RESET

	def __generateSectionData__(self, sec_title, section):
			
		section_data   = self.data[sec_title].copy()
		show_symbol    = section_data['show_symbol']
		section_symbol = section_data['section_symbol']
		show_header    = section_data['show_header']

		section_data.pop('show_symbol')
		section_data.pop('section_symbol')
		section_data.pop('show_header')

		section_header_colors = {
			'A': Color.HEADER_SEC_A,
			'B': Color.HEADER_SEC_B,
			'C': Color.HEADER_SEC_C,
			'D': Color.HEADER_SEC_D
		}
		header_color = section_header_colors.get(section)

		section_symbol_colors = {
			'A': Color.SYMBOL_SEC_A,
			'B': Color.SYMBOL_SEC_B,
			'C': Color.SYMBOL_SEC_C,
			'D': Color.SYMBOL_SEC_D
		}
		symbol_color = section_symbol_colors.get(section)

		section_text_colors = {
			'A': Color.TEXT_SEC_A,
			'B': Color.TEXT_SEC_B,
			'C': Color.TEXT_SEC_C,
			'D': Color.TEXT_SEC_D
		}
		text_color = section_text_colors.get(section)

		section_symbols = {
			'A': Symbol.SYMBOL_SEC_A,
			'B': Symbol.SYMBOL_SEC_B,
			'C': Symbol.SYMBOL_SEC_C,
			'D': Symbol.SYMBOL_SEC_D
		}
		symbol = section_symbols.get(section)

		text = [
			(symbol_color + symbol if show_symbol else "") +
			(header_color + item[0] + ": " if show_header else "") + 
			text_color + item[1] for item in section_data.items()
		]

		return text

	def getANSILength(self, text):
		ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
		matches = ansi_escape.findall(text)
		return sum([len(x) for x in matches])

	def getTextLength(self, text):
		
		return len(text) - self.getANSILength(text)

	def printx(self):

		self.__addBorders__()
		
		# Build banner
		output = self.getBanner()
		for i in range(len(output)):
			output[i] = Fore.LIGHTRED_EX + Back.BLACK + output[i]

		# Top border
		output.append(self.top_border)

		# Calculate row counts for each section based on the ratio
		top_section_height = int(self.height * self.ratio_top)
		bottom_section_height = self.height - top_section_height - 2
		
		# Section data
		sec_a_title, sec_b_title, sec_c_title, sec_d_title = self.data.keys()
		text_1 = self.__generateSectionData__(sec_a_title, 'A')
		text_2 = self.__generateSectionData__(sec_b_title, 'B')
		text_3 = self.__generateSectionData__(sec_c_title, 'C')
		text_4 = self.__generateSectionData__(sec_d_title, 'D')

		# Add rows for the upper section (with a horizontal split in the middle)
		for i in range(top_section_height):
			t1_rows = text_1[(top_section_height - 1) * -1:]
			t2_rows = text_2[(top_section_height - 1) * -1:]

			if max(len(t1_rows), len(t2_rows)) > i:
				
				# Match row counts
				if len(t1_rows) != len(t2_rows):
					if len(t1_rows) > len(t2_rows):
						t2_rows += [" " for _ in range(len(t1_rows) - len(t2_rows))]
					else:
						t1_rows += [" " for _ in range(len(t2_rows) - len(t1_rows))]

				# Trim overflow
				trim_limit = self.width // 2 - 1
				if self.getTextLength(t1_rows[i]) > trim_limit:
					t1_rows[i] = t1_rows[i][:trim_limit + self.getANSILength(t1_rows[i])]
				else:
					t1_rows[i] = t1_rows[i] + " " * (trim_limit - self.getTextLength(t1_rows[i]))

				if self.getTextLength(t2_rows[i]) > trim_limit:
					t2_rows[i] = t2_rows[i][:trim_limit + self.getANSILength(t2_rows[i])]
				else:
					t2_rows[i] = t2_rows[i] + " " * (trim_limit - self.getTextLength(t2_rows[i]))

				if len(t1_rows) == len(t2_rows):
					parta = Color.BORDER + Border.VERTICAL +  Color.RESET + t1_rows[i].ljust(self.width // 2 - 1, ' ') + Color.BORDER + Border.VERTICAL + Color.RESET
					partb = t2_rows[i].ljust(self.width // 2 - 1, ' ') + Color.BORDER + Border.VERTICAL + Color.RESET
					output.append(parta + partb)
					continue

			output.append(self.empty_row_upper)
		# exit()

		# Horizontal split for the upper part
		output.append(self.mid_horizontal)

		# Add rows for the lower section (without any split)
		for i in range(bottom_section_height):
			t3_rows = text_3[(bottom_section_height - 1) * -1:]
			t4_rows = text_4[(bottom_section_height - 1) * -1:]

			if max(len(t3_rows), len(t4_rows)) > i:
				
				# Match row counts for t3_rows and t4_rows
				if len(t3_rows) != len(t4_rows):
					if len(t3_rows) > len(t4_rows):
						t4_rows += [" " for _ in range(len(t3_rows) - len(t4_rows))]
					else:
						t3_rows += [" " for _ in range(len(t4_rows) - len(t3_rows))]

				# Trim overflow
				trim_limit = self.width // 2 - 1
				if self.getTextLength(t3_rows[i]) > trim_limit:
					t3_rows[i] = t3_rows[i][:trim_limit + self.getANSILength(t3_rows[i])]
				else:
					t3_rows[i] = t3_rows[i] + " " * (trim_limit - self.getTextLength(t3_rows[i]))

				if self.getTextLength(t4_rows[i]) > trim_limit:
					t4_rows[i] = t4_rows[i][:trim_limit + self.getANSILength(t4_rows[i])]
				else:
					t4_rows[i] = t4_rows[i] + " " * (trim_limit - self.getTextLength(t4_rows[i]))


				if len(t3_rows) == len(t4_rows) and max(len(t3_rows), len(t4_rows)) > i:
					parta = Color.BORDER + Border.VERTICAL + Color.RESET + t3_rows[i].ljust(self.width // 2 - 1) + Color.BORDER + Border.VERTICAL + Color.RESET
					partb = t4_rows[i].ljust(self.width // 2 - 1) + Color.BORDER + Border.VERTICAL + Color.RESET
					output.append(parta + partb)
					continue

			output.append(self.empty_row_upper)

		output.append(self.bottom_border)

		# output.append(Symbol.loading[self.loading_scene_count])

		# Print the result
		# for line in output:
		print("\n".join(output))

		self.msg_row_count = len(output) + 1

	def getBanner(self):

		banner_width = 110

		banner_text = [
			"                                                                           ",
			"  __  __                          _____                      _____   _____ ",
			" |  \/  |                        |  __ \                    |_   _| |_   _|",
			" | \  / |   ___    __ _    __ _  | |__) |  _   _   _ __       | |     | |  ",
			" | |\/| |  / _ \  / _` |  / _` | |  _  /  | | | | | '_ \      | |     | |  ",
			" | |  | | |  __/ | (_| | | (_| | | | \ \  | |_| | | | | |    _| |_   _| |_ ",
			" |_|  |_|  \___|  \__, |  \__,_| |_|  \_\  \__,_| |_| |_|   |_____| |_____|",
			"                   __/ |                                                   ",
			"                  |___/                                                    ",
			"                                                                           "
		]

		background = []

		for index in range(len(banner_text)):

			banner_anim_symbol_len = len(Symbol.banner_animation)

			result = ""
			for i in range(index, banner_width + index):
				result += Symbol.banner_animation[i % banner_anim_symbol_len]

			start = self.current_frame % banner_anim_symbol_len
			result = result[start:] + result[:start]

			if index % 2 == 0:
				background.append(result[::-1])
			else:
				background.append(result)

		result = []

		banner_width = len(background[0])
		for i, bg_row in enumerate(background):
			if i < len(banner_text):
				text_row = banner_text[i]

				# Center the banner text within the row
				padding = (banner_width - len(text_row)) // 2
				padded_text = ' ' * padding + text_row + ' ' * (banner_width - len(text_row) - padding)
				
				# Remove overlapping characters
				modified_row = ''.join(
					bg_char if text_char == ' ' else text_char 
					for bg_char, text_char in zip(bg_row, padded_text)
				)
			else:
	            # Use the background row if there's no corresponding banner text
				modified_row = bg_row
			
			result.append(modified_row)

		return result

	def animateGift_(self, start_index):
		
		section_width = 70
		gift_animation = len(Symbol.gift_animation)

		result = ""
		for i in range(start_index, section_width + start_index):
			result += Symbol.gift_animation[i % gift_animation]

		start = self.current_frame % gift_animation
		result = result[start:] + result[:start]

		if start_index % gift_animation == 0:
			return result[::-1]
		return result

	def getProgress(self):
		current_time = time.time()

		total_duration = self.next_end - self.next_beginning
		elapsed_time = current_time - self.next_beginning

		elapsed_time = max(0, min(elapsed_time, total_duration))

		progress_percentage = elapsed_time / total_duration

		filled_length = int(self.bar_width * progress_percentage)

		progress_bar = (
			Fore.LIGHTBLACK_EX + '[' + Fore.LIGHTCYAN_EX + 
			Symbol.SYMBOL_PROGRESS * filled_length + (' ' * (self.bar_width - filled_length)) + 
			Fore.LIGHTBLACK_EX + ']')

		return progress_bar #f"\r{progress_bar} {progress_percentage * 100:.2f}%"

	def show(self):
		self.ui_start = int(time.time_ns() // 1_000_000)

		gift_scenes_per_sec = 5
		frames_per_sec = 5
		
		frame_time = 1 / frames_per_sec 
		self.current_frame = 0


		while True:

			self.printx() 
			time.sleep(frame_time)
			self.eraseLines()
			self.current_frame += 1

			# self.data["Gift History"] = {
			# 	"show_symbol": False,
			# 	"section_symbol":"",
			# 	"show_header": False,
			# 	self.current_frame:self.animateGift(0),
			# 	self.current_frame + 1:self.animateGift(1),
			# 	self.current_frame + 2:self.animateGift(0),
			# 	self.current_frame + 3:self.animateGift(1),
			# 	self.current_frame + 4:self.animateGift(0),
			# }

			# str(js['data']['amount'])

			self.data["Game Info"]["Next   "] = self.getProgress()

			if self.current_frame == 1000_0000:
				self.current_frame = 0


class Main:
	"""Main class"""

	version_support = "1.8.6"

	def __init__(self, config_file='config.js', force_secondary_config=False, update_token=False,
		skip_warn=False, keep_play_in_browser=False, continue_on_chances_over=False):
		self.configObject = Config(config_file)
		self.config = self.configObject.load(force_secondary_config)
		self.config.file = config_file
		self.config.skip_warn = skip_warn
		self.config.keep_play_in_browser = keep_play_in_browser
		self.config.continue_on_chances_over = continue_on_chances_over
		
		self.ui = CLUI(self)
		self.utils  = Utils(self)
		self.wow = WOW(self)

		if os.name != 'nt':
			logger.error("Unsupported Opertating System. Only works with NT systems.")
			sys.exit(1)

		logger.info("==================================================")

		ui_thread = threading.Thread(target=self.ui.show, daemon=True)
		ui_thread.start()

		if update_token:
			self.getAccessToken()


		# s = Signin(self)
		# s.start()
	
	# Kind a mess. Should be cleard
	def checkToken(self):
		logger.info(":checkToken:")

		r = self.utils.validateJWT(self.config.refreshCode)
		if r == 400:
			logger.warning("Refresh token expired. Update manually.")
			exit()
		elif r == 200:
			logger.debug("Refresh token OK")
		else:
			logger.error("Unknown")
			exit()


		r = self.utils.validateJWT(self.config.accessToken)
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
			if self.version_support != r.version:
				logger.warning("New update avilable")
				tmp_ = f"\n  Current version: {self.config.appVersion}"
				tmp_ += f"\n  Avilable version: {r.version}"
				tmp_ += f"\n  Last update: {r.date}"
				tmp_ += f"\n  Message: {r.message}"
				tmp_ += f"\n"

				logger.debug(tmp_)
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

		rr = self.utils.decrypt(r, self.config.encryptionKey)
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

		rr = self.utils.decrypt(r, self.config.encryptionKey)
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

		rr = self.utils.decrypt(r['data'], self.config.encryptionKey)
		if rr != None:
			rr = json.loads(rr)
			logger.debug(rr)
			self.config.GAME_LAUNCHER_URL = rr['redirectUrl']
			self.config.GAME_LAUNCHER_TOKEN = rr['token']
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
			self.configObject.update("refreshCode", data['refreshCode'])
			self.configObject.update("accessToken", data['accessToken'])
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

		rr = self.utils.decrypt(r, self.config.encryptionKey)
		if rr == None:
			logger.error("Unknown")
			exit()

		logger.debug(rr)
		rr = self.utils.decrypt(json.loads(rr)['fcmToken'], self.config.config_Key)
		if rr == None:
			logger.error("Unknown")
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
			self.gamePlaying.printx()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="MeagaRun II Client")
	parser.add_argument("--config", "-c", type=str, default='config.js', help="Specify the path to the configuration file.")
	parser.add_argument("--secondary-config", "-c2", action="store_true", help="Force load secondary configuration.")
	parser.add_argument("--update-token", action="store_true", help="Update authentication token.")
	parser.add_argument("--skip-warn", action="store_true", help="Force contune in warning situation.")
	parser.add_argument("--ignore-chances-limit", action="store_true", help="Prevent the app from auto-terminating when chances are over.")
	parser.add_argument("--browser-mode", action="store_true", help="Allow gameplay to continue in the browser.")

	args = parser.parse_args()
	main = Main(config_file=args.config, force_secondary_config=args.secondary_config, update_token=args.update_token,
		skip_warn=args.skip_warn, keep_play_in_browser=args.browser_mode, continue_on_chances_over=args.ignore_chances_limit)
	
	try:
		main.start()
	except KeyboardInterrupt as e:
		exit()
	
