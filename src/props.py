class Color:

	# \033[38;2;<R>;<G>;<B>m  # Foreground
	# \033[48;2;<R>;<G>;<B>m  # Background
	
	F_GRAY = '\033[38;2;51;51;51m'

	F_LOG_INFO = '\033[38;2;70;150;190m'
	F_LOG_WARN = '\033[38;2;205;193;7m'
	F_LOG_ERROR = '\033[38;2;180;76;60m'
	F_LOG_DEFAULT = '\033[38;2;189;195;199m'

	B_LOG_INFO = '\033[48;2;10;20;80m'
	B_LOG_WARN = '\033[48;2;80;50;0m'
	B_LOG_ERROR = '\033[48;2;80;10;10m'

	B_PROGRESS = '\033[48;2;20;20;20m'
	F_PROGRESS = '\033[38;2;10;240;140m'

	RESET = '\x1b[0m'
	
	OWNER = '\033[38;2;30;144;255m'
	BORDER = F_GRAY + '\x1b[40m'
	
	SECTION_NAME = '\033[38;2;255;165;0m' + '\x1b[40m'
	SECTION_SYMBOL = F_GRAY + '\x1b[40m'

	BANNER_COMBO = [
		('\033[38;2;180;60;30m', '\033[38;2;150;120;0m'),
		('\033[38;2;60;120;180m', '\033[38;2;0;90;150m'),
		('\033[38;2;60;180;90m', '\033[38;2;0;150;60m'),
		('\033[38;2;120;60;180m', '\033[38;2;90;30;150m'),
		('\033[38;2;180;90;60m', '\033[38;2;150;60;30m'),
		('\033[38;2;180;60;120m', '\033[38;2;150;30;90m'),
		('\033[38;2;90;180;60m', '\033[38;2;60;150;30m'),
		('\033[38;2;180;180;60m', '\033[38;2;150;150;30m'),
		('\033[38;2;60;180;180m', '\033[38;2;30;150;150m'),
		('\033[38;2;180;60;180m', '\033[38;2;150;30;150m'),
	]


	BANNER_FG = ('\033[38;2;180;60;30m', '\033[38;2;60;180;30m', '\033[38;2;100;16;227m',
				'\033[38;2;30;180;60m', '\033[38;2;24;100;214m')

	# BANNER_BG_R = '\033[38;2;150;120;0m'
	# BANNER_FG = '\033[38;2;30;144;255m'

	SYMBOL_SEC_A = '\033[38;2;30;144;255m'
	HEADER_SEC_A = '\033[38;2;200;10;140m'
	TEXT_SEC_A = '\033[38;2;50;150;250m'

	SYMBOL_SEC_B = '\x1b[91m'
	HEADER_SEC_B = '\x1b[97m'
	TEXT_SEC_B = '\x1b[92m'

	SYMBOL_SEC_C = '\x1b[95m'
	HEADER_SEC_C = '\x1b[97m'
	TEXT_SEC_C   = '\x1b[92m'

	SYMBOL_SEC_D = '\x1b[92m'
	HEADER_SEC_D = '\x1b[97m'
	TEXT_SEC_D = '\x1b[94m'

	B_BLACK = '\x1b[40m'
	F_BLUE = '\x1b[34m'
	F_YELLOW = '\x1b[33m'
	F_RED = '\x1b[31m'
	F_LIGHT_BLCK = '\x1b[90m'
	F_WHITE = '\x1b[37m'
	F_GREEN = '\x1b[32m'

	GIFT_LOW = F_RED
	GIFT_MID = F_YELLOW
	GIFT_HIGH = F_GREEN

class Border:

	TOP_LEFT =     Color.BORDER + "╓" #"╔" #"┏"
	TOP_RIGHT =    Color.BORDER + "╖" #"╗" #"┓"
	BOTTOM_LEFT =  Color.BORDER + "╙" #"╚" #"┗"
	BOTTOM_RIGHT = Color.BORDER + "╜" #"╝" #"┛"
	HORIZONTAL =   Color.BORDER + "─" #"━"
	VERTICAL =     Color.BORDER + "║" #"┃"
	TOP_SPLIT =    Color.BORDER + "╥" #"┳" 
	BOTTOM_SPLIT = Color.BORDER + "╨" #"┻"
	LEFT_SPLIT =   Color.BORDER + "╟" #"┣"
	RIGHT_SPLIT =  Color.BORDER + "╢" #"┫"
	CROSS =        Color.BORDER + "╫" #"╋"

	HORIZONTAL_2   = Color.BORDER + "═" #"━"
	BOTTOM_SPLIT_2 = Color.BORDER + "╩" #"┻"
	BOTTOM_LEFT_2  =  Color.BORDER + "╚" #"┗"
	BOTTOM_RIGHT_2 = Color.BORDER + "╝" #"┛"

	HEADER_LEFT =  Color.BORDER + "┨" + Color.SECTION_NAME #"▐"
	HEADER_RIGHT = Color.BORDER + "┠" #"▌"

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
