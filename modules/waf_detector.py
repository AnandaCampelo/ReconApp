import requests
from typing import Optional
from utils.logger import Logger

class WAFDetector:
    
    COMMON_WAFS = {
        'Cloudflare': ['cloudflare', '__cfduid'],
        'Akamai': ['akamai', 'ak_bmsc'],
        'Imperva': ['imperva', 'incap_ses_'],
        'AWS WAF': ['aws', 'awselb'],
        'ModSecurity': ['mod_security', 'modsecurity']
    }
    
    def __init__(self, target: str):
        self.target = target if target.startswith(('http://', 'https://')) else f'http://{target}'
        self.logger = Logger("WAFDetector")
        
    def _check_headers(self, headers: dict) -> Optional[str]:
        for waf, signatures in self.COMMON_WAFS.items():
            for sig in signatures:
                for header, value in headers.items():
                    if sig.lower() in header.lower() or sig.lower() in value.lower():
                        return waf
        return None
    
    def _check_cookies(self, cookies: dict) -> Optional[str]:
        """Verifica cookies por sinais de WAF"""
        for waf, signatures in self.COMMON_WAFS.items():
            for sig in signatures:
                for cookie in cookies:
                    if sig.lower() in cookie.lower():
                        return waf
        return None
    
    def run(self):
        try:
            self.logger.info(f"Verificando WAF em {self.target}")
            
            response = requests.get(self.target, timeout=5)
            
            waf = self._check_headers(response.headers)
            
            if not waf:
                waf = self._check_cookies(response.cookies.get_dict())
            
            if waf:
                self.logger.success(f"WAF detectado: {waf}")
            else:
                self.logger.warning("Nenhum WAF conhecido detectado")
                
        except requests.RequestException as e:
            self.logger.error(f"Erro ao conectar ao alvo: {e}")