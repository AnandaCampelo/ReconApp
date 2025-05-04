import unittest
from unittest.mock import patch
from modules.dns_enum import DNSEnumerator

class TestDNSEnumerator(unittest.TestCase):
    
    @patch('dns.resolver.Resolver.resolve')
    def test_dns_query(self, mock_resolve):
        mock_resolve.return_value = ["192.168.1.1"]
        
        enumerator = DNSEnumerator("example.com")
        results = enumerator._query_record("A")
        
        self.assertEqual(results, ["192.168.1.1"])

if __name__ == '__main__':
    unittest.main()