import sys
from modules.portscan import PortScanner
from modules.dns_enum import DNSEnumerator
from modules.subdomain_enum import SubdomainEnumerator
from modules.waf_detector import WAFDetector
from modules.web_scanner import WebScanner
from colorama import init, Fore

init(autoreset=True)  

def show_banner():
    print(Fore.CYAN + r"""
    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗ █████╗ ██████╗ ██████╗
    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║███████║██████╔╝██████╔╝
    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══██║██╔═══╝ ██╔═══╝
    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██║  ██║██║     ██║
    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝
    """ + Fore.RESET)
    
    print(f"{Fore.YELLOW}ReconApp - Ferramenta de Reconhecimento para Pentest{Fore.RESET}")
    print(f"{Fore.YELLOW}Versão 1.0{Fore.RESET}\n")

def show_menu():
    print(f"{Fore.GREEN}Menu Principal:{Fore.RESET}")
    print("1. Portscan (Varredura de Portas)")
    print("2. DNS Lookup (Consulta DNS)")
    print("3. Enumeração de Subdomínios")
    print("4. Detecção de WAF")
    print("5. Scanner Web")
    print("6. Sair")
    print(f"{Fore.CYAN}\nEscolha uma opção (1-6): {Fore.RESET}", end="")

def run_portscan():
    print(f"\n{Fore.YELLOW}=== Portscan ==={Fore.RESET}")
    target = input("Digite o IP ou rede (ex: 192.168.1.1 ou 192.168.1.0/24): ")
    ports = input("Intervalo de portas (ex: 1-1000) [1-1024]: ") or "1-1024"
    threads = input("Número de threads [50]: ") or "50"
    
    try:
        scanner = PortScanner(target, ports, int(threads))
        scanner.run()
    except Exception as e:
        print(f"{Fore.RED}Erro: {e}{Fore.RESET}")

def run_dns_lookup():
    print(f"\n{Fore.YELLOW}=== DNS Lookup ==={Fore.RESET}")
    domain = input("Digite o domínio (ex: example.com): ")
    
    try:
        enumerator = DNSEnumerator(domain)
        enumerator.run()
    except Exception as e:
        print(f"{Fore.RED}Erro: {e}{Fore.RESET}")

def run_subdomain_enum():
    print(f"\n{Fore.YELLOW}=== Enumeração de Subdomínios ==={Fore.RESET}")
    domain = input("Digite o domínio base (ex: example.com): ")
    
    try:
        enumerator = SubdomainEnumerator(domain)
        enumerator.run()
    except Exception as e:
        print(f"{Fore.RED}Erro: {e}{Fore.RESET}")

def run_waf_detector():
    print(f"\n{Fore.YELLOW}=== Detecção de WAF ==={Fore.RESET}")
    target = input("Digite a URL ou IP (ex: https://example.com): ")
    
    try:
        detector = WAFDetector(target)
        detector.run()
    except Exception as e:
        print(f"{Fore.RED}Erro: {e}{Fore.RESET}")

def run_web_scanner():
    print(f"\n{Fore.YELLOW}=== Scanner Web ==={Fore.RESET}")
    url = input("Digite a URL (ex: https://example.com): ")
    aggressive = input("Modo agressivo? (s/n): ").lower() == 's'
    
    try:
        scanner = WebScanner(url, aggressive)
        scanner.run()
    except Exception as e:
        print(f"{Fore.RED}Erro: {e}{Fore.RESET}")

def main(): 
    show_banner()
    
    while True:
        show_menu()
        choice = input().strip()
        
        if choice == '1':
            run_portscan()
        elif choice == '2':
            run_dns_lookup()
        elif choice == '3':
            run_subdomain_enum()
        elif choice == '4':
            run_waf_detector()
        elif choice == '5':
            run_web_scanner()
        elif choice == '6':
            print(f"\n{Fore.YELLOW}Saindo do ReconApp...{Fore.RESET}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}Opção inválida! Tente novamente.{Fore.RESET}")
        
        input(f"\n{Fore.CYAN}Pressione Enter para continuar...{Fore.RESET}")
        print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Programa interrompido pelo usuário.{Fore.RESET}")
        sys.exit(0)