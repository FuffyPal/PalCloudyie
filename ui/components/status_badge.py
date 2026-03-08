"""
PalCloudy - UI: Status Badge
Sunucu durumunu göstermek için renkli badge
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StatusType(Enum):
    """Status tipi enum'u"""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    LOADING = "loading"
    UNKNOWN = "unknown"


class StatusBadge(Gtk.Box):
    """
    Sunucu durumunu gösteren badge.
    
    Özellikleri:
    - Color-coded status (green, yellow, red, gray)
    - Icon support
    - Custom text
    - Animated loading state
    
    Örnek Kullanım:
        >>> badge = StatusBadge(status=StatusType.OK, text="Çalışıyor")
        >>> box.append(badge)
    """
    
    def __init__(self, status: StatusType = StatusType.UNKNOWN, text: str = "", **kwargs):
        """
        Status Badge'i oluştur.
        
        Args:
            status: Durum tipi
            text: Gösterilecek metin
            **kwargs: Ek parametreler
        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, **kwargs)
        
        self.status = status
        self.text = text
        
        self.set_spacing(6)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_start(8)
        self.set_margin_end(8)
        
        # Özel CSS sınıfı ekle
        self.add_css_class("status-badge")
        
        # Status icon
        self.icon = Gtk.Image()
        self.append(self.icon)
        
        # Status text
        self.label = Gtk.Label()
        self.label.set_text(text)
        self.append(self.label)
        
        # Durumu ayarla
        self.set_status(status, text)
        
        logger.info(f"✅ StatusBadge oluşturuldu: {status.value}")
    
    def set_status(self, status: StatusType, text: str = ""):
        """
        Durumu ayarla.
        
        Args:
            status: Yeni durum
            text: Gösterilecek metin
        """
        self.status = status
        if text:
            self.text = text
        
        self.label.set_text(self.text)
        
        # CSS class'ı güncelle
        self.remove_css_class("status-ok")
        self.remove_css_class("status-warning")
        self.remove_css_class("status-error")
        self.remove_css_class("status-maintenance")
        self.remove_css_class("status-loading")
        
        if status == StatusType.OK:
            self.add_css_class("status-ok")
            self.icon.set_from_icon_name("emblem-ok-symbolic")
            self.label.add_css_class("success")
        
        elif status == StatusType.WARNING:
            self.add_css_class("status-warning")
            self.icon.set_from_icon_name("dialog-warning-symbolic")
            self.label.add_css_class("warning")
        
        elif status == StatusType.ERROR:
            self.add_css_class("status-error")
            self.icon.set_from_icon_name("dialog-error-symbolic")
            self.label.add_css_class("error")
        
        elif status == StatusType.MAINTENANCE:
            self.add_css_class("status-maintenance")
            self.icon.set_from_icon_name("emblem-system-symbolic")
            self.label.add_css_class("maintenance")
        
        elif status == StatusType.LOADING:
            self.add_css_class("status-loading")
            self.icon.set_from_icon_name("emblem-synchronizing-symbolic")
            self.label.add_css_class("loading")
        
        else:  # UNKNOWN
            self.icon.set_from_icon_name("dialog-question-symbolic")
            self.label.add_css_class("dim-label")
        
        logger.debug(f"📊 Status güncellemeldi: {status.value}")
    
    def get_status(self) -> StatusType:
        """Mevcut durumu al"""
        return self.status


class HealthIndicator(Gtk.Box):
    """
    CPU, RAM, Disk sağlığını gösteren gösterge.
    
    Örnek Kullanım:
        >>> indicator = HealthIndicator()
        >>> indicator.set_cpu(45.5)
        >>> indicator.set_ram(75.3)
        >>> indicator.set_disk(60.1)
    """
    
    def __init__(self, **kwargs):
        """Health Indicator'ı başlat"""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, **kwargs)
        
        self.set_spacing(12)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        
        # CPU
        self.cpu_bar = self._create_progress_bar("CPU", "#FF9800")
        self.append(self.cpu_bar)
        
        # RAM
        self.ram_bar = self._create_progress_bar("RAM", "#2196F3")
        self.append(self.ram_bar)
        
        # Disk
        self.disk_bar = self._create_progress_bar("Disk", "#4CAF50")
        self.append(self.disk_bar)
        
        logger.info("✅ HealthIndicator başlatıldı")
    
    def _create_progress_bar(self, label: str, color: str) -> Gtk.Box:
        """Progress bar oluştur"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(4)
        
        # Label
        lbl = Gtk.Label()
        lbl.set_text(label)
        lbl.add_css_class("dim-label")
        box.append(lbl)
        
        # Progress bar
        progress = Gtk.ProgressBar()
        progress.set_show_text(True)
        progress.set_text("0%")
        progress.add_css_class("health-bar")
        box.append(progress)
        
        return box
    
    def set_cpu(self, percentage: float):
        """CPU yüzdesini ayarla"""
        bar = self.cpu_bar.get_first_child().get_next_sibling()
        bar.set_fraction(min(percentage / 100, 1.0))
        bar.set_text(f"{percentage:.0f}%")
    
    def set_ram(self, percentage: float):
        """RAM yüzdesini ayarla"""
        bar = self.ram_bar.get_first_child().get_next_sibling()
        bar.set_fraction(min(percentage / 100, 1.0))
        bar.set_text(f"{percentage:.0f}%")
    
    def set_disk(self, percentage: float):
        """Disk yüzdesini ayarla"""
        bar = self.disk_bar.get_first_child().get_next_sibling()
        bar.set_fraction(min(percentage / 100, 1.0))
        bar.set_text(f"{percentage:.0f}%")
    
    def set_all(self, cpu: float, ram: float, disk: float):
        """Tüm değerleri ayarla"""
        self.set_cpu(cpu)
        self.set_ram(ram)
        self.set_disk(disk)


class StatusBadgeCompact(Gtk.Label):
    """
    Kompakt status badge (sadece metin + renk).
    
    Örnek Kullanım:
        >>> badge = StatusBadgeCompact(StatusType.OK)
    """
    
    def __init__(self, status: StatusType = StatusType.UNKNOWN, **kwargs):
        """
        Kompakt badge'i oluştur.
        
        Args:
            status: Durum tipi
        """
        super().__init__(**kwargs)
        
        self.status = status
        self.set_status(status)
        
        self.add_css_class("badge")
        self.add_css_class("status-badge-compact")
    
    def set_status(self, status: StatusType):
        """Durumu ayarla"""
        self.status = status
        
        status_text = {
            StatusType.OK: "✅ OK",
            StatusType.WARNING: "⚠️ Uyarı",
            StatusType.ERROR: "❌ Hata",
            StatusType.MAINTENANCE: "🔧 Bakım",
            StatusType.LOADING: "⏳ Yükleniyor",
            StatusType.UNKNOWN: "❓ Bilinmiyor",
        }
        
        self.set_text(status_text.get(status, "Bilinmiyor"))
        self.add_css_class(f"status-{status.value}")


# CSS styling (kullanıcı tarafından aplikasyonda eklenecek)
STATUS_BADGE_CSS = b"""
.status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    background-color: @window_bg_color;
    border: 1px solid @borders;
}

.status-ok {
    background-color: #E8F5E9;
    color: #1B5E20;
}

.status-warning {
    background-color: #FFF3E0;
    color: #E65100;
}

.status-error {
    background-color: #FFEBEE;
    color: #B71C1C;
}

.status-maintenance {
    background-color: #F3E5F5;
    color: #4A148C;
}

.status-loading {
    background-color: #E3F2FD;
    color: #0D47A1;
}

.status-badge-compact {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
}

.health-bar {
    min-height: 8px;
}

.health-bar text {
    font-size: 0.8em;
}
"""
