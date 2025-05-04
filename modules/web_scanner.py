import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional
from utils.logger import Logger
from colorama import Fore

class WebScanner:
    
    COMMON_TECH = {
        'CMS': ['wordpress', 'joomla', 'drupal'],
        'Web Servers': ['apache', 'nginx', 'iis'],
        'Frameworks': ['laravel', 'django', 'rails'],
        'JavaScript': ['jquery', 'react', 'vue', 'angular']
    }
    
    COMMON_FILES = [
        'robots.txt', 'sitemap.xml', '.git/HEAD',
        'wp-config.php', 'admin.php', 'login.php'
    ]
    
    def __init__(self, url: str, aggressive: bool = False):
        self.base_url = url if url.startswith(('http://', 'https://')) else f'http://{url}'
        self.aggressive = aggressive
        self.session = requests.Session()
        self.logger = Logger("WebScanner")
        self.tech_found = {}
        self.vulnerabilities = []
        
    def _get_tech_from_headers(self, headers: Dict) -> List[str]:
        tech = []
        server = headers.get('Server', '').lower()
        x_powered = headers.get('X-Powered-By', '').lower()
        
        for category, technologies in self.COMMON_TECH.items():
            for t in technologies:
                if t in server or t in x_powered:
                    tech.append(f"{category}: {t}")
        
        return tech
    
    def _get_tech_from_html(self, html: str) -> List[str]:
        tech = []
        soup = BeautifulSoup(html, 'html.parser')
        
        meta_generator = soup.find('meta', attrs={'name': 'generator'})
        if meta_generator:
            tech.append(f"Generator: {meta_generator.get('content', '')}")
        
        for script in soup.find_all('script'):
            src = script.get('src', '').lower()
            for t in self.COMMON_TECH['JavaScript']:
                if t in src:
                    tech.append(f"JavaScript: {t}")
        
        return tech
    
    def _check_common_files(self) -> Dict[str, int]:
        results = {}
        
        for file in self.COMMON_FILES:
            url = urljoin(self.base_url, file)
            try:
                response = self.session.head(url, timeout=3)
                results[file] = response.status_code
            except:
                results[file] = 0
        
        return results
    
    def _check_security_headers(self) -> Dict[str, str]:
        security_headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'Referrer-Policy'
        ]
        
        headers = self.session.head(self.base_url, timeout=3).headers
        return {h: headers.get(h, 'Ausente') for h in security_headers}
    
    def _check_vulnerabilities(self) -> List[str]:
        vulns = []
        
        try:
            response = self.session.request('OPTIONS', self.base_url, timeout=3)
            allowed = response.headers.get('Allow', '')
            if 'PUT' in allowed or 'DELETE' in allowed:
                vulns.append(f"Métodos HTTP perigosos permitidos: {allowed}")
        except:
            pass
        
        test_dir = urljoin(self.base_url, 'images/')
        try:
            response = self.session.get(test_dir, timeout=3)
            if '<directory' in response.text.lower():
                vulns.append("Directory listing ativado")
        except:
            pass
        
        return vulns
    
    def run(self):
        self.logger.info(f"Iniciando scan web em {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=5)
            
            self.tech_found['headers'] = self._get_tech_from_headers(response.headers)
            self.tech_found['html'] = self._get_tech_from_html(response.text)
            
            common_files = self._check_common_files()
            
            security_headers = self._check_security_headers()
            
            if self.aggressive:
                self.vulnerabilities = self._check_vulnerabilities()
            
            self._display_results(common_files, security_headers)
            
        except Exception as e:
            self.logger.error(f"Erro durante o scan: {e}")
    
    def _display_results(self, common_files: Dict, security_headers: Dict):
        print(f"\n{Fore.YELLOW}=== Tecnologias Identificadas ==={Fore.RESET}")
        if not any(self.tech_found.values()):
            print("Nenhuma tecnologia identificada")
        else:
            for source, techs in self.tech_found.items():
                if techs:
                    print(f"\n{source.capitalize()}:")
                    for tech in techs:
                        print(f"  {Fore.CYAN}{tech}{Fore.RESET}")
        
        print(f"\n{Fore.YELLOW}=== Arquivos/Diretórios Comuns ==={Fore.RESET}")
        for file, status in common_files.items():
            if status == 200:
                print(f"  {Fore.GREEN}{file} (200){Fore.RESET}")
            elif status > 0:
                print(f"  {file} ({status})")
        
        print(f"\n{Fore.YELLOW}=== Headers de Segurança ==={Fore.RESET}")
        for header, value in security_headers.items():
            color = Fore.GREEN if value != 'Ausente' else Fore.RED
            print(f"  {header}: {color}{value}{Fore.RESET}")
        
        if self.aggressive and self.vulnerabilities:
            print(f"\n{Fore.YELLOW}=== Possíveis Vulnerabilidades ==={Fore.RESET}")
            for vuln in self.vulnerabilities:
                print(f"  {Fore.RED}{vuln}{Fore.RESET}")