from colorama import Fore, Style
from datetime import datetime
import sys

class Logger:
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level.upper()
        self.colors = {
            'DEBUG': Fore.BLUE,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED + Style.BRIGHT
        }
    
    def _log(self, level: str, message: str):
        if self._should_log(level):
            timestamp = datetime.now().strftime('%H:%M:%S')
            color = self.colors.get(level, Fore.RESET)
            print(f"{color}[{timestamp}][{self.name}][{level}] {message}{Style.RESET_ALL}")
            sys.stdout.flush()
    
    def _should_log(self, level: str) -> bool:
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return levels.index(level) >= levels.index(self.level)
    
    def debug(self, message: str):
        self._log('DEBUG', message)
    
    def info(self, message: str):
        self._log('INFO', message)
    
    def success(self, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{Fore.GREEN}[{timestamp}][{self.name}][SUCCESS] {message}{Style.RESET_ALL}")
    
    def warning(self, message: str):
        self._log('WARNING', message)
    
    def error(self, message: str):
        self._log('ERROR', message)
    
    def critical(self, message: str):
        self._log('CRITICAL', message)