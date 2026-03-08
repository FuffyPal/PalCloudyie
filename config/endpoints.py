"""
PalCloudy Endpoints Configuration
Tüm OVH ve partner API endpoint'lerinin tanımlanması
"""

# OVH Ana Endpoint'leri
OVH_ENDPOINTS = {
    "ovh-eu": {
        "name": "OVHcloud Europe",
        "description": "Avrupa API uç noktası",
        "url": "https://eu.api.ovh.com",
        "regions": ["France", "Netherlands", "Germany", "UK"],
        "api_base": "ovh-eu"
    },
    "ovh-us": {
        "name": "OVHcloud US",
        "description": "ABD API uç noktası",
        "url": "https://api.ovh.com",
        "regions": ["Canada (Montreal)", "United States (Beaumont)"],
        "api_base": "ovh-us"
    },
    "ovh-ca": {
        "name": "OVHcloud North America",
        "description": "Kuzey Amerika API uç noktası",
        "url": "https://ca.api.ovh.com",
        "regions": ["Canada"],
        "api_base": "ovh-ca"
    },
}

# So you Start Endpoint'leri
SOYOUSTART_ENDPOINTS = {
    "soyoustart-eu": {
        "name": "So you Start Europe",
        "description": "So you Start Avrupa API uç noktası",
        "url": "https://eu.api.soyoustart.com",
        "regions": ["France"],
        "api_base": "soyoustart-eu"
    },
    "soyoustart-ca": {
        "name": "So you Start North America",
        "description": "So you Start Kuzey Amerika API uç noktası",
        "url": "https://ca.api.soyoustart.com",
        "regions": ["Canada"],
        "api_base": "soyoustart-ca"
    },
}

# Kimsufi Endpoint'leri
KIMSUFI_ENDPOINTS = {
    "kimsufi-eu": {
        "name": "Kimsufi Europe",
        "description": "Kimsufi Avrupa API uç noktası",
        "url": "https://eu.api.kimsufi.com",
        "regions": ["France"],
        "api_base": "kimsufi-eu"
    },
    "kimsufi-ca": {
        "name": "Kimsufi North America",
        "description": "Kimsufi Kuzey Amerika API uç noktası",
        "url": "https://ca.api.kimsufi.com",
        "regions": ["Canada"],
        "api_base": "kimsufi-ca"
    },
}

# Tüm Endpoint'leri Birleştir
ALL_ENDPOINTS = {
    **OVH_ENDPOINTS,
    **SOYOUSTART_ENDPOINTS,
    **KIMSUFI_ENDPOINTS,
}

# Endpoint Kategorileri (UI için)
ENDPOINT_GROUPS = {
    "OVHcloud": OVH_ENDPOINTS,
    "So you Start": SOYOUSTART_ENDPOINTS,
    "Kimsufi": KIMSUFI_ENDPOINTS,
}


def get_endpoint_info(endpoint_id: str) -> dict:
    """
    Verilen endpoint ID'sine göre detaylı bilgi döndürür.
    
    Args:
        endpoint_id: Endpoint tanımlayıcısı (örn: 'ovh-eu')
    
    Returns:
        dict: Endpoint bilgisi veya boş dict
    """
    return ALL_ENDPOINTS.get(endpoint_id, {})


def get_endpoints_by_group(group_name: str) -> dict:
    """
    Belirli bir grubuluğa ait endpoint'leri döndürür.
    
    Args:
        group_name: Grup adı ('OVHcloud', 'So you Start', vb.)
    
    Returns:
        dict: Grup endpoint'leri
    """
    return ENDPOINT_GROUPS.get(group_name, {})


def list_all_endpoints() -> dict:
    """
    Tüm endpoint'leri kategorize ederek döndürür.
    
    Returns:
        dict: Kategorize edilmiş endpoint'ler
    """
    return ENDPOINT_GROUPS.copy()


# Test Fonksiyonu
if __name__ == "__main__":
    print("Tüm Endpoint'ler:")
    print()
    
    for group, endpoints in list_all_endpoints().items():
        print(f"📦 {group}:")
        for endpoint_id, endpoint_info in endpoints.items():
            print(f"  • {endpoint_id:20} → {endpoint_info['name']}")
            print(f"    └─ {endpoint_info['description']}")
        print()
