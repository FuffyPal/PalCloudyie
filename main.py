#!/usr/bin/env python3
"""
PalCloudy - OVH Cloud Management Panel
Entry point dosyası - Faz 2: Login UI & Authentication
"""

import sys
import os

# Proje kökleri yolu (debug için)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Faz 2: GUI ile başlat
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from app import run_application
    USE_GUI = True
except (ImportError, ValueError):
    # GUI yoksa CLI mod
    USE_GUI = False
    from core.factory import create_client, get_available_endpoints
    from api.test_connection import run_full_diagnostics


def main():
    """
    PalCloudy uygulamasını başlatan ana fonksiyon.
    Faz 2'de: Libadwaita GUI ile başlat, GUI yoksa CLI test modu.
    """

    if USE_GUI:
        print("=" * 60)
        print("🚀 PalCloudy - OVH Cloud Management Panel")
        print("=" * 60)
        print("🎨 GUI modu etkinleştiriliyor...")
        print()

        # GUI uygulamasını çalıştır
        return run_application()

    else:
        # CLI Test Modu (GUI yüklü değilse)
        print("=" * 60)
        print("🚀 PalCloudy - OVH Cloud Management Panel")
        print("=" * 60)
        print("⚠️  Libadwaita/GTK4 bulunamadı! CLI test modunda çalışıyor...")
        print()

        # Kullanılabilir endpoint'leri göster
        print("📍 Kullanılabilir Endpoints:")
        endpoints = get_available_endpoints()
        for endpoint_id, endpoint_label in endpoints.items():
            print(f"   • {endpoint_id:20} → {endpoint_label}")
        print()

        # DEMO: Varsayılan yapılandırma ile test
        print("🔧 Faz 1 - Bağlantı Testi (Demo):")
        print("-" * 60)

        # NOT: Gerçek API anahtarları burada olmazsa, None döner
        # Kullanıcı UI'dan girmeli
        APP_KEY = os.getenv("OVH_APP_KEY", "DEMO_APP_KEY")
        APP_SECRET = os.getenv("OVH_APP_SECRET", "DEMO_APP_SECRET")
        CONSUMER_KEY = os.getenv("OVH_CONSUMER_KEY", "DEMO_CONSUMER_KEY")
        ENDPOINT = "ovh-us"  # Demo endpoint

        print(f"Endpoint: {ENDPOINT}")
        print(f"APP_KEY: {APP_KEY[:10]}..." if len(APP_KEY) > 10 else APP_KEY)
        print()

        try:
            # Client oluştur
            client = create_client(ENDPOINT, APP_KEY, APP_SECRET, CONSUMER_KEY)

            if client is None:
                print("⚠️  Client oluşturulamadı. API anahtarlarını kontrol edin.")
                print()
                print("Geliştirme ortamında test etmek için:")
                print("  export OVH_APP_KEY='your-app-key'")
                print("  export OVH_APP_SECRET='your-app-secret'")
                print("  export OVH_CONSUMER_KEY='your-consumer-key'")
                print("  python3 main.py")
                return 1

            print("✅ Client başarıyla oluşturuldu")
            print()

            # Teşhis testleri çalıştır
            print("🔍 Kapsamlı Teşhis Testleri:")
            print("-" * 60)

            results = run_full_diagnostics(client)

            # Sonuçları yazdır
            for test_name, test_result in results.items():
                if test_name == "client_created":
                    status = "✅" if test_result else "❌"
                    print(f"{status} Client Created: {test_result}")
                elif isinstance(test_result, dict):
                    if "success" in test_result:
                        status = "✅" if test_result["success"] else "❌"
                        print(f"{status} {test_name}: {test_result.get('message', 'N/A')}")
                        if "server_count" in test_result:
                            print(f"   └─ Sunucu Sayısı: {test_result['server_count']}")
                    elif "error" in test_result:
                        print(f"❌ {test_name}: {test_result['error']}")
                    else:
                        print(f"ℹ️  {test_name}:")
                        for key, value in test_result.items():
                            print(f"   └─ {key}: {value}")

            print()
            print("=" * 60)
            print("✅ CLI Test Modu Tamamlandı")
            print("=" * 60)

            return 0

        except Exception as e:
            print(f"❌ Kritik hata: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(main())
