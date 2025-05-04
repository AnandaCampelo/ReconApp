import socket
import requests
from typing import List, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import Logger
from utils.helpers import read_wordlist
from time import sleep

class SubdomainEnumerator:
    
    def __init__(self, domain: str, wordlist_path: str = None, threads: int = 20):
        self.domain = domain
        self.wordlist = self._get_wordlist(wordlist_path)
        self.threads = threads
        self.logger = Logger("SubdomainEnum")
        self.found_subdomains: Set[str] = set()
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def _get_wordlist(self, path: str) -> List[str]:
        if path:
            custom = read_wordlist(path)
            if custom:
                return custom
        return self._default_wordlist()

    def _default_wordlist(self) -> List[str]:
        return [
            'www', 'mail', 'webmail', 'admin', 'blog', 'test', 'dev',
            'api', 'secure', 'portal', 'cdn', 'm', 'mobile', 'app',
            'apps', 'cloud', 'static', 'staging', 'prod', 'backup'
        ]

    def _check_dns(self, subdomain: str) -> bool:
        try:
            socket.setdefaulttimeout(2)
            socket.gethostbyname(f"{subdomain}.{self.domain}")
            return True
        except:
            return False

    def _check_http(self, subdomain: str) -> bool:
        url = f"http://{subdomain}.{self.domain}"
        try:
            response = requests.head(
                url,
                headers={'User-Agent': self.USER_AGENT},
                timeout=3,
                allow_redirects=False
            )
            return response.status_code < 400
        except:
            return False

    def _enumerate_with_dns(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self._check_dns, sub): sub
                for sub in self.wordlist
            }
            for future in as_completed(futures):
                if future.result():
                    subdomain = futures[future]
                    self.found_subdomains.add(f"{subdomain}.{self.domain}")

    def _enumerate_with_http(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self._check_http, sub): sub
                for sub in self.wordlist
            }
            for future in as_completed(futures):
                if future.result():
                    subdomain = futures[future]
                    self.found_subdomains.add(f"{subdomain}.{self.domain}")

    def run(self):
        self.logger.info(f"Iniciando enumeração para {self.domain}")
        
        self._enumerate_with_dns()
        
        if not self.found_subdomains:
            self._enumerate_with_http()
        
        if self.found_subdomains:
            self.logger.success(f"\nSubdomínios encontrados ({len(self.found_subdomains)}):")
            for sub in sorted(self.found_subdomains):
                print(f"- {sub}")
        else:
            self.logger.warning("\nNenhum subdomínio encontrado. Recomendações:")
            self.logger.warning("1. Use uma wordlist personalizada com '-w arquivo.txt'")
            self.logger.warning("2. Tente domínios menos protegidos que google.com")
            self.logger.warning("3. Aumente o timeout no código para redes mais lentas")