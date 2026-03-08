"""
PalCloudy - UI: Progress Bar
Task progress'i göstermek için animated progress bar
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
import logging

logger = logging.getLogger(__name__)


class TaskProgressBar(Gtk.Box):
    """
    Task progress'ini gösteren progress bar.
    
    Özellikleri:
    - Progress percentage (0-100)
    - Status message
    - Animated updates
    - Cancel button (optional)
    
    Örnek Kullanım:
        >>> progress = TaskProgressBar()
        >>> progress.start("Sunucu reboot ediliyor...")
        >>> progress.update(50, "50% tamamlandı")
        >>> progress.complete("Tamamlandı!")
    """
    
    def __init__(self, show_cancel_button: bool = True, **kwargs):
        """
        Progress Bar'ı oluştur.
        
        Args:
            show_cancel_button: Cancel butonu göster
            **kwargs: Ek parametreler
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.show_cancel = show_cancel_button
        self.current_progress = 0
        self.on_cancel_clicked = None
        
        self.set_spacing(8)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        # Başlık
        self.title_label = Gtk.Label()
        self.title_label.set_markup("<b>İşlem Devam Ediyor</b>")
        self.title_label.set_halign(Gtk.Align.START)
        self.append(self.title_label)
        
        # Progress bar
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.progressbar.set_text("0%")
        self.append(self.progressbar)
        
        # Status message
        self.status_label = Gtk.Label()
        self.status_label.set_text("Başlaniyor...")
        self.status_label.add_css_class("dim-label")
        self.status_label.set_wrap(True)
        self.append(self.status_label)
        
        # Butonlar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(6)
        button_box.set_halign(Gtk.Align.CENTER)
        
        if show_cancel_button:
            cancel_button = Gtk.Button()
            cancel_button.set_label("❌ İptal Et")
            cancel_button.connect("clicked", self._on_cancel_clicked)
            button_box.append(cancel_button)
        
        self.append(button_box)
        
        logger.info("✅ TaskProgressBar başlatıldı")
    
    def start(self, title: str = "İşlem Devam Ediyor", message: str = "Başlaniyor..."):
        """
        Progress'i başlat.
        
        Args:
            title: Başlık
            message: Başlangıç mesajı
        """
        self.title_label.set_markup(f"<b>{title}</b>")
        self.status_label.set_text(message)
        self.current_progress = 0
        self.progressbar.set_fraction(0)
        self.progressbar.set_text("0%")
        
        logger.info(f"▶️ Progress başladı: {title}")
    
    def update(self, percentage: float, message: str = ""):
        """
        Progress'i güncelle.
        
        Args:
            percentage: İlerleme yüzdesi (0-100)
            message: Durum mesajı
        """
        # Yüzdeyi sınırla
        percentage = min(100, max(0, percentage))
        self.current_progress = percentage
        
        # Progress bar'ı güncelle
        self.progressbar.set_fraction(percentage / 100)
        self.progressbar.set_text(f"{percentage:.0f}%")
        
        # Mesaj güncelle
        if message:
            self.status_label.set_text(message)
        
        logger.debug(f"📊 Progress: {percentage:.0f}% - {message}")
    
    def complete(self, title: str = "✅ Tamamlandı!", message: str = ""):
        """
        Progress'i tamamla.
        
        Args:
            title: Tamamlanma başlığı
            message: Tamamlanma mesajı
        """
        self.title_label.set_markup(f"<b>{title}</b>")
        self.current_progress = 100
        self.progressbar.set_fraction(1.0)
        self.progressbar.set_text("100%")
        
        if message:
            self.status_label.set_text(message)
        
        logger.info(f"✅ Progress tamamlandı: {title}")
    
    def fail(self, title: str = "❌ Hata!", message: str = ""):
        """
        Progress'i başarısız olarak işaretle.
        
        Args:
            title: Hata başlığı
            message: Hata mesajı
        """
        self.title_label.set_markup(f"<b>{title}</b>")
        self.title_label.add_css_class("error")
        
        if message:
            self.status_label.set_text(message)
        
        logger.error(f"❌ Progress başarısız: {title}")
    
    def _on_cancel_clicked(self, button):
        """İptal butonuna tıklandı"""
        logger.info("⛔ Progress iptal edildi")
        if self.on_cancel_clicked:
            self.on_cancel_clicked()


class AnimatedProgressBar(Gtk.ProgressBar):
    """
    Animated progress bar (otomatik animasyon).
    
    Örnek Kullanım:
        >>> bar = AnimatedProgressBar()
        >>> bar.pulse()  # Animasyonu başlat
    """
    
    def __init__(self, **kwargs):
        """Animated progress bar'ı oluştur"""
        super().__init__(**kwargs)
        
        self.set_show_text(True)
        self.set_text("Yükleniyor...")
        
        # Pulse animation için GLib timeout
        self.pulse_handler_id = None
    
    def pulse(self):
        """Animasyonu başlat"""
        if self.pulse_handler_id is None:
            self.pulse_handler_id = GLib.timeout_add(50, self._do_pulse)
            logger.info("▶️ Progress animation başladı")
    
    def _do_pulse(self) -> bool:
        """Pulse action"""
        self.pulse()
        return True
    
    def stop_pulse(self):
        """Animasyonu durdur"""
        if self.pulse_handler_id is not None:
            GLib.source_remove(self.pulse_handler_id)
            self.pulse_handler_id = None
            logger.info("⏹️ Progress animation durduruldu")


class DeterminateProgressBar(Gtk.Box):
    """
    Determine (belirli) progress bar.
    
    Örnek Kullanım:
        >>> bar = DeterminateProgressBar()
        >>> bar.set_progress(50)  # %50
    """
    
    def __init__(self, **kwargs):
        """Determine progress bar'ı oluştur"""
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.set_spacing(4)
        
        # Label
        self.label = Gtk.Label()
        self.label.set_text("0%")
        self.append(self.label)
        
        # Progress bar
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(False)
        self.append(self.progressbar)
    
    def set_progress(self, percentage: float):
        """
        Progress'i ayarla.
        
        Args:
            percentage: İlerleme yüzdesi (0-100)
        """
        percentage = min(100, max(0, percentage))
        
        self.progressbar.set_fraction(percentage / 100)
        self.label.set_text(f"{percentage:.0f}%")


# Örnek animasyon kodu (reference)
ANIMATION_EXAMPLE = """
# GLib timer ile manuel animation
def animate_progress(bar, duration_ms):
    start_time = time.time()
    
    def update():
        elapsed = (time.time() - start_time) * 1000
        progress = min(100, (elapsed / duration_ms) * 100)
        bar.update(progress, f"{progress:.0f}% tamamlandı")
        
        return progress < 100  # Devam et if < 100
    
    GLib.timeout_add(100, update)
"""
