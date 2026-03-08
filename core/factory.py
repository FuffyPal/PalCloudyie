"""
PalCloudy API Client Factory
Endpoint seçimine göre ovh.Client nesnesi üreten fabrika modülü.
"""

from typing import Optional

try:
    import ovh
    HAS_OVH = True
except ImportError:
    HAS_OVH = False
    # Demo için mock client
    class MockOVHClient:
        def __init__(self, **kwargs):
            self.endpoint = kwargs.get('endpoint', 'unknown')
            self.app_key = kwargs.get('application_key', 'N/A')
        
        def get(self, path):
            if path == '/me':
                return {'nichandle': 'demo-user', 'email': 'demo@example.com'}
            elif '/dedicated/server' in path:
                return ['server1.example.com', 'server2.example.com']
            return {}
    
    ovh = type('ovh', (), {'Client': MockOVHClient})()


# Endpoint Haritası
ENDPOINTS_MAP = {
    "ovh-eu": "ovh-eu",
    "ovh-us": "ovh-us",
    "ovh-ca": "ovh-ca",
    "soyoustart-eu": "soyoustart-eu",
    "soyoustart-ca": "soyoustart-ca",
    "kimsufi-eu": "kimsufi-eu",
    "kimsufi-ca": "kimsufi-ca",
}

# Endpoint Açıklamaları (UI için)
ENDPOINT_LABELS = {
    "ovh-eu": "OVHcloud Europe",
    "ovh-us": "OVHcloud US",
    "ovh-ca": "OVHcloud North America",
    "soyoustart-eu": "So you Start Europe",
    "soyoustart-ca": "So you Start North America",
    "kimsufi-eu": "Kimsufi Europe",
    "kimsufi-ca": "Kimsufi North America",
}


def create_client(
    endpoint: str,
    app_key: str,
    app_secret: str,
    consumer_key: str
) -> Optional[ovh.Client]:
    """
    Seçilen endpoint'e göre OVH API Client oluşturur.
    
    Args:
        endpoint: Endpoint adı (ovh-eu, soyoustart-ca, vb.)
        app_key: OVH API Application Key
        app_secret: OVH API Application Secret
        consumer_key: OVH API Consumer Key
    
    Returns:
        Başarılı ise ovh.Client nesnesi, aksi halde None
    
    Raises:
        ValueError: Geçersiz endpoint adı verilirse
    """
    
    # Endpoint validasyonu
    if endpoint not in ENDPOINTS_MAP:
        raise ValueError(
            f"Geçersiz endpoint: {endpoint}. "
            f"Geçerli endpoints: {', '.join(ENDPOINTS_MAP.keys())}"
        )
    
    try:
        # ovh.Client oluştur
        client = ovh.Client(
            endpoint=ENDPOINTS_MAP[endpoint],
            application_key=app_key,
            application_secret=app_secret,
            consumer_key=consumer_key
        )
        return client
    
    except Exception as e:
        print(f"Client oluşturma hatası: {str(e)}")
        return None


def get_available_endpoints() -> dict:
    """
    Tüm kullanılabilir endpoint'leri ve açıklamalarını döndürür.
    
    Returns:
        dict: {endpoint_id: endpoint_label} formatında endpoint listesi
    """
    return ENDPOINT_LABELS.copy()


def validate_endpoint(endpoint: str) -> bool:
    """
    Endpoint adının geçerli olup olmadığını kontrol eder.
    
    Args:
        endpoint: Kontrol edilecek endpoint adı
    
    Returns:
        bool: Geçerli ise True, aksi halde False
    """
    return endpoint in ENDPOINTS_MAP
