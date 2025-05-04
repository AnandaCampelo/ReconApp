import dns.resolver
import dns.zone
import dns.query
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import Logger
from colorama import Fore

class DNSEnumerator:
    
    def __init__(self, domain: str, records: List[str] = None, 
                 dns_server: str = None, threads: int = 20):
        self.domain = domain
        self.records = records or ['A', 'AAAA', 'MX', 'TXT', 'NS', 'SOA']
        self.dns_server = dns_server
        self.threads = threads
        self.logger = Logger("DNSEnum")
        
        self.resolver = dns.resolver.Resolver()
        if dns_server:
            self.resolver.nameservers = [dns_server]

    def _query_record(self, record_type: str) -> List[str]:
        try:
            answers = self.resolver.resolve(self.domain, record_type)
            return [str(r) for r in answers]
        except dns.resolver.NoAnswer:
            return []
        except dns.resolver.NXDOMAIN:
            self.logger.error(f"Domínio {self.domain} não existe")
            return []
        except Exception as e:
            self.logger.error(f"Erro ao consultar {record_type}: {e}")
            return []

    def check_zone_transfer(self) -> bool:
        try:
            ns_servers = self._query_record('NS')
            for ns in ns_servers:
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(ns, self.domain))
                    if zone:
                        self.logger.critical(f"Zone transfer VULNERÁVEL em {ns}")
                        return True
                except:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar zone transfer: {e}")
            return False

    def dns_bruteforce(self, wordlist: List[str]) -> Dict[str, List[str]]:
        results = {}
        
        def check_subdomain(sub: str):
            full_domain = f"{sub}.{self.domain}"
            try:
                self.resolver.resolve(full_domain, 'A')
                return full_domain
            except:
                return None
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_subdomain, word): word for word in wordlist}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results[result] = self._query_record('A')
        
        return results

    def run(self):
        self.logger.info(f"Iniciando enumeração DNS para {self.domain}")
        
        if self.check_zone_transfer():
            self.logger.warning("Vulnerabilidade crítica encontrada!")
        
        record_results = {}
        for record in self.records:
            answers = self._query_record(record)
            if answers:
                record_results[record] = answers
                self.logger.success(f"Registros {record}:")
                for answer in answers:
                    print(f"  {Fore.CYAN}{answer}{Fore.RESET}")
        
        self.logger.info("\nResumo da enumeração DNS:")
        for record, values in record_results.items():
            print(f"{Fore.YELLOW}{record}:{Fore.RESET} {len(values)} registros encontrados")