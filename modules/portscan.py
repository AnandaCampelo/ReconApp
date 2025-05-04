import socket
import sys
from typing import List, Tuple, Optional  
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore
from utils.logger import Logger

class PortScanner:
    
    WELL_KNOWN_PORTS = {
        20: "FTP (Data)",
        21: "FTP (Control)",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        3306: "MySQL",
        3389: "RDP",
        8080: "HTTP-Alt"
    }
    
    def __init__(self, target: str, port_range: str = '1-1024', 
                 max_threads: int = 50, stealth: bool = False):
        self.target = target
        self.port_range = port_range
        self.max_threads = max_threads
        self.stealth = stealth
        self.logger = Logger("PortScanner")
        
    def _parse_ports(self) -> List[int]:
        try:
            if ',' in self.port_range:
                return [int(p) for p in self.port_range.split(',')]
            elif '-' in self.port_range:
                start, end = map(int, self.port_range.split('-'))
                return list(range(start, end + 1))
            else:
                return [int(self.port_range)]
        except ValueError:
            self.logger.error("Formato de porta inválido. Use '1-100' ou '22,80,443'")
            sys.exit(1)
    
    def _tcp_connect_scan(self, port: int) -> Tuple[int, bool, Optional[str]]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            service = self.WELL_KNOWN_PORTS.get(port, "Unknown") if result == 0 else None
            return port, result == 0, service
        except Exception as e:
            self.logger.debug(f"Erro ao escanear porta {port}: {e}")
            return port, False, None
        finally:
            sock.close()
    
    def _syn_stealth_scan(self, port: int) -> Tuple[int, bool, Optional[str]]:
        try:
            return self._tcp_connect_scan(port)
        except Exception as e:
            self.logger.error(f"Erro no SYN scan: {e}")
            return port, False, None
    
    def run(self):
        ports = self._parse_ports()
        open_ports = []
        
        self.logger.info(f"Iniciando varredura em {self.target} (Portas: {len(ports)})")
        self.logger.info(f"Modo: {'Stealth (SYN)' if self.stealth else 'TCP Connect'}")
        
        scan_method = self._syn_stealth_scan if self.stealth else self._tcp_connect_scan
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(scan_method, port): port for port in ports}
            
            for future in as_completed(futures):
                port, is_open, service = future.result()
                if is_open:
                    open_ports.append(port)
                    msg = f"Porta {Fore.GREEN}{port}{Fore.RESET} ({service}) {Fore.GREEN}ABERTA{Fore.RESET}"
                    self.logger.success(msg)
        
        self.logger.info(f"Varredura concluída. Portas abertas: {len(open_ports)}")
        self.logger.info(f"Portas abertas: {sorted(open_ports)}")