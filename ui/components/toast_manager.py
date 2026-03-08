"""
PalCloudy - UI: Toast Manager (FIXED)
Bildirim (toast) göstermek için manager
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import logging
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

from gi.repository import Adw, GLib, Gtk

logger = logging.getLogger(__name__)


class ToastType(Enum):
    """Toast bildirimi tipi"""

    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class Toast:
    """Tek bir toast bildirimi"""

    def __init__(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration_ms: int = 3000,
    ):
        """
        Toast'ı oluştur.

        Args:
            message: Gösterilecek mesaj
            toast_type: Bildirim tipi
            duration_ms: Gösterilme süresi (milisaniye)
        """
        self.message = message
        self.toast_type = toast_type
        self.duration_ms = duration_ms
        self.created_at = datetime.now()
        self.dismissed = False

    def __repr__(self) -> str:
        return f"Toast({self.toast_type.value}, {self.message[:30]}...)"


class ToastManager:
    """
    Toast bildirimlerini yönet.

    Özellikleri:
    - Success, Error, Info, Warning tipi
    - Auto-dismiss (belirtilen süre sonra kapan)
    - Custom duration
    - Stack management

    Örnek Kullanım:
        >>> manager = ToastManager(parent_window)
        >>> manager.show_success("Sunucu reboot edildi")
        >>> manager.show_error("Bağlantı başarısız", duration_ms=5000)
        >>> manager.show_info("Sistem güncelleniyor...")
    """

    def __init__(self, parent_window: Optional[Adw.ApplicationWindow] = None):
        """
        Toast Manager'ı oluştur.

        Args:
            parent_window: Ana pencere (isteğe bağlı)
        """
        self.parent_window = parent_window
        self.toasts = []
        self._apply_css()

        logger.info("✅ ToastManager başlatıldı")

    def show(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration_ms: int = 3000,
        on_dismissed: Optional[Callable] = None,
    ) -> Toast:
        """
        Toast bildirimini göster.

        Args:
            message: Gösterilecek mesaj
            toast_type: Bildirim tipi
            duration_ms: Gösterilme süresi
            on_dismissed: Bildirim kapanırken çağrılacak callback

        Returns:
            Toast nesnesi
        """
        toast = Toast(message, toast_type, duration_ms)
        self.toasts.append(toast)

        logger.info(f"📢 Toast gösterildi: [{toast_type.value}] {message}")

        # Ana pencerey var ise Adw.Toast kullan
        if self.parent_window:
            self._show_adw_toast(message, toast_type, duration_ms)

        # Auto-dismiss timer
        if duration_ms > 0:
            GLib.timeout_add(
                duration_ms, lambda: self._dismiss_toast(toast, on_dismissed)
            )

        return toast

    def show_success(
        self,
        message: str,
        duration_ms: int = 3000,
        on_dismissed: Optional[Callable] = None,
    ) -> Toast:
        """
        Başarı bildirimini göster.

        Args:
            message: Mesaj
            duration_ms: Süre
            on_dismissed: Callback

        Returns:
            Toast nesnesi
        """
        return self.show(message, ToastType.SUCCESS, duration_ms, on_dismissed)

    def show_error(
        self,
        message: str,
        duration_ms: int = 5000,
        on_dismissed: Optional[Callable] = None,
    ) -> Toast:
        """
        Hata bildirimini göster.

        Args:
            message: Mesaj
            duration_ms: Süre (hata için daha uzun)
            on_dismissed: Callback

        Returns:
            Toast nesnesi
        """
        return self.show(message, ToastType.ERROR, duration_ms, on_dismissed)

    def show_info(
        self,
        message: str,
        duration_ms: int = 3000,
        on_dismissed: Optional[Callable] = None,
    ) -> Toast:
        """
        Bilgi bildirimini göster.

        Args:
            message: Mesaj
            duration_ms: Süre
            on_dismissed: Callback

        Returns:
            Toast nesnesi
        """
        return self.show(message, ToastType.INFO, duration_ms, on_dismissed)

    def show_warning(
        self,
        message: str,
        duration_ms: int = 4000,
        on_dismissed: Optional[Callable] = None,
    ) -> Toast:
        """
        Uyarı bildirimini göster.

        Args:
            message: Mesaj
            duration_ms: Süre
            on_dismissed: Callback

        Returns:
            Toast nesnesi
        """
        return self.show(message, ToastType.WARNING, duration_ms, on_dismissed)

    def _dismiss_toast(
        self, toast: Toast, on_dismissed: Optional[Callable] = None
    ) -> bool:
        """
        Toast'ı kapat.

        Args:
            toast: Kapanacak toast
            on_dismissed: Callback

        Returns:
            False (timer'ı kaldır)
        """
        toast.dismissed = True
        if toast in self.toasts:
            self.toasts.remove(toast)

        logger.debug(f"🗑️ Toast kapatıldı: {toast}")

        if on_dismissed:
            on_dismissed()

        return False  # Timer'ı kaldır

    def _show_adw_toast(self, message: str, toast_type: ToastType, duration_ms: int):
        """
        Adw.Toast kullanarak göster (Libadwaita).

        Args:
            message: Mesaj
            toast_type: Tip
            duration_ms: Süre
        """
        if not self.parent_window:
            return

        # Adw.ToastOverlay var ise kullan
        if hasattr(self.parent_window, "add_toast"):
            toast = Adw.Toast()
            toast.set_title(message)

            # Tipi göster emoji ile
            emoji_map = {
                ToastType.SUCCESS: "✅",
                ToastType.ERROR: "❌",
                ToastType.INFO: "ℹ️",
                ToastType.WARNING: "⚠️",
            }
            emoji = emoji_map.get(toast_type, "")
            toast.set_title(f"{emoji} {message}")

            self.parent_window.add_toast(toast)

    def _apply_css(self):
        """Toast CSS styling ekle - FIXED VERSION"""
        try:
            css_provider = Gtk.CssProvider()
            css_data = b"""
                .toast-success {
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 4px;
                    margin: 8px;
                }

                .toast-error {
                    background-color: #F44336;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 4px;
                    margin: 8px;
                }

                .toast-info {
                    background-color: #2196F3;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 4px;
                    margin: 8px;
                }

                .toast-warning {
                    background-color: #FFC107;
                    color: black;
                    padding: 12px 16px;
                    border-radius: 4px;
                    margin: 8px;
                }
            """
            css_provider.load_from_data(css_data)

            # GUI context varsa CSS ekle (FIXED: DisplayManager.get().get_default_display())
            display = Gtk.DisplayManager.get().get_default_display()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
        except Exception as e:
            logger.warning(f"⚠️  CSS yüklenemedi: {e}")

    def clear_all(self):
        """Tüm toast'ları kapat"""
        for toast in self.toasts[:]:
            self._dismiss_toast(toast)

        logger.info(f"🗑️  Tüm toast'lar kapatıldı")

    def get_active_toasts(self) -> list:
        """Aktif toast'ları al"""
        return [t for t in self.toasts if not t.dismissed]


# Singleton instance
_toast_manager: Optional[ToastManager] = None


def get_toast_manager(
    parent_window: Optional[Adw.ApplicationWindow] = None,
) -> ToastManager:
    """
    Global toast manager'ı al (singleton).

    Args:
        parent_window: Ana pencere (ilk çağrıda)

    Returns:
        ToastManager instance
    """
    global _toast_manager
    if _toast_manager is None:
        _toast_manager = ToastManager(parent_window)
    return _toast_manager


# Örnek kullanım
USAGE_EXAMPLE = """
from ui.components.toast_manager import get_toast_manager, ToastType

# Manager'ı al
toast_mgr = get_toast_manager(window)

# Başarı
toast_mgr.show_success("Sunucu reboot edildi!")

# Hata
toast_mgr.show_error("Bağlantı başarısız")

# Bilgi
toast_mgr.show_info("Sistem güncelleniyor...")

# Uyarı
toast_mgr.show_warning("Disk alanı az")

# Custom callback
def on_toast_dismissed():
    print("Toast kapatıldı")

toast_mgr.show_info("Test", duration_ms=2000, on_dismissed=on_toast_dismissed)
"""
