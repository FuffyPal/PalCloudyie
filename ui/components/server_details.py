"""
PalCloudy - UI: Server Details Panel
Seçilen sunucunun detaylı bilgilerini göster
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from typing import Dict, Any, Optional, Callable
from ui.components.status_badge import StatusBadge, StatusType, HealthIndicator
import logging

logger = logging.getLogger(__name__)


class ServerDetailsPanel(Gtk.Box):
    """
    Seçilen sunucunun detaylı bilgilerini göster.
    
    Özellikleri:
    - Server info, network settings, storage info
    - Status badge
    - Health indicators (CPU, RAM, Disk)
    - Action buttons (Reboot, Reinstall, Power)
    
    Örnek Kullanım:
        >>> panel = ServerDetailsPanel(on_reboot=self.on_reboot)
        >>> panel.load_server(server_data)
        >>> window.add_child(panel)
    """
    
    def __init__(self, 
                 on_reboot: Optional[Callable] = None,
                 on_reinstall: Optional[Callable] = None,
                 on_power: Optional[Callable] = None,
                 **kwargs):
        """
        Server Details Panel'ı oluştur.
        
        Args:
            on_reboot: Reboot butonuna tıklandığında
            on_reinstall: Reinstall butonuna tıklandığında
            on_power: Power butonuna tıklandığında
            **kwargs: Ek parametreler
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.on_reboot = on_reboot
        self.on_reinstall = on_reinstall
        self.on_power = on_power
        self.current_server = None
        
        self.set_spacing(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        # ScrolledWindow (içerik uzun olabilir)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # İçerik box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_spacing(12)
        
        # Header
        self._build_header(content_box)
        
        # Detaylar
        self._build_details(content_box)
        
        # Health Indicators
        self._build_health(content_box)
        
        # Action buttons
        self._build_actions(content_box)
        
        # Placeholder (sunucu seçilmediğinde)
        self.placeholder = self._build_placeholder()
        
        scrolled.set_child(content_box)
        self.append(scrolled)
        
        # İlk başta placeholder göster
        self.show_placeholder()
        
        logger.info("✅ ServerDetailsPanel başlatıldı")
    
    def _build_header(self, parent: Gtk.Box):
        """Başlık bölümü oluştur"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_box.set_spacing(8)
        
        # Server adı
        self.name_label = Gtk.Label()
        self.name_label.set_markup("<b>Sunucu Seçilmedi</b>")
        self.name_label.set_selectable(True)
        header_box.append(self.name_label)
        
        # Status badge
        self.status_badge = StatusBadge(StatusType.UNKNOWN, "Bilinmiyor")
        header_box.append(self.status_badge)
        
        parent.append(header_box)
    
    def _build_details(self, parent: Gtk.Box):
        """Detaylar bölümü oluştur"""
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        details_box.set_spacing(6)
        
        # Başlık
        title = Gtk.Label()
        title.set_markup("<b>📋 Sunucu Bilgileri</b>")
        title.set_halign(Gtk.Align.START)
        details_box.append(title)
        
        # Info grid
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)
        
        # Labels
        self.ip_label = self._create_info_row(grid, 0, "IP Adresi:", "N/A")
        self.os_label = self._create_info_row(grid, 1, "İşletim Sistemi:", "N/A")
        self.dc_label = self._create_info_row(grid, 2, "Veri Merkezi:", "N/A")
        self.cpu_label = self._create_info_row(grid, 3, "İşlemci:", "N/A")
        
        details_box.append(grid)
        parent.append(details_box)
    
    def _build_health(self, parent: Gtk.Box):
        """Health indicators oluştur"""
        health_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        health_box.set_spacing(8)
        
        # Başlık
        title = Gtk.Label()
        title.set_markup("<b>📊 Sistem Sağlığı</b>")
        title.set_halign(Gtk.Align.START)
        health_box.append(title)
        
        # Health indicator
        self.health_indicator = HealthIndicator()
        health_box.append(self.health_indicator)
        
        parent.append(health_box)
    
    def _build_actions(self, parent: Gtk.Box):
        """Action buttons oluştur"""
        actions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        actions_box.set_spacing(8)
        
        # Başlık
        title = Gtk.Label()
        title.set_markup("<b>⚙️ İşlemler</b>")
        title.set_halign(Gtk.Align.START)
        actions_box.append(title)
        
        # Button grid
        button_grid = Gtk.Grid()
        button_grid.set_row_spacing(6)
        button_grid.set_column_spacing(6)
        button_grid.set_column_homogeneous(True)
        
        # Reboot button
        self.reboot_btn = Gtk.Button()
        self.reboot_btn.set_label("🔄 Reboot")
        self.reboot_btn.connect("clicked", lambda x: self._on_reboot_clicked())
        button_grid.attach(self.reboot_btn, 0, 0, 1, 1)
        
        # Reinstall button
        self.reinstall_btn = Gtk.Button()
        self.reinstall_btn.set_label("💾 Kurulumu Yenile")
        self.reinstall_btn.connect("clicked", lambda x: self._on_reinstall_clicked())
        button_grid.attach(self.reinstall_btn, 1, 0, 1, 1)
        
        # Power button
        self.power_btn = Gtk.Button()
        self.power_btn.set_label("⚡ Güç Kontrol")
        self.power_btn.connect("clicked", lambda x: self._on_power_clicked())
        button_grid.attach(self.power_btn, 0, 1, 1, 1)
        
        actions_box.append(button_grid)
        parent.append(actions_box)
    
    def _build_placeholder(self) -> Gtk.Box:
        """Placeholder oluştur"""
        placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        placeholder.set_spacing(12)
        placeholder.set_halign(Gtk.Align.CENTER)
        placeholder.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
        icon.set_pixel_size(96)
        placeholder.append(icon)
        
        # Metin
        label = Gtk.Label()
        label.set_markup(
            "<b>Sunucu Seçin</b>\n"
            "Sol tarafdan bir sunucu seçerek detaylarını görüntüleyebilirsiniz"
        )
        label.set_justify(Gtk.Justification.CENTER)
        placeholder.append(label)
        
        return placeholder
    
    def _create_info_row(self, grid: Gtk.Grid, row: int, label_text: str, value_text: str) -> Gtk.Label:
        """Info satırı oluştur"""
        # Label
        label = Gtk.Label()
        label.set_markup(f"<b>{label_text}</b>")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, row, 1, 1)
        
        # Value
        value = Gtk.Label()
        value.set_text(value_text)
        value.set_selectable(True)
        grid.attach(value, 1, row, 1, 1)
        
        return value
    
    def load_server(self, server: Dict[str, Any]):
        """
        Sunucu bilgilerini yükle.
        
        Args:
            server: Sunucu veri sözlüğü
            {
                'name': 'ns123456.ip-1-2-3.eu',
                'ip': '1.2.3.4',
                'state': 'ok',
                'os': 'Debian 11',
                'datacenter': 'sbg',
                'cpu': 45.5,
                'ram': 75.3,
                'disk': 60.1,
            }
        """
        self.current_server = server
        
        # Başlık
        self.name_label.set_markup(f"<b>{server.get('name', 'Unknown')}</b>")
        
        # Status
        state = server.get('state', 'unknown')
        status_map = {
            'ok': (StatusType.OK, "✅ Çalışıyor"),
            'maintenance': (StatusType.MAINTENANCE, "🔧 Bakım"),
            'error': (StatusType.ERROR, "❌ Hata"),
        }
        status_type, status_text = status_map.get(state, (StatusType.UNKNOWN, "❓ Bilinmiyor"))
        self.status_badge.set_status(status_type, status_text)
        
        # Detaylar
        self.ip_label.set_text(server.get('ip', 'N/A'))
        self.os_label.set_text(server.get('os', 'N/A'))
        self.dc_label.set_text(server.get('datacenter', 'N/A'))
        cpu_text = server.get('cpu', 'N/A')
        self.cpu_label.set_text(f"{cpu_text}" if isinstance(cpu_text, str) else f"{cpu_text} cores")
        
        # Health
        self.health_indicator.set_all(
            server.get('cpu_usage', 0),
            server.get('ram_usage', 0),
            server.get('disk_usage', 0),
        )
        
        logger.info(f"📋 Sunucu yüklendi: {server.get('name', 'Unknown')}")
    
    def show_placeholder(self):
        """Placeholder göster"""
        # Butonları deactivate et
        for btn in [self.reboot_btn, self.reinstall_btn, self.power_btn]:
            btn.set_sensitive(False)
        
        logger.debug("📭 Placeholder gösterildi")
    
    def _on_reboot_clicked(self):
        """Reboot butonuna tıklandı"""
        if self.current_server and self.on_reboot:
            logger.info(f"🔄 Reboot istendi: {self.current_server['name']}")
            self.on_reboot(self.current_server)
    
    def _on_reinstall_clicked(self):
        """Reinstall butonuna tıklandı"""
        if self.current_server and self.on_reinstall:
            logger.info(f"💾 Reinstall istendi: {self.current_server['name']}")
            self.on_reinstall(self.current_server)
    
    def _on_power_clicked(self):
        """Power butonuna tıklandı"""
        if self.current_server and self.on_power:
            logger.info(f"⚡ Power kontrol istendi: {self.current_server['name']}")
            self.on_power(self.current_server)


# Örnek veri
EXAMPLE_SERVER = {
    'name': 'ns123456.ip-1-2-3.eu',
    'ip': '1.2.3.4',
    'state': 'ok',
    'os': 'Debian 11 (64)',
    'datacenter': 'sbg',
    'cpu': 'Intel Xeon E5-2650 v3',
    'cpu_usage': 45.5,
    'ram_usage': 75.3,
    'disk_usage': 60.1,
}
