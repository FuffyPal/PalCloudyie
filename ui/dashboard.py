"""
PalCloudy Dashboard Page
Kaydedilmiş hesaplar ve sunucu yönetimi
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from core.auth_handler import get_auth_handler


class DashboardPage(Adw.Bin):
    """
    Ana dashboard sayfası.
    Hesap listesi ve server management.
    """
    
    def __init__(self, on_account_selected=None, **kwargs):
        """
        Dashboard'ı başlat.
        
        Args:
            on_account_selected: Hesap seçilince çalışacak callback
        """
        super().__init__(**kwargs)
        
        self.on_account_selected = on_account_selected
        self.auth_handler = get_auth_handler()
        
        # Sayfayı oluştur
        self._build_ui()
    
    def _build_ui(self):
        """Ana UI'ı inşa et."""
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        
        # Header
        header_label = Gtk.Label()
        header_label.set_markup("<b>Kaydedilmiş Hesaplar</b>")
        header_label.set_halign(Gtk.Align.START)
        main_box.append(header_label)
        
        # Accounts listbox
        accounts_list = Gtk.ListBox()
        accounts_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        accounts_list.add_css_class("boxed-list")
        
        # Kaydedilmiş hesapları al
        accounts = self.auth_handler.list_credentials()
        
        if not accounts:
            # Empty state
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            empty_box.set_spacing(12)
            empty_box.set_halign(Gtk.Align.CENTER)
            empty_box.set_valign(Gtk.Align.CENTER)
            empty_box.set_margin_top(40)
            empty_box.set_margin_bottom(40)
            
            icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
            icon.set_pixel_size(64)
            empty_box.append(icon)
            
            empty_label = Gtk.Label()
            empty_label.set_markup("<b>Hesap Bulunamadı</b>\n<small>Yeni hesap eklemek için + Hesap Ekle'ye tıklayın</small>")
            empty_label.set_justify(Gtk.Justification.CENTER)
            empty_box.append(empty_label)
            
            main_box.append(empty_box)
        else:
            # Hesapları listele
            for account in accounts:
                row = self._create_account_row(account)
                accounts_list.append(row)
            
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_child(accounts_list)
            scrolled.set_vexpand(True)
            main_box.append(scrolled)
        
        self.set_child(main_box)
    
    def _create_account_row(self, account):
        """Hesap satırı oluştur."""
        
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.set_spacing(12)
        row.set_margin_top(12)
        row.set_margin_bottom(12)
        row.set_margin_start(12)
        row.set_margin_end(12)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("user-properties-symbolic")
        icon.set_pixel_size(32)
        row.append(icon)
        
        # Account info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_box.set_spacing(4)
        
        nickname = Gtk.Label()
        nickname.set_markup(f"<b>{account['nickname']}</b>")
        nickname.set_halign(Gtk.Align.START)
        info_box.append(nickname)
        
        endpoint = Gtk.Label()
        endpoint.set_markup(f"<small>Endpoint: {account['endpoint']}</small>")
        endpoint.add_css_class("dim-label")
        endpoint.set_halign(Gtk.Align.START)
        info_box.append(endpoint)
        
        row.append(info_box)
        row.set_hexpand(True)
        
        # Action buttons
        switch_button = Gtk.Button()
        switch_button.set_label("Geç")
        switch_button.connect("clicked", self.on_switch_account, account['id'])
        row.append(switch_button)
        
        delete_button = Gtk.Button()
        delete_button.set_label("🗑️")
        delete_button.connect("clicked", self.on_delete_account, account['id'])
        row.append(delete_button)
        
        return row
    
    def on_switch_account(self, button, account_id):
        """Farklı hesaba geç."""
        print(f"💫 Hesap değiştiriliyor: {account_id}")
        if self.on_account_selected:
            self.on_account_selected(account_id)
    
    def on_delete_account(self, button, account_id):
        """Hesabı sil."""
        print(f"🗑️  Hesap siliniyor: {account_id}")
        self.auth_handler.delete_credential(account_id)
        
        # Sayfayı yenile
        self._build_ui()
        
        print(f"✅ Hesap silindi: {account_id}")
