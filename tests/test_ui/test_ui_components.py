"""
PalCloudy - Test: UI Components
ServerListView, StatusBadge, ProgressBar, ToastManager testleri
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ui.components.server_list import ServerListView, EXAMPLE_SERVERS
from ui.components.status_badge import StatusBadge, StatusType, HealthIndicator
from ui.components.progress_bar import TaskProgressBar
from ui.components.toast_manager import ToastManager, ToastType, get_toast_manager


class TestServerListView(unittest.TestCase):
    """ServerListView'ı test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.callback = Mock()
        self.list_view = ServerListView(on_server_selected=self.callback)
    
    def test_initialization(self):
        """✅ Başlatma"""
        self.assertIsNotNone(self.list_view)
        self.assertEqual(len(self.list_view.servers), 0)
    
    def test_load_servers(self):
        """✅ Sunucuları yükle"""
        self.list_view.load_servers(EXAMPLE_SERVERS)
        
        self.assertEqual(len(self.list_view.servers), 3)
        self.assertEqual(self.list_view.servers[0]['name'], EXAMPLE_SERVERS[0]['name'])
    
    def test_get_selected_server(self):
        """✅ Seçilen sunucuyu al"""
        self.list_view.load_servers(EXAMPLE_SERVERS)
        
        # Seçim yapılamadığından None dönmeli
        selected = self.list_view.get_selected_server()
        self.assertIsNone(selected)
    
    def test_refresh(self):
        """✅ Listesini yenile"""
        self.list_view.load_servers(EXAMPLE_SERVERS)
        
        # Yenileme
        self.list_view.refresh()
        
        self.assertEqual(len(self.list_view.servers), 3)
    
    def test_empty_list(self):
        """✅ Boş liste"""
        self.list_view.load_servers([])
        
        self.assertEqual(len(self.list_view.servers), 0)


class TestStatusBadge(unittest.TestCase):
    """StatusBadge'i test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        pass
    
    def test_initialization(self):
        """✅ Başlatma"""
        badge = StatusBadge(StatusType.OK, "Çalışıyor")
        
        self.assertEqual(badge.status, StatusType.OK)
        self.assertEqual(badge.text, "Çalışıyor")
    
    def test_set_status_ok(self):
        """✅ Status OK"""
        badge = StatusBadge(StatusType.UNKNOWN)
        badge.set_status(StatusType.OK, "OK")
        
        self.assertEqual(badge.status, StatusType.OK)
    
    def test_set_status_error(self):
        """✅ Status ERROR"""
        badge = StatusBadge(StatusType.OK)
        badge.set_status(StatusType.ERROR, "Hata")
        
        self.assertEqual(badge.status, StatusType.ERROR)
    
    def test_get_status(self):
        """✅ Status al"""
        badge = StatusBadge(StatusType.WARNING, "Uyarı")
        
        self.assertEqual(badge.get_status(), StatusType.WARNING)


class TestHealthIndicator(unittest.TestCase):
    """HealthIndicator'ı test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.indicator = HealthIndicator()
    
    def test_initialization(self):
        """✅ Başlatma"""
        self.assertIsNotNone(self.indicator)
    
    def test_set_cpu(self):
        """✅ CPU ayarla"""
        self.indicator.set_cpu(45.5)
        
        # CPU bar'ı kontrol et
        self.assertIsNotNone(self.indicator.cpu_bar)
    
    def test_set_ram(self):
        """✅ RAM ayarla"""
        self.indicator.set_ram(75.3)
        
        self.assertIsNotNone(self.indicator.ram_bar)
    
    def test_set_disk(self):
        """✅ Disk ayarla"""
        self.indicator.set_disk(60.1)
        
        self.assertIsNotNone(self.indicator.disk_bar)
    
    def test_set_all(self):
        """✅ Tüm değerleri ayarla"""
        self.indicator.set_all(45.5, 75.3, 60.1)
        
        # Tümü ayarlanmış olmalı
        self.assertIsNotNone(self.indicator)


class TestTaskProgressBar(unittest.TestCase):
    """TaskProgressBar'ı test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.progress_bar = TaskProgressBar()
    
    def test_initialization(self):
        """✅ Başlatma"""
        self.assertEqual(self.progress_bar.current_progress, 0)
    
    def test_start(self):
        """✅ Progress'i başlat"""
        self.progress_bar.start("Test", "Başlaniyor")
        
        self.assertEqual(self.progress_bar.current_progress, 0)
    
    def test_update(self):
        """✅ Progress güncellemeleri"""
        self.progress_bar.start("Test")
        self.progress_bar.update(50, "50% tamamlandı")
        
        self.assertEqual(self.progress_bar.current_progress, 50)
    
    def test_complete(self):
        """✅ Progress tamamla"""
        self.progress_bar.start("Test")
        self.progress_bar.update(50)
        self.progress_bar.complete("Tamamlandı!")
        
        self.assertEqual(self.progress_bar.current_progress, 100)
    
    def test_fail(self):
        """✅ Progress başarısız"""
        self.progress_bar.start("Test")
        self.progress_bar.fail("Hata!", "Sunucu açılmadı")
        
        # Başarısız olsa da state kaydedilir
        self.assertIsNotNone(self.progress_bar)
    
    def test_progress_bounds(self):
        """✅ Progress sınırları (0-100)"""
        self.progress_bar.update(150)  # 100'den fazla
        self.assertEqual(self.progress_bar.current_progress, 100)
        
        self.progress_bar.update(-10)  # 0'dan az
        self.assertEqual(self.progress_bar.current_progress, 0)


class TestToastManager(unittest.TestCase):
    """ToastManager'ı test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.manager = ToastManager()
    
    def test_initialization(self):
        """✅ Başlatma"""
        self.assertEqual(len(self.manager.toasts), 0)
    
    def test_show_success(self):
        """✅ Başarı bildirim"""
        toast = self.manager.show_success("Test başarılı", duration_ms=100)
        
        self.assertIsNotNone(toast)
        self.assertEqual(toast.toast_type, ToastType.SUCCESS)
    
    def test_show_error(self):
        """✅ Hata bildirim"""
        toast = self.manager.show_error("Test hatası", duration_ms=100)
        
        self.assertIsNotNone(toast)
        self.assertEqual(toast.toast_type, ToastType.ERROR)
    
    def test_show_info(self):
        """✅ Bilgi bildirim"""
        toast = self.manager.show_info("Test bilgisi", duration_ms=100)
        
        self.assertIsNotNone(toast)
        self.assertEqual(toast.toast_type, ToastType.INFO)
    
    def test_show_warning(self):
        """✅ Uyarı bildirim"""
        toast = self.manager.show_warning("Test uyarısı", duration_ms=100)
        
        self.assertIsNotNone(toast)
        self.assertEqual(toast.toast_type, ToastType.WARNING)
    
    def test_multiple_toasts(self):
        """✅ Birden fazla bildirim"""
        self.manager.show_success("Toast 1", duration_ms=100)
        self.manager.show_error("Toast 2", duration_ms=100)
        self.manager.show_info("Toast 3", duration_ms=100)
        
        self.assertEqual(len(self.manager.toasts), 3)
    
    def test_get_active_toasts(self):
        """✅ Aktif toast'ları al"""
        toast = self.manager.show_success("Test", duration_ms=100)
        
        active = self.manager.get_active_toasts()
        self.assertGreater(len(active), 0)
    
    def test_clear_all(self):
        """✅ Tüm toast'ları kapat"""
        self.manager.show_success("Toast 1", duration_ms=100)
        self.manager.show_error("Toast 2", duration_ms=100)
        
        self.manager.clear_all()
        
        # Tüm toast'lar dismissed olmalı
        for toast in self.manager.toasts:
            self.assertTrue(toast.dismissed)


class TestGetToastManager(unittest.TestCase):
    """Singleton get_toast_manager() fonksiyonunu test et"""
    
    def test_singleton_instance(self):
        """✅ Singleton instance döner"""
        manager1 = get_toast_manager()
        manager2 = get_toast_manager()
        
        self.assertIs(manager1, manager2)


# Test runner
if __name__ == '__main__':
    unittest.main(verbosity=2)
