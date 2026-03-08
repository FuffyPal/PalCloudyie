"""
PalCloudy Login Page
Libadwaita (Adw) tabanlı giriş sayfası ve API anahtarı girişi
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from config.endpoints import list_all_endpoints
from core.auth_handler import get_auth_handler
from core.factory import create_client
from api.test_connection import test_connection


class LoginPage(Adw.Bin):
    """
    API anahtarları giriş sayfası.
    Endpoint seçimi, anahtar girişi ve validasyon.
    """
    
    def __init__(self, on_login_success=None, **kwargs):
        """
        Giriş sayfasını başlat.
        
        Args:
            on_login_success: Giriş başarılı olunca çalışacak callback
            **kwargs: Ek parametreler
        """
        super().__init__(**kwargs)
        
        self.on_login_success = on_login_success
        self.auth_handler = get_auth_handler()
        
        # Kayıtlı hesapları yükle
        self.accounts = self.auth_handler.list_credentials()
        
        # Sayfayı oluştur
        self._build_ui()
    
    def _build_ui(self):
        """Ana UI'ı inşa et."""
        
        # Ana container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(24)
        main_box.set_margin_top(40)
        main_box.set_margin_bottom(40)
        main_box.set_margin_start(40)
        main_box.set_margin_end(40)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.START)
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_box.set_spacing(8)
        header_box.set_halign(Gtk.Align.CENTER)
        
        logo = Gtk.Label()
        logo.set_markup("<span size='48000'><b>☁️</b></span>")
        header_box.append(logo)
        
        title = Gtk.Label()
        title.set_markup("<b>PalCloudy</b>")
        title.add_css_class("title")
        header_box.append(title)
        
        subtitle = Gtk.Label()
        subtitle.set_text("OVH API Anahtarlarını Gir")
        subtitle.add_css_class("subtitle")
        subtitle.add_css_class("dim-label")
        header_box.append(subtitle)
        
        main_box.append(header_box)
        
        # Form container (max-width)
        form_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        form_container.set_spacing(18)
        form_container.set_size_request(450, -1)
        form_container.set_halign(Gtk.Align.CENTER)
        
        # Tabs: Yeni Giriş vs Kaydedilmiş
        self.tab_switcher = Adw.ViewSwitcher()
        self.tab_stack = Adw.ViewStack()  # Gtk.Stack yerine Adw.ViewStack
        
        # Tab 1: Yeni Giriş
        new_login_box = self._build_new_login_tab()
        self.tab_stack.add_titled(new_login_box, "new", "🆕 Yeni Giriş")
        
        # Tab 2: Kaydedilmiş Hesaplar
        if self.accounts:
            saved_login_box = self._build_saved_accounts_tab()
            self.tab_stack.add_titled(saved_login_box, "saved", "💾 Kaydedilmiş")
        
        self.tab_switcher.set_stack(self.tab_stack)
        form_container.append(self.tab_switcher)
        form_container.append(self.tab_stack)
        
        main_box.append(form_container)
        
        # Lisans/bilgi notu
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>API anahtarlarınız şifreli şekilde yerel depolanır.\n"
            "Herhangi bir uzak sunucuya gönderilmez.</small>"
        )
        info_label.add_css_class("dim-label")
        info_label.set_justify(Gtk.Justification.CENTER)
        main_box.append(info_label)
        
        self.set_child(main_box)
    
    def _build_new_login_tab(self) -> Gtk.Widget:
        """Yeni giriş sekmesini inşa et."""
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        # Endpoint seçimi
        endpoint_label = Gtk.Label()
        endpoint_label.set_markup("<b>1. Endpoint Seç</b>")
        endpoint_label.set_halign(Gtk.Align.START)
        box.append(endpoint_label)
        
        self.endpoint_combo = Gtk.ComboBoxText()
        self.endpoint_combo.set_halign(Gtk.Align.FILL)
        self.endpoint_combo.set_entry_text_column(0)
        
        # Endpoint'leri categorize ile ekle
        endpoints = list_all_endpoints()
        self.endpoint_map = {}
        
        idx = 0
        for group, group_endpoints in endpoints.items():
            for endpoint_id, endpoint_info in group_endpoints.items():
                label = f"{group} - {endpoint_info['name']}"
                self.endpoint_combo.append(endpoint_id, label)
                self.endpoint_map[endpoint_id] = endpoint_info['name']
                if idx == 0:
                    self.endpoint_combo.set_active(0)
                idx += 1
        
        box.append(self.endpoint_combo)
        
        # Takma ad (nickname)
        nickname_label = Gtk.Label()
        nickname_label.set_markup("<b>2. Hesap Adı</b>")
        nickname_label.set_halign(Gtk.Align.START)
        box.append(nickname_label)
        
        self.nickname_entry = Gtk.Entry()
        self.nickname_entry.set_placeholder_text("Ör: My OVH Account")
        self.nickname_entry.set_halign(Gtk.Align.FILL)
        box.append(self.nickname_entry)
        
        # API Anahtarları
        keys_label = Gtk.Label()
        keys_label.set_markup("<b>3. API Anahtarlarını Gir</b>")
        keys_label.set_halign(Gtk.Align.START)
        box.append(keys_label)
        
        # App Key
        self.app_key_entry = Gtk.Entry()
        self.app_key_entry.set_placeholder_text("Application Key")
        self.app_key_entry.set_halign(Gtk.Align.FILL)
        self.app_key_entry.set_visibility(False)  # Gizli metin
        box.append(self.app_key_entry)
        
        # App Secret
        self.app_secret_entry = Gtk.Entry()
        self.app_secret_entry.set_placeholder_text("Application Secret")
        self.app_secret_entry.set_halign(Gtk.Align.FILL)
        self.app_secret_entry.set_visibility(False)
        box.append(self.app_secret_entry)
        
        # Consumer Key
        self.consumer_key_entry = Gtk.Entry()
        self.consumer_key_entry.set_placeholder_text("Consumer Key")
        self.consumer_key_entry.set_halign(Gtk.Align.FILL)
        self.consumer_key_entry.set_visibility(False)
        box.append(self.consumer_key_entry)
        
        # Yardım linki
        help_button = Gtk.LinkButton(
            uri="https://help.ovhcloud.com/csm/en-managing-tokens-and-permissions?id=kb_article_view&sysparm_article=KB0042854",
            label="🔗 API Anahtarlarını Nasıl Elde Ederim?"
        )
        box.append(help_button)
        
        # Butonlar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(6)
        button_box.set_halign(Gtk.Align.END)
        
        test_button = Gtk.Button()
        test_button.set_label("🔍 Bağlantıyı Test Et")
        test_button.connect("clicked", self.on_test_connection)
        button_box.append(test_button)
        
        login_button = Gtk.Button()
        login_button.set_label("✅ Giriş Yap")
        login_button.add_css_class("suggested-action")
        login_button.connect("clicked", self.on_login_clicked)
        self.login_button = login_button
        button_box.append(login_button)
        
        box.append(button_box)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_wrap(True)
        self.status_label.set_halign(Gtk.Align.CENTER)
        box.append(self.status_label)
        
        return box
    
    def _build_saved_accounts_tab(self) -> Gtk.Widget:
        """Kaydedilmiş hesaplar sekmesini inşa et."""
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        label = Gtk.Label()
        label.set_markup("<b>Kaydedilmiş Hesaplar</b>")
        label.set_halign(Gtk.Align.START)
        box.append(label)
        
        # Hesap listesi
        accounts_list = Gtk.ListBox()
        accounts_list.set_selection_mode(Gtk.SelectionMode.NONE)
        accounts_list.add_css_class("boxed-list")
        
        for account in self.accounts:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            row.set_spacing(12)
            row.set_margin_top(8)
            row.set_margin_bottom(8)
            row.set_margin_start(12)
            row.set_margin_end(12)
            
            # Hesap bilgisi
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            info_box.set_spacing(4)
            
            name = Gtk.Label()
            name.set_markup(f"<b>{account['nickname']}</b>")
            name.set_halign(Gtk.Align.START)
            info_box.append(name)
            
            endpoint = Gtk.Label()
            endpoint.set_text(f"Endpoint: {account['endpoint']}")
            endpoint.add_css_class("dim-label")
            endpoint.set_halign(Gtk.Align.START)
            info_box.append(endpoint)
            
            row.append(info_box)
            row.set_hexpand(True)
            
            # Düğmeler
            use_button = Gtk.Button()
            use_button.set_label("Kullan")
            use_button.connect(
                "clicked",
                self.on_use_saved_account,
                account['id']
            )
            row.append(use_button)
            
            delete_button = Gtk.Button()
            delete_button.set_label("🗑️")
            delete_button.connect(
                "clicked",
                self.on_delete_account,
                account['id']
            )
            row.append(delete_button)
            
            accounts_list.append(row)
        
        box.append(accounts_list)
        
        return box
    
    def on_test_connection(self, button):
        """Bağlantı testini çalıştır."""
        
        # Inputları al
        endpoint = self.endpoint_combo.get_active_id()
        app_key = self.app_key_entry.get_text()
        app_secret = self.app_secret_entry.get_text()
        consumer_key = self.consumer_key_entry.get_text()
        
        # Validasyon
        if not all([endpoint, app_key, app_secret, consumer_key]):
            self._set_status("❌ Tüm alanları doldurun!", "error")
            return
        
        # UI'ı disable et
        self.login_button.set_sensitive(False)
        self.status_label.set_text("🔄 Test yapılıyor...")
        
        # Test başlatıldı
        def run_test():
            client = create_client(endpoint, app_key, app_secret, consumer_key)
            success, message = test_connection(client)
            
            GLib.idle_add(lambda: self._on_test_complete(success, message))
        
        # Background thread'de çalıştır (UI donmasını önlemek için)
        import threading
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def _on_test_complete(self, success, message):
        """Test tamamlandığında çalışır."""
        self.login_button.set_sensitive(True)
        
        if success:
            self._set_status(message, "success")
        else:
            self._set_status(message, "error")
    
    def on_login_clicked(self, button):
        """Giriş yap butonuna tıklandı."""
        
        # Inputları al
        endpoint = self.endpoint_combo.get_active_id()
        app_key = self.app_key_entry.get_text()
        app_secret = self.app_secret_entry.get_text()
        consumer_key = self.consumer_key_entry.get_text()
        nickname = self.nickname_entry.get_text()
        
        # Validasyon
        if not all([endpoint, app_key, app_secret, consumer_key]):
            self._set_status("❌ Tüm alanları doldurun!", "error")
            return
        
        if not self.auth_handler.validate_credentials(app_key, app_secret, consumer_key):
            self._set_status("❌ API anahtarları geçersiz format!", "error")
            return
        
        # Credential'ı kaydet
        success = self.auth_handler.save_credentials(
            endpoint=endpoint,
            app_key=app_key,
            app_secret=app_secret,
            consumer_key=consumer_key,
            nickname=nickname or f"Account-{endpoint}"
        )
        
        if success:
            self._set_status("✅ Giriş başarılı! Yönlendiriliyorsunuz...", "success")
            
            # Callback çalıştır
            if self.on_login_success:
                GLib.timeout_add(500, self.on_login_success)
        else:
            self._set_status("❌ Kaydetme sırasında hata!", "error")
    
    def on_use_saved_account(self, button, account_id):
        """Kaydedilmiş hesapla giriş yap."""
        
        if self.on_login_success:
            self.on_login_success()
    
    def on_delete_account(self, button, account_id):
        """Hesapı sil."""
        
        self.auth_handler.delete_credential(account_id)
        
        # Sayfayı yenile
        self._build_ui()
        
        toast = Adw.Toast()
        toast.set_title("✅ Hesap silindi")
        self.get_root().add_toast(toast)
    
    def _set_status(self, text: str, status_type: str = "info"):
        """Status mesajını göster."""
        
        self.status_label.set_text(text)
        
        # CSS class'ını ayarla
        self.status_label.remove_css_class("success")
        self.status_label.remove_css_class("error")
        self.status_label.remove_css_class("info")
        
        if status_type == "success":
            self.status_label.add_css_class("success")
        elif status_type == "error":
            self.status_label.add_css_class("error")
        else:
            self.status_label.add_css_class("info")


def create_login_window(on_success=None):
    """
    Standalone giriş penceresi oluştur.
    
    Args:
        on_success: Giriş başarılı olunca çalışacak callback
    
    Returns:
        Adw.ApplicationWindow: Giriş penceresi
    """
    
    app = Adw.Application()
    window = Adw.ApplicationWindow(application=app)
    window.set_title("PalCloudy - Giriş Yap")
    window.set_default_size(550, 800)
    
    login_page = LoginPage(on_login_success=on_success)
    window.set_content(login_page)
    
    return app, window
