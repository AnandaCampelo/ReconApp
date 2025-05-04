import unittest
from unittest.mock import patch, MagicMock
from modules.portscan import PortScanner

class TestPortScanner(unittest.TestCase):
    
    @patch('socket.socket')
    def test_portscan_open_port(self, mock_socket):
        mock_instance = MagicMock()
        mock_instance.connect_ex.return_value = 0 
        mock_socket.return_value = mock_instance
        
        scanner = PortScanner("127.0.0.1", "80", 1)
        port, is_open, _ = scanner._tcp_connect_scan(80)
        
        self.assertEqual(port, 80)
        self.assertTrue(is_open)
        mock_instance.close.assert_called_once()
    
    @patch('socket.socket')
    def test_portscan_closed_port(self, mock_socket):
        mock_instance = MagicMock()
        mock_instance.connect_ex.return_value = 1 
        mock_socket.return_value = mock_instance
        
        scanner = PortScanner("127.0.0.1", "80", 1)
        port, is_open, _ = scanner._tcp_connect_scan(80)
        
        self.assertEqual(port, 80)
        self.assertFalse(is_open)

if __name__ == '__main__':
    unittest.main()