"""
PalCloudy Application
Ana uygulama sınıfı ve lifecycle yönetimi
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from ui.window import PalCloudyWindow, PalCloudyApp
from ui.login_page import LoginPage
from core.auth_handler import get_auth_handler


class PalCloudyLoginApp(Adw.Application):
    """
    PalCloudy giriş uygulaması.
    İlk açılışta giriş sayfasını gösterir, ardından ana pencereye geçer.
    """
    
    def __init__(self, **kwargs):
        """Uygulamayı başlat."""
        super().__init__(**kwargs)
        
        # Uygulama ID
        self.set_application_id("io.github.palcloudy")
        
        # Sinyal bağlantıları
        self.connect("activate", self.on_activate)
        self.connect("startup", self.on_startup)
        
        # Kimlik doğrulama handler
        self.auth_handler = get_auth_handler()
        
        # Hesaplar ve pencere referansları
        self.main_window = None
        self.current_account = None
    
    def on_startup(self, app):
        """
        Uygulama başlangıcında çalışır.
        Kaynakları ve action'ları hazırla.
        """
        # Dark mode ayarını kontrol et
        style_manager = Adw.StyleManager.get_default()
        # system_default: system preferences'ı takip et
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
    
    def on_activate(self, app):
        """
        Uygulama etkinleştirildiğinde çalışır.
        Giriş yapılmış mı kontrol et, pencereyi göster.
        """
        
        window = self.get_active_window()
        
        if window is None:
            # Kaydedilmiş hesap var mı kontrol et
            accounts = self.auth_handler.list_credentials()
            
            if accounts:
                # Kaydedilmiş hesaplarla doğrudan dashboard'a git
                self._show_main_window(accounts[0]['id'])
            else:
                # Giriş sayfasını göster
                self._show_login_window()
        else:
            window.present()
    
    def _show_login_window(self):
        """Giriş penceresi göster."""
        
        window = Adw.ApplicationWindow(application=self)
        window.set_title("PalCloudy - Giriş Yap")
        window.set_default_size(550, 800)
        window.set_resizable(True)
        
        # Giriş sayfası
        login_page = LoginPage(on_login_success=self._on_login_success)
        window.set_content(login_page)
        
        window.present()
        
        self.login_window = window
    
    def _show_main_window(self, account_id: str = None):
        """Ana pencereyi göster."""
        
        # Giriş penceresini kapat
        if hasattr(self, 'login_window') and self.login_window:
            self.login_window.close()
        
        # Ana pencereyi oluştur
        self.main_window = PalCloudyWindow(self)
        self.main_window.present()
        
        # Hesap yükle
        if account_id:
            credential = self.auth_handler.get_credential(account_id)
            if credential:
                self.current_account = credential
                # TODO: İlgili sunucuları yükle ve dashboard'ı doldur
                print(f"✅ Hesap yüklendi: {credential['nickname']}")
    
    def _on_login_success(self):
        """Giriş başarılı olduğunda çalışır."""
        
        # En son kaydedilen hesapları al
        accounts = self.auth_handler.list_credentials()
        
        if accounts:
            # Son hesapla giriş yap
            self._show_main_window(accounts[-1]['id'])
        
        return False  # GLib callback'ten çık


def create_application() -> Adw.Application:
    """
    Uygulamayı oluştur ve döndür.
    
    Returns:
        Adw.Application: PalCloudy uygulaması
    """
    return PalCloudyLoginApp()


def run_application():
    """Uygulamayı çalıştır."""
    app = create_application()
    return app.run()


if __name__ == "__main__":
    import sys
    sys.exit(run_application())
