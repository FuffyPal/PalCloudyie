"""
PalCloudy - API: Sunucu Detayları
/dedicated/server/{serviceName} endpoint'ine GET isteği gönder
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def get_server_details(client, service_name: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Belirli bir dedicated sunucunun tüm detaylarını al.
    
    Args:
        client: OVH API client (ovh.Client)
        service_name: Sunucu adı (ör: "ns123456.ip-1-2-3.eu")
    
    Returns:
        (success: bool, details: Dict, message: str)
    
    Example:
        >>> success, details, msg = get_server_details(client, "ns123456.ip-1-2-3.eu")
        >>> if success:
        ...     print(f"IP: {details['ip']}")
        ...     print(f"OS: {details['os']}")
    """
    try:
        logger.info(f"📋 Sunucu detayları getiriliyor: {service_name}")
        
        # API çağrısı
        server_info = client.get(f'/dedicated/server/{service_name}')
        
        if not server_info:
            return False, {}, f"❌ Sunucu bulunamadı: {service_name}"
        
        # Detayları standartlaştır
        details = {
            # Temel Bilgiler
            'name': server_info.get('serviceName', service_name),
            'state': server_info.get('state', 'unknown'),
            
            # Ağ Bilgileri
            'ip': server_info.get('ip', 'N/A'),
            'ipv6': server_info.get('ipv6', 'N/A'),
            'hostname': server_info.get('hostname', 'N/A'),
            
            # İşletim Sistemi
            'os': server_info.get('os', 'Unknown'),
            'os_type': server_info.get('osType', 'linux'),
            
            # Donanım Bilgileri
            'ram': server_info.get('ram', 0),  # MB
            'disk': server_info.get('disk', 0),  # Bytes
            'cpu': server_info.get('cpu', 'N/A'),
            'cpu_count': server_info.get('cpuCount', 0),
            'cores': server_info.get('cores', 0),
            'threads': server_info.get('threads', 0),
            
            # Depolama
            'root_device': server_info.get('rootDevice', '/dev/sda'),
            'disk_type': server_info.get('diskType', 'N/A'),
            
            # Konum
            'datacenter': server_info.get('datacenter', 'Unknown'),
            'region': server_info.get('region', 'Unknown'),
            'rack': server_info.get('rack', 'Unknown'),
            
            # Ek Bilgiler
            'support_level': server_info.get('supportLevel', 'standard'),
            'offer': server_info.get('offer', 'Unknown'),
            'serial_number': server_info.get('serialNumber', 'N/A'),
            'bios': server_info.get('bios', 'N/A'),
            'firmware': server_info.get('firmware', 'N/A'),
        }
        
        logger.info(f"✅ {service_name} detayları başarıyla getirildi")
        return True, details, f"✅ Sunucu detayları başarıyla getirildi"
        
    except Exception as e:
        error_msg = f"❌ Sunucu detayları getirilemedi: {str(e)}"
        logger.error(error_msg)
        return False, {}, error_msg


def get_server_status_summary(client, service_name: str) -> Tuple[bool, Dict[str, str], str]:
    """
    Sunucunun hızlı durum özetini al (CPU, RAM, Disk).
    
    Args:
        client: OVH API client
        service_name: Sunucu adı
    
    Returns:
        (success: bool, status: Dict, message: str)
    """
    try:
        logger.info(f"🔍 Sunucu durumu kontrol ediliyor: {service_name}")
        
        # API çağrısı
        details, _, _ = get_server_details(client, service_name)
        
        if not details:
            return False, {}, "❌ Sunucu bilgileri alınamadı"
        
        # Durum özeti oluştur
        status = {
            'state': details.get('state', 'unknown'),
            'cpu': details.get('cpu', 'N/A'),
            'ram': f"{details.get('ram', 0)} MB",
            'disk': f"{details.get('disk', 0)} Bytes",
            'os': details.get('os', 'Unknown'),
            'datacenter': details.get('datacenter', 'Unknown'),
        }
        
        return True, status, "✅ Sunucu durumu başarıyla alındı"
        
    except Exception as e:
        return False, {}, f"❌ Durum alınamadı: {str(e)}"


# Örnek Çıktı
EXAMPLE_DETAILS = {
    'name': 'ns123456.ip-1-2-3.eu',
    'state': 'ok',
    'ip': '1.2.3.4',
    'ipv6': '2001:db8::1',
    'hostname': 'ns123456.ip-1-2-3.eu',
    'os': 'Linux Debian 11 (64)',
    'os_type': 'linux',
    'ram': 32768,
    'disk': 1099511627776,
    'cpu': 'Intel Xeon E5-2650 v3 @ 2.30GHz',
    'cpu_count': 1,
    'cores': 10,
    'threads': 20,
    'root_device': '/dev/sda',
    'disk_type': 'SSD',
    'datacenter': 'sbg',
    'region': 'eu',
    'rack': 'rack123',
    'support_level': 'standard',
    'offer': 'Advanced 3',
    'serial_number': 'ABC123DEF456',
    'bios': '2.3.0',
    'firmware': '1.2.3',
}
