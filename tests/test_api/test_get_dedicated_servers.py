"""
PalCloudy - Test: Dedicated Servers API
get_dedicated_servers() fonksiyonunu test et
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from api.get_dedicated_servers import (
    get_dedicated_servers,
    parse_server_response,
    EXAMPLE_RESPONSE
)


class TestGetDedicatedServers(unittest.TestCase):
    """get_dedicated_servers() fonksiyonunu test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        # Mock OVH client oluştur
        self.mock_client = Mock()
    
    def test_successful_server_list_retrieval(self):
        """✅ Başarılı sunucu listesi alma"""
        # Mock setup
        server_names = ['ns123456.ip-1-2-3.eu', 'ns654321.ip-5-6-7.eu']
        self.mock_client.get.side_effect = [
            server_names,  # İlk çağrı: sunucu adları
            {'name': server_names[0], 'ip': '1.2.3.4', 'state': 'ok'},  # İkinci çağrı: detaylar
            {'name': server_names[1], 'ip': '5.6.7.8', 'state': 'ok'},  # Üçüncü çağrı: detaylar
        ]
        
        # Test çalıştır
        success, servers, message = get_dedicated_servers(self.mock_client)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(len(servers), 2)
        self.assertEqual(servers[0]['name'], server_names[0])
        self.assertEqual(servers[0]['ip'], '1.2.3.4')
        self.assertIn('✅', message)
    
    def test_empty_server_list(self):
        """✅ Boş sunucu listesi (hesapta sunucu yok)"""
        # Mock setup
        self.mock_client.get.return_value = []
        
        # Test çalıştır
        success, servers, message = get_dedicated_servers(self.mock_client)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(len(servers), 0)
        self.assertIn('Sunucu bulunamadı', message)
    
    def test_api_error_handling(self):
        """✅ API hatası yönetimi"""
        # Mock setup
        self.mock_client.get.side_effect = Exception("API Error: Connection timeout")
        
        # Test çalıştır
        success, servers, message = get_dedicated_servers(self.mock_client)
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(len(servers), 0)
        self.assertIn('❌', message)
    
    def test_partial_server_retrieval_with_errors(self):
        """✅ Kısmi sunucu listesi (bazı sunucular başarısız)"""
        # Mock setup
        server_names = ['ns123456.ip-1-2-3.eu', 'ns654321.ip-5-6-7.eu', 'ns999999.ip-9-10-11.eu']
        
        def get_side_effect(url):
            if url == '/dedicated/server':
                return server_names
            elif 'ns123456' in url:
                return {'name': server_names[0], 'ip': '1.2.3.4', 'state': 'ok'}
            elif 'ns654321' in url:
                raise Exception("Server not found")
            elif 'ns999999' in url:
                return {'name': server_names[2], 'ip': '9.10.11.12', 'state': 'ok'}
        
        self.mock_client.get.side_effect = get_side_effect
        
        # Test çalıştır
        success, servers, message = get_dedicated_servers(self.mock_client)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(len(servers), 2)  # 2 başarılı, 1 başarısız
        self.assertIn('ns123456', servers[0]['name'])
        self.assertIn('ns999999', servers[1]['name'])


class TestParseServerResponse(unittest.TestCase):
    """parse_server_response() fonksiyonunu test et"""
    
    def test_parse_complete_response(self):
        """✅ Tam sunucu bilgisini parse et"""
        server_info = {
            'serviceName': 'ns123456.ip-1-2-3.eu',
            'ip': '1.2.3.4',
            'state': 'ok',
            'os': 'Debian 11',
            'ram': 32768,
            'disk': 1099511627776,
            'cpu': 'Intel Xeon',
            'datacenter': 'sbg',
        }
        
        result = parse_server_response(server_info)
        
        self.assertEqual(result['name'], 'ns123456.ip-1-2-3.eu')
        self.assertEqual(result['ip'], '1.2.3.4')
        self.assertEqual(result['ram'], 32768)
        self.assertEqual(result['datacenter'], 'sbg')
    
    def test_parse_partial_response(self):
        """✅ Eksik bilgi ile parse et (default değerler)"""
        server_info = {
            'serviceName': 'ns123456.ip-1-2-3.eu',
            'ip': '1.2.3.4',
            # Diğer alanlar yok
        }
        
        result = parse_server_response(server_info)
        
        self.assertEqual(result['name'], 'ns123456.ip-1-2-3.eu')
        self.assertEqual(result['ip'], '1.2.3.4')
        self.assertEqual(result['state'], 'unknown')  # Default
        self.assertEqual(result['ram'], 0)  # Default


class TestExampleData(unittest.TestCase):
    """Örnek veri doğruluğunu test et"""
    
    def test_example_response_structure(self):
        """✅ Örnek response yapısı doğru"""
        self.assertIsInstance(EXAMPLE_RESPONSE, list)
        self.assertEqual(len(EXAMPLE_RESPONSE), 2)
        
        for server in EXAMPLE_RESPONSE:
            self.assertIn('name', server)
            self.assertIn('ip', server)
            self.assertIn('state', server)
            self.assertIn('os', server)


# Test runner
if __name__ == '__main__':
    # Test verbose mode'da çalıştır
    unittest.main(verbosity=2)
