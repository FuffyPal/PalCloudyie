"""
PalCloudy API Connection Tester
Oluşturulan client ile bağlantı ve kimlik doğrulama testleri.
"""

import sys
from typing import Tuple, Optional


def test_connection(client) -> Tuple[bool, str]:
    """
    Sağlanan OVH Client ile bağlantı testini gerçekleştirir.
    
    Args:
        client: ovh.Client nesnesi
    
    Returns:
        Tuple[bool, str]: (Başarı durumu, Mesaj)
    """
    
    if client is None:
        return False, "❌ Client nesnesi None. Kimlik bilgileri kontrol edin."
    
    try:
        # /me endpoint'ini sorgulayarak kimlik doğrulamayı test et
        me = client.get('/me')
        
        if me and 'nichandle' in me:
            return True, f"✅ Bağlantı başarılı! Hoşgeldiniz: {me['nichandle']}"
        else:
            return False, "❌ /me endpoint'i beklenmeyen cevap döndürdü"
    
    except Exception as e:
        error_msg = str(e)
        
        # Yaygın hataları yorumla
        if "401" in error_msg or "Unauthorized" in error_msg:
            return False, "❌ Kimlik doğrulama başarısız. API anahtarlarını kontrol edin."
        elif "403" in error_msg or "Forbidden" in error_msg:
            return False, "❌ Erişim reddedildi. Consumer Key geçersiz olabilir."
        elif "Connection" in error_msg or "timeout" in error_msg:
            return False, f"❌ Ağ bağlantısı hatası: {error_msg}"
        else:
            return False, f"❌ Bağlantı hatası: {error_msg}"


def test_server_list(client) -> Tuple[bool, str, Optional[list]]:
    """
    Client ile sunucu listesini sorgular.
    
    Args:
        client: ovh.Client nesnesi
    
    Returns:
        Tuple[bool, str, Optional[list]]: (Başarı, Mesaj, Sunucu listesi)
    """
    
    if client is None:
        return False, "❌ Client nesnesi None", None
    
    try:
        # Dedicated serverları listele
        servers = client.get('/dedicated/server')
        
        if isinstance(servers, list):
            count = len(servers)
            return True, f"✅ {count} dedicated server bulundu", servers
        else:
            return False, "❌ Sunucu listesi alınamadı", None
    
    except Exception as e:
        error_msg = str(e)
        
        if "401" in error_msg:
            return False, "❌ Kimlik doğrulama hatası", None
        elif "404" in error_msg:
            return False, "ℹ️ Herhangi bir sunucu bulunamadı", []
        else:
            return False, f"❌ Sunucu listesi hatası: {error_msg}", None


def run_full_diagnostics(client) -> dict:
    """
    Kapsamlı teşhis testleri çalıştırır.
    
    Args:
        client: ovh.Client nesnesi
    
    Returns:
        dict: Test sonuçları
    """
    
    results = {
        "client_created": client is not None,
        "connection_test": None,
        "server_list_test": None,
        "user_info": None,
    }
    
    if client is None:
        results["error"] = "Client oluşturulamadı"
        return results
    
    # Test 1: Bağlantı ve Kimlik Doğrulama
    success, msg = test_connection(client)
    results["connection_test"] = {"success": success, "message": msg}
    
    if success:
        # Test 2: Sunucu Listesi
        success, msg, servers = test_server_list(client)
        results["server_list_test"] = {
            "success": success,
            "message": msg,
            "server_count": len(servers) if servers else 0
        }
        
        # Test 3: Kullanıcı Bilgisi
        try:
            me = client.get('/me')
            results["user_info"] = {
                "nichandle": me.get('nichandle'),
                "email": me.get('email'),
                "firstname": me.get('firstname'),
                "lastname": me.get('lastname'),
            }
        except Exception as e:
            results["user_info"] = {"error": str(e)}
    
    return results


if __name__ == "__main__":
    # Test için örnek kullanım
    print("API test_connection.py modülü yüklenmiştir.")
    print("run_full_diagnostics(client) ile kapsamlı test yapabilirsiniz.")
