from logger import logger
from logger import CustomFormatterUI
from logger import CustomLogHandlerUI
from props import Color
from props import Symbol
from props import Border

import re
import os
import sys
import time 
import random
from box import Box

class CLUI:

	width, height = 110, 17
	ratio_top = 0.30  # Ratio for the top section

	def __init__(self, instance):

		logHandler = CustomLogHandlerUI(self)
		logHandler.setFormatter(CustomFormatterUI())
		logger.addHandler(logHandler)

		os.system('cls')

		instance.logger = logger
		self.bar_width = 40
		self.next_end = time.time() 
		self.next_beginning = time.time() + 5
		self.gift_history = []
		self.banner_index = random.randint(0, 6)
		self.banner_color_combo_index = random.randint(0, len(Color.BANNER_COMBO) - 1), random.randint(0, len(Color.BANNER_COMBO) - 1)
		self.banner_fg_index = random.randint(0, 4)

		self.data = Box({
			"Game Info": {
				"show_symbol": True,
				"section_symbol":"",
				"show_header": True,
				"Name   ": "None",
				"Chances": "None",
				"Reward ": "None",
				"Next   ": "" + Symbol.SYMBOL_PROGRESS * self.bar_width + ""
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
			Border.LEFT_SPLIT   + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_a_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_a_title + Border.HEADER_RIGHT +
			Border.HORIZONTAL + Border.TOP_SPLIT + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_b_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_b_title + Border.HEADER_RIGHT +
			Border.HORIZONTAL + Border.RIGHT_SPLIT + Color.RESET
		)
		self.mid_horizontal = (
			Border.LEFT_SPLIT + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_c_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_c_title + Border.HEADER_RIGHT  + 
			Border.HORIZONTAL + Border.CROSS + Border.HORIZONTAL * (self.width // 2 - self.getTextLength(sec_d_title) - 4) + 
			Color.SECTION_NAME + Border.HEADER_LEFT + sec_d_title + Border.HEADER_RIGHT +
			Border.HORIZONTAL + Border.RIGHT_SPLIT + Color.RESET
		)
		self.bottom_border = (
			Border.BOTTOM_LEFT_2 + Border.HORIZONTAL_2 * (self.width // 2 - 1) + Border.BOTTOM_SPLIT_2 +
			Border.HORIZONTAL_2 * (self.width // 2 - 10) +
			Color.OWNER + " thiwaK " + Border.HORIZONTAL_2 + Border.BOTTOM_RIGHT_2 + Color.RESET
		)

		self.empty_row_upper = (
			Border.VERTICAL + 
			Color.RESET + " " * (self.width // 2 - 1) + 
			Border.VERTICAL + 
			Color.RESET + " " * (self.width // 2 - 1) + Border.VERTICAL
			)
		self.empty_row_lower = Border.VERTICAL + " " * (self.width - 1) + Border.VERTICAL + Color.RESET

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
			(header_color + item[0] + Color.F_WHITE + ": " if show_header else "") + 
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
			if i%2 == 0:
				output[i] = output[i].replace("⁖", Color.BANNER_COMBO[self.banner_color_combo_index[0]][0] + "⁖" + Color.BANNER_FG[self.banner_fg_index])
			else:
				output[i] = output[i].replace("⁖", Color.BANNER_COMBO[self.banner_color_combo_index[1]][1] + "⁖" + Color.BANNER_FG[self.banner_fg_index])

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
					parta = Border.VERTICAL + Color.RESET + t3_rows[i].ljust(self.width // 2 - 1) + Border.VERTICAL + Color.RESET
					partb = t4_rows[i].ljust(self.width // 2 - 1) + Border.VERTICAL + Color.RESET
					output.append(parta + partb)
					continue

			output.append(self.empty_row_upper)

		output.append(self.bottom_border)
		print("\n".join(output))

		self.msg_row_count = len(output) + 1

	def getBanner(self):

		banner_width = 109

		banner_text = [
			["  __  __                          _____                      _____   _____ ",
			" |  \/  |                        |  __ \                    |_   _| |_   _|",
			" | \  / |   ___    __ _    __ _  | |__) |  _   _   _ __       | |     | |  ",
			" | |\/| |  / _ \  / _` |  / _` | |  _  /  | | | | | '_ \      | |     | |  ",
			" | |  | | |  __/ | (_| | | (_| | | | \ \  | |_| | | | | |    _| |_   _| |_ ",
			" |_|  |_|  \___|  \__, |  \__,_| |_|  \_\  \__,_| |_| |_|   |_____| |_____|",
			"                   __/ |                                                   ",
			"                  |___/                                                    "],
	
			["'||    ||'                         '||''|.                        '||' '||'",
			" |||  |||    ....    ... .  ....    ||   ||  ... ...  .. ...       ||   || ",
			" |'|..'||  .|...||  || ||  '' .||   ||''|'    ||  ||   ||  ||      ||   || ",
			" | '|' ||  ||        |''   .|' ||   ||   |.   ||  ||   ||  ||      ||   || ",
			".|. | .||.  '|...'  '||||. '|..'|' .||.  '|'  '|..'|. .||. ||.    .||. .||.",
			"                   .|....'                                                 ",],
																						
			["MM    MM                        RRRRRR                     IIIII IIIII ",
			"MMM  MMM   eee   gggggg   aa aa RR   RR uu   uu nn nnn      III   III  ",
			"MM MM MM ee   e gg   gg  aa aaa RRRRRR  uu   uu nnn  nn     III   III  ",
			"MM    MM eeeee  ggggggg aa  aaa RR  RR  uu   uu nn   nn     III   III  ",
			"MM    MM  eeeee      gg  aaa aa RR   RR  uuuu u nn   nn    IIIII IIIII ",
			"                 ggggg                                                 ",],
	
			["ooo        ooooo                                ooooooooo.                                ooooo ooooo ",
			"`88.       .888'                                `888   `Y88.                              `888' `888' ",
			" 888b     d'888   .ooooo.   .oooooooo  .oooo.    888   .d88' oooo  oooo  ooo. .oo.         888   888  ",
			" 8 Y88. .P  888  d88' `88b 888' `88b  `P  )88b   888ooo88P'  `888  `888  `888P\"Y88b        888   888  ",
			" 8  `888'   888  888ooo888 888   888   .oP\"888   888`88b.     888   888   888   888        888   888  ",
			" 8    Y     888  888    .o `88bod8P'  d8(  888   888  `88b.   888   888   888   888        888   888  ",
			"o8o        o888o `Y8bod8P' `8oooooo.  `Y888\"\"8o o888o  o888o  `V88V\"V8P' o888o o888o      o888o o888o ",
			"                           d\"     YD                                                                  ",
			"                           \"Y88888P'                                                                  ",],
																																																					 
	
			["███╗   ███╗███████╗ ██████╗  █████╗ ██████╗ ██╗   ██╗███╗   ██╗    ██╗██╗",
			"████╗ ████║██╔════╝██╔════╝ ██╔══██╗██╔══██╗██║   ██║████╗  ██║    ██║██║",
			"██╔████╔██║█████╗  ██║  ███╗███████║██████╔╝██║   ██║██╔██╗ ██║    ██║██║",
			"██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║██╔══██╗██║   ██║██║╚██╗██║    ██║██║",
			"██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║██║  ██║╚██████╔╝██║ ╚████║    ██║██║",
			"╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═╝╚═╝",],
																							
			[".88b  d88. d88888b  d888b   .d8b.  d8888b. db    db d8b   db      d888888b d888888b ",
			"88'YbdP`88 88'     88' Y8b d8' `8b 88  `8D 88    88 888o  88        `88'     `88'   ",
			"88  88  88 88ooooo 88      88ooo88 88oobY' 88    88 88V8o 88         88       88    ",
			"88  88  88 88~~~~~ 88  ooo 88~~~88 88`8b   88    88 88 V8o88         88       88    ",
			"88  88  88 88.     88. ~8~ 88   88 88 `88. 88b  d88 88  V888        .88.     .88.   ",
			"YP  YP  YP Y88888P  Y888P  YP   YP 88   YD ~Y8888P' VP   V8P      Y888888P Y888888P ",],
																																														
			["`7MMM.     ,MMF'                           `7MM\"\"\"Mq.                             `7MMF'`7MMF'",
			"  MMMb    dPMM                               MM   `MM.                              MM    MM  ",
			"  M YM   ,M MM  .gP\"Ya   .P\"Ybmmm  ,6\"Yb.    MM   ,M9 `7MM  `7MM  `7MMpMMMb.        MM    MM  ",
			"  M  Mb  M' MM ,M'   Yb :MI    I8 8)   MM    MMmmdM9    MM    MM    MM    MM        MM    MM  ",
			"  M  YM.P'  MM 8M\"\"\"\"\"\"  WmmmmP\"   ,pm9MM    MM  YM.    MM    MM    MM    MM        MM    MM  ",
			"  M  `YM'   MM YM.    , 8M        8M   MM    MM   `Mb.  MM    MM    MM    MM        MM    MM  ",
			".JML. `'  .JMML.`Mbmmd'  YMMMMMb  `Moo9^Yo..JMML. .JMM. `Mbod\"YML..JMML  JMML.    .JMML..JMML.",
			"                        6'     dP                                                            ",
			"                        Ybmmmd'                                                              ",],
		]
		banner_text = [" ", ] + banner_text[self.banner_index] + [" ", ]

		background = []#[Border.TOP_LEFT + (Border.HORIZONTAL * (self.width - 2)) ]

		for index in range(len(banner_text)):

			banner_anim_symbol_len = len(Symbol.banner_animation)

			result = ""

			for i in range(index, banner_width + index):
				result += Symbol.banner_animation[i % banner_anim_symbol_len]

			start = self.current_frame % banner_anim_symbol_len
			result = result[start:] + result[:start]


			if index % 2 == 0:
				background.append(Border.VERTICAL + result[::-1] + Border.VERTICAL)
			else:
				background.append(Border.VERTICAL + result + Border.VERTICAL)

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
			Color.B_PROGRESS + '' +  
			Color.F_PROGRESS + Symbol.SYMBOL_PROGRESS * filled_length + (' ' * (self.bar_width - filled_length)) + 
			'' + Color.B_BLACK + Color.RESET)

		return progress_bar #f"\r{progress_bar} {progress_percentage * 100:.2f}%"

	def updateGiftHistory(self):
		random.seed(42)  # Ensure consistent results if needed

		gifts_per_row = 9
		top_section_height = int(self.height * self.ratio_top) - 1

		self.data["Gift History"] = {
			"show_symbol": False,
			"section_symbol": "",
			"show_header": False,
		}

		history = self.gift_history
		place_holder = Color.BORDER + "|  *  "

		result = Color.BORDER
		row_count = 0

		for i, gift in enumerate(history):
			if str(gift).isdecimal():
				if int(gift) <= 10:
					gift = Color.GIFT_LOW + str(gift) + Color.BORDER
				elif int(gift) <= 200:
					gift = Color.GIFT_MID + str(gift) + Color.BORDER
				else:
					gift = Color.GIFT_HIGH + str(gift) + Color.BORDER
			else:
				gift = Color.BORDER + str(gift) + Color.BORDER

			result += "|" + str(gift).center(5 + self.getANSILength(str(gift)), ' ')

			if (i + 1) % gifts_per_row == 0 or i == len(history) - 1:
				# Fill remaining slots if it's the last row
				if i == len(history) - 1 and (i + 1) % gifts_per_row != 0:
					remaining_slots = gifts_per_row - (i + 1) % gifts_per_row
					result += place_holder * remaining_slots

				# Save the row
				self.data["Gift History"].update({time.time_ns() + random.randint(1, 999): result})
				result = Color.BORDER
				row_count += 1

		# Add padding rows if needed
		if top_section_height > row_count:
			empty_row_count = top_section_height - row_count
			for _ in range(empty_row_count):
				row = place_holder * gifts_per_row
				self.data["Gift History"].update({time.time_ns() + random.randint(1, 999): row})


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

			self.updateGiftHistory()

			self.data["Game Info"]["Next   "] = self.getProgress()

			if self.current_frame == 1000_0000:
				self.current_frame = 0
