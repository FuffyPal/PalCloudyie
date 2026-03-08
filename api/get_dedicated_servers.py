"""
PalCloudy - API: Dedicated Servers Listesi
/dedicated/server endpoint'ine GET isteği gönder
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def get_dedicated_servers(client) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    OVH API'den tüm dedicated sunucuları listele.
    
    Args:
        client: OVH API client (ovh.Client)
    
    Returns:
        (success: bool, servers: List[Dict], message: str)
        
    Example:
        >>> success, servers, msg = get_dedicated_servers(client)
        >>> if success:
        ...     for server in servers:
        ...         print(f"{server['name']} - {server['ip']} - {server['state']}")
    """
    try:
        logger.info("📋 Dedicated sunucular listeleniyor...")
        
        # OVH API çağrısı: Sunucu adlarını listele
        server_names = client.get('/dedicated/server')
        logger.debug(f"API çağrısı başarılı. {len(server_names)} sunucu bulundu.")
        
        if not server_names:
            return True, [], "✅ Sunucu bulunamadı (hesapta sunucu yok)"
        
        # Her sunucu için detayları al
        servers = []
        for server_name in server_names:
            try:
                server_info = client.get(f'/dedicated/server/{server_name}')
                
                # Temel bilgileri çıkar
                server_data = {
                    'name': server_name,
                    'ip': server_info.get('ip', 'N/A'),
                    'state': server_info.get('state', 'unknown'),
                    'os': server_info.get('os', 'Unknown OS'),
                    'ram': server_info.get('ram', 0),
                    'disk': server_info.get('disk', 0),
                    'cpu': server_info.get('cpu', 'N/A'),
                    'root_device': server_info.get('rootDevice', '/dev/sda'),
                }
                servers.append(server_data)
                logger.debug(f"✅ {server_name} yüklendi")
                
            except Exception as e:
                logger.warning(f"⚠️  {server_name} yüklenemedi: {str(e)}")
                # Bu sunucu başarısız olsa da devam et
                continue
        
        message = f"✅ {len(servers)} sunucu başarıyla yüklendi"
        logger.info(message)
        return True, servers, message
        
    except Exception as e:
        error_msg = f"❌ Sunucuları getirme başarısız: {str(e)}"
        logger.error(error_msg)
        return False, [], error_msg


def parse_server_response(server_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sunucu bilgisini standart formata dönüştür.
    
    Args:
        server_info: OVH API'den dönen sunucu bilgisi
    
    Returns:
        Standartlaştırılmış sunucu verisi
    """
    return {
        'name': server_info.get('serviceName', ''),
        'ip': server_info.get('ip', 'N/A'),
        'state': server_info.get('state', 'unknown'),
        'os': server_info.get('os', 'Unknown'),
        'ram': server_info.get('ram', 0),
        'disk': server_info.get('disk', 0),
        'cpu': server_info.get('cpu', 'N/A'),
        'root_device': server_info.get('rootDevice', '/dev/sda'),
        'datacenter': server_info.get('datacenter', 'Unknown'),
    }


# Örnek çıktı formatı
EXAMPLE_RESPONSE = [
    {
        'name': 'ns123456.ip-1-2-3.eu',
        'ip': '1.2.3.4',
        'state': 'ok',
        'os': 'Linux Debian 11',
        'ram': 32768,  # MB
        'disk': 1099511627776,  # Bytes
        'cpu': 'Intel Xeon E5-2650',
        'root_device': '/dev/sda',
        'datacenter': 'sbg',
    },
    {
        'name': 'ns654321.ip-5-6-7.eu',
        'ip': '5.6.7.8',
        'state': 'ok',
        'os': 'CentOS 7',
        'ram': 16384,
        'disk': 549755813888,
        'cpu': 'Intel Xeon E5-2620',
        'root_device': '/dev/sda',
        'datacenter': 'rbx',
    },
]
