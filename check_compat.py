#!/usr/bin/env python3
"""
PalCloudy - Libadwaita 1.8.4 Uyumluluk Kontrolü
Adw API versiyonunu kontrol et ve gerekli düzeltmeleri yap
"""

import gi
gi.require_version('Adw', '1')
from gi.repository import Adw

def check_adwaita_version():
    """Libadwaita sürümünü kontrol et."""
    print("=" * 70)
    print("🔍 Libadwaita Uyumluluk Kontrolü")
    print("=" * 70)
    print()
    
    try:
        # Adw.NavigationSplitView örneği oluştur ve metodlarını kontrol et
        split_view = Adw.NavigationSplitView()
        
        methods = {
            'set_sidebar': 'set_sidebar() mevcut ✅',
            'set_sidebar_child': 'set_sidebar_child() mevcut ⚠️ (deprecated)',
            'set_content': 'set_content() mevcut ⚠️ (deprecated)',
            'set_content_child': 'set_content_child() mevcut ✅',
        }
        
        print("📋 NavigationSplitView Metodları:")
        for method_name, label in methods.items():
            has_method = hasattr(split_view, method_name)
            status = "✅" if has_method else "❌"
            print(f"  {status} {label}")
        
        print()
        print("✅ Uyumluluğa göre önerilen yöntemler:")
        print("  • set_sidebar() ← Sidebar için (MODERN)")
        print("  • set_content_child() ← Content için (MODERN)")
        print()
        
        # Adw.Toast kontrol et
        print("📋 Adw.Toast Metodları:")
        toast = Adw.Toast()
        toast_methods = {
            'set_title': hasattr(toast, 'set_title'),
            'set_button_label': hasattr(toast, 'set_button_label'),
            'set_action_name': hasattr(toast, 'set_action_name'),
        }
        
        for method, has_it in toast_methods.items():
            status = "✅" if has_it else "❌"
            print(f"  {status} {method}")
        
        print()
        print("=" * 70)
        print("✅ Uyumluluk Kontrolü Tamamlandı!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_adwaita_version()
