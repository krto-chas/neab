"""
Konsol-formatter för snygg output i terminalen
Windows-kompatibel med färger och tydliga symboler
"""
from colorama import init, Fore, Style, Back
import sys

# Initiera colorama för Windows-support
init(autoreset=True)

class ConsoleFormatter:
    """Hanterar professionell konsolutskrift med färger och symboler"""

    # Använd Windows-säkra symboler
    SYMBOLS = {
        'success': '[OK]',
        'error': '[!]',
        'info': '[i]',
        'warning': '[!]',
        'arrow': '-->',
        'bullet': '*',
        'step': '>',
        'done': '[DONE]'
    }

    @staticmethod
    def success(msg):
        """Grön success-meddelande"""
        print(f"{Fore.GREEN}{ConsoleFormatter.SYMBOLS['success']} {msg}{Style.RESET_ALL}")

    @staticmethod
    def error(msg):
        """Röd error-meddelande"""
        print(f"{Fore.RED}{ConsoleFormatter.SYMBOLS['error']} ERROR: {msg}{Style.RESET_ALL}")

    @staticmethod
    def info(msg):
        """Blå info-meddelande"""
        print(f"{Fore.CYAN}{ConsoleFormatter.SYMBOLS['info']} {msg}{Style.RESET_ALL}")

    @staticmethod
    def warning(msg):
        """Gul varning"""
        print(f"{Fore.YELLOW}{ConsoleFormatter.SYMBOLS['warning']} VARNING: {msg}{Style.RESET_ALL}")

    @staticmethod
    def header(msg):
        """Stor header med border"""
        border = "=" * 80
        print(f"\n{Fore.BLUE}{Style.BRIGHT}{border}")
        print(f"  {msg.upper()}")
        print(f"{border}{Style.RESET_ALL}\n")

    @staticmethod
    def section(msg):
        """Sektion-header"""
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}>> {msg} <<{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-' * 60}{Style.RESET_ALL}")

    @staticmethod
    def step(number, total, msg):
        """Progress step"""
        percentage = int((number / total) * 100)
        bar_length = 20
        filled = int((number / total) * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"{Fore.CYAN}[{number}/{total}]{Style.RESET_ALL} {msg}")
        print(f"  {Fore.GREEN}{bar}{Style.RESET_ALL} {percentage}%")

    @staticmethod
    def bullet(msg, indent=2):
        """Bullet point med indentation"""
        spaces = " " * indent
        print(f"{spaces}{Fore.WHITE}{ConsoleFormatter.SYMBOLS['bullet']} {msg}{Style.RESET_ALL}")

    @staticmethod
    def table_header(columns):
        """Tabell-header"""
        header = " | ".join(f"{col:20}" for col in columns)
        separator = "-" * len(header)
        print(f"\n{Fore.CYAN}{header}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{separator}{Style.RESET_ALL}")

    @staticmethod
    def table_row(values, color=Fore.WHITE):
        """Tabell-rad"""
        row = " | ".join(f"{str(val):20}" for val in values)
        print(f"{color}{row}{Style.RESET_ALL}")

    @staticmethod
    def progress_complete(msg, filepath=None):
        """Slutförd progress med filsökväg"""
        ConsoleFormatter.success(msg)
        if filepath:
            print(f"  {Fore.WHITE}{ConsoleFormatter.SYMBOLS['arrow']} {filepath}{Style.RESET_ALL}")

    @staticmethod
    def banner():
        """ASCII banner för applikationen"""
        banner = f"""
{Fore.BLUE}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║           NEAB SECURITY ASSESSMENT SUITE                                 ║
║           Riskworkshop med regulatorisk kartläggning                     ║
║                                                                           ║
║           Version 2.0 | Python 3.13                                      ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)

    @staticmethod
    def summary_box(title, data):
        """Sammanfattningsbox med data"""
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}┌─ {title} {'─' * (60 - len(title))}┐{Style.RESET_ALL}")
        for key, value in data.items():
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} {key:30} : {Fore.GREEN}{value}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}└{'─' * 62}┘{Style.RESET_ALL}\n")

    @staticmethod
    def risk_level(level):
        """Färgkodad risknivå"""
        colors = {
            'Mycket hög': Fore.RED,
            'Hög': Fore.YELLOW,
            'Medel': Fore.CYAN,
            'Låg': Fore.GREEN
        }
        color = colors.get(level, Fore.WHITE)
        return f"{color}{level}{Style.RESET_ALL}"

    @staticmethod
    def compliance_status(status):
        """Färgkodad compliance-status"""
        colors = {
            'Uppfyllt': Fore.GREEN,
            'Delvis uppfyllt': Fore.YELLOW,
            'Ej uppfyllt': Fore.RED
        }
        color = colors.get(status, Fore.WHITE)
        return f"{color}{status}{Style.RESET_ALL}"


class ProgressBar:
    """Enkel progressbar för längre operationer"""

    def __init__(self, total, desc="Progress"):
        self.total = total
        self.current = 0
        self.desc = desc

    def update(self, amount=1):
        """Uppdatera progressbar"""
        self.current += amount
        percentage = int((self.current / self.total) * 100)
        bar_length = 40
        filled = int((self.current / self.total) * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\r{self.desc}: {Fore.GREEN}{bar}{Style.RESET_ALL} {percentage}% ({self.current}/{self.total})", end='')

        if self.current >= self.total:
            print()  # Ny rad när klar

    def complete(self):
        """Markera som slutförd"""
        self.current = self.total
        self.update(0)
        ConsoleFormatter.success(f"{self.desc} slutförd!")


# Bekvämlighets-funktioner för snabb användning
def print_success(msg):
    ConsoleFormatter.success(msg)

def print_error(msg):
    ConsoleFormatter.error(msg)

def print_info(msg):
    ConsoleFormatter.info(msg)

def print_warning(msg):
    ConsoleFormatter.warning(msg)

def print_header(msg):
    ConsoleFormatter.header(msg)

def print_section(msg):
    ConsoleFormatter.section(msg)