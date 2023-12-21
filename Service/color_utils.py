from colorama import Fore, Back, Style

colors = {
    "info": Fore.BLUE,
    "warning": Fore.YELLOW,
    "error": Fore.RED,
    "success": Fore.GREEN,
    "prompt": Fore.CYAN,
    "menu": Fore.MAGENTA
}

def colored_print(message, color):
    print(f"{colors.get(color, '')}{message}{Style.RESET_ALL}")

