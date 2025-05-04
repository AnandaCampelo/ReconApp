import ipaddress
import re
from typing import Union, Optional, List

import requests

def read_wordlist(path: str) -> List[str]:
    if not path:
        return None
    try:
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return None

def is_valid_ip(target: str) -> bool:
    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        return False

def is_valid_domain(domain: str) -> bool:
    pattern = re.compile(
        r'^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])'
        r'(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$'
    )
    return bool(pattern.match(domain))

def parse_ports(port_str: str) -> List[int]:
    ports = []
    parts = port_str.split(',')
    
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    
    return sorted(set(ports))

def get_http_status(url: str) -> Optional[int]:
    try:
        response = requests.head(url, timeout=3, allow_redirects=False)
        return response.status_code
    except:
        return None