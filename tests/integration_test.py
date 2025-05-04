import unittest
from modules.portscan import PortScanner
from modules.dns_enum import DNSEnumerator
import socket

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_domain = "example.com"
        cls.test_ip = "127.0.0.1"
    
    def test_portscan_integration(self):
        scanner = PortScanner(self.test_ip, "80", 1)
        port, is_open, _ = scanner._tcp_connect_scan(80)
        
        self.assertIsInstance(port, int)
        self.assertIsInstance(is_open, bool)
        
        if self.test_ip == "127.0.0.1":
            self.assertEqual(port, 80)
    
    def test_dns_integration(self):
        enumerator = DNSEnumerator(self.test_domain)
        records = enumerator._query_record("A")
        
        self.assertIsInstance(records, list)
        
        for ip in records:
            try:
                socket.inet_aton(ip)
            except socket.error:
                self.fail(f"IP inválido retornado: {ip}")

if __name__ == '__main__':
    unittest.main()