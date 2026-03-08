"""
PalCloudy - Test: Task Manager
TaskManager sınıfını test et
"""

import unittest
import time
import sys
import os

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.task_manager import TaskManager, TaskStatus, get_task_manager


class TestTaskManager(unittest.TestCase):
    """TaskManager sınıfını test et"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.manager = TaskManager()
    
    def test_create_task(self):
        """✅ Task oluştur"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.manager.tasks)
        
        task = self.manager.get_task(task_id)
        self.assertEqual(task.task_type, "reboot")
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_get_task(self):
        """✅ Task'ı al"""
        task_id = self.manager.create_task("reinstall", {"server": "ns654321", "os": "debian11"})
        
        task = self.manager.get_task(task_id)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, task_id)
        self.assertEqual(task.params["os"], "debian11")
    
    def test_get_nonexistent_task(self):
        """✅ Olmayan task'ı al"""
        task = self.manager.get_task("nonexistent_id")
        
        self.assertIsNone(task)
    
    def test_update_progress(self):
        """✅ İlerleme durumunu güncelle"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        
        # Progress güncelle
        self.manager.update_progress(task_id, 50, "Sunucu reboot ediliyor...")
        
        task = self.manager.get_task(task_id)
        self.assertEqual(task.progress, 50)
        self.assertEqual(task.message, "Sunucu reboot ediliyor...")
        self.assertEqual(task.status, TaskStatus.RUNNING)
    
    def test_complete_task(self):
        """✅ Task'ı tamamla"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        
        result = {"status": "success", "reboot_time": 120}
        self.manager.complete_task(task_id, result)
        
        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.progress, 100)
        self.assertEqual(task.result, result)
        self.assertIsNotNone(task.completed_at)
    
    def test_fail_task(self):
        """✅ Task'ı başarısız olarak işaretle"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        
        error_msg = "Connection timeout"
        self.manager.fail_task(task_id, error_msg)
        
        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error, error_msg)
        self.assertIsNotNone(task.completed_at)
    
    def test_cancel_task(self):
        """✅ Task'ı iptal et"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        
        self.manager.cancel_task(task_id)
        
        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.CANCELLED)
    
    def test_list_tasks(self):
        """✅ Task'ları listele"""
        # Birkaç task oluştur
        task_id1 = self.manager.create_task("reboot", {"server": "ns123456"})
        task_id2 = self.manager.create_task("reinstall", {"server": "ns654321"})
        
        # Birini tamamla
        self.manager.complete_task(task_id1)
        
        # Tüm task'ları al
        all_tasks = self.manager.list_tasks()
        self.assertEqual(len(all_tasks), 2)
        
        # Completed task'ları al
        completed_tasks = self.manager.list_tasks(TaskStatus.COMPLETED)
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(completed_tasks[0].task_id, task_id1)
        
        # Pending task'ları al
        pending_tasks = self.manager.list_tasks(TaskStatus.PENDING)
        self.assertEqual(len(pending_tasks), 1)
        self.assertEqual(pending_tasks[0].task_id, task_id2)
    
    def test_task_to_dict(self):
        """✅ Task'ı dict'e dönüştür"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        
        task = self.manager.get_task(task_id)
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict['task_id'], task_id)
        self.assertEqual(task_dict['task_type'], "reboot")
        self.assertEqual(task_dict['status'], "pending")
        self.assertEqual(task_dict['progress'], 0)
    
    def test_multiple_tasks_isolation(self):
        """✅ Birden fazla task bağımsız olarak çalış"""
        task_id1 = self.manager.create_task("reboot", {"server": "ns1"})
        task_id2 = self.manager.create_task("reboot", {"server": "ns2"})
        
        # Task 1'i güncelle
        self.manager.update_progress(task_id1, 50, "Task 1 çalışıyor")
        
        # Task 2 etkilenmemiş olmalı
        task1 = self.manager.get_task(task_id1)
        task2 = self.manager.get_task(task_id2)
        
        self.assertEqual(task1.progress, 50)
        self.assertEqual(task2.progress, 0)  # Unchanged
    
    def test_cleanup_old_tasks(self):
        """✅ Eski task'ları temizle"""
        task_id = self.manager.create_task("reboot", {"server": "ns123456"})
        task = self.manager.get_task(task_id)
        
        # Task'ı tamamla (completed_at set edilir)
        self.manager.complete_task(task_id)
        
        # Cleanup'ı çalıştır (0 saatlik TTL = tümünü sil)
        self.manager.cleanup_old_tasks(hours=0)
        
        # Task artık yok
        retrieved = self.manager.get_task(task_id)
        self.assertIsNone(retrieved)


class TestGetTaskManager(unittest.TestCase):
    """Singleton get_task_manager() fonksiyonunu test et"""
    
    def test_singleton_instance(self):
        """✅ Singleton instance döner"""
        manager1 = get_task_manager()
        manager2 = get_task_manager()
        
        self.assertIs(manager1, manager2)  # Aynı nesne
    
    def test_task_persists_across_calls(self):
        """✅ Task'lar singleton'da kalır"""
        manager = get_task_manager()
        
        task_id = manager.create_task("reboot", {"server": "ns123456"})
        
        # Başka bir manager call'ı ile al
        manager2 = get_task_manager()
        task = manager2.get_task(task_id)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.task_type, "reboot")


# Test runner
if __name__ == '__main__':
    unittest.main(verbosity=2)
