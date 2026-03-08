"""
PalCloudy - Core: Task Manager
Background işleri yönetmek için
"""

import uuid
import logging
from typing import Dict, Any, Callable, Optional
from enum import Enum
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task durumu enum'u"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Tek bir task'i temsil eden sınıf"""
    
    def __init__(self, task_id: str, task_type: str, params: Dict[str, Any]):
        self.task_id = task_id
        self.task_type = task_type  # "reboot", "reinstall", "power", etc.
        self.params = params
        self.status = TaskStatus.PENDING
        self.progress = 0  # 0-100
        self.message = "Başlıyor..."
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Task'ı dict'e dönüştür"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'status': self.status.value,
            'progress': self.progress,
            'message': self.message,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    """
    Background task yöneticisi.
    
    Örnek Kullanım:
        >>> manager = TaskManager()
        >>> task_id = manager.create_task("reboot", {"server": "ns123456"})
        >>> task = manager.get_task(task_id)
        >>> print(f"Durumu: {task.status.value}")
    """
    
    def __init__(self):
        """Task Manager'ı başlat"""
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        logger.info("✅ TaskManager başlatıldı")
    
    def create_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """
        Yeni bir task oluştur.
        
        Args:
            task_type: Task tipi ("reboot", "reinstall", vb.)
            params: Task parametreleri
        
        Returns:
            task_id: Oluşturulan task'ın ID'si
        """
        task_id = str(uuid.uuid4())
        
        with self.lock:
            task = Task(task_id, task_type, params)
            self.tasks[task_id] = task
        
        logger.info(f"✅ Task oluşturuldu: {task_id} ({task_type})")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Task'ı ID'sine göre al.
        
        Args:
            task_id: Task ID'si
        
        Returns:
            Task nesnesi veya None
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def update_progress(self, task_id: str, progress: int, message: str):
        """
        Task'ın ilerleme durumunu güncelle.
        
        Args:
            task_id: Task ID'si
            progress: İlerleme yüzdesi (0-100)
            message: Durum mesajı
        """
        task = self.get_task(task_id)
        if task:
            with self.lock:
                task.progress = min(100, max(0, progress))
                task.message = message
                task.status = TaskStatus.RUNNING if progress < 100 else TaskStatus.COMPLETED
            
            logger.debug(f"📊 {task_id} güncellendi: %{progress}")
    
    def complete_task(self, task_id: str, result: Optional[Dict] = None):
        """
        Task'ı tamamla.
        
        Args:
            task_id: Task ID'si
            result: Task sonucu
        """
        task = self.get_task(task_id)
        if task:
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.message = "Tamamlandı ✅"
                task.completed_at = datetime.now()
                task.result = result
            
            logger.info(f"✅ Task tamamlandı: {task_id}")
    
    def fail_task(self, task_id: str, error: str):
        """
        Task'ı başarısız olarak işaretle.
        
        Args:
            task_id: Task ID'si
            error: Hata mesajı
        """
        task = self.get_task(task_id)
        if task:
            with self.lock:
                task.status = TaskStatus.FAILED
                task.error = error
                task.message = f"Hata: {error}"
                task.completed_at = datetime.now()
            
            logger.error(f"❌ Task başarısız: {task_id} - {error}")
    
    def cancel_task(self, task_id: str):
        """
        Task'ı iptal et.
        
        Args:
            task_id: Task ID'si
        """
        task = self.get_task(task_id)
        if task:
            with self.lock:
                task.status = TaskStatus.CANCELLED
                task.message = "İptal edildi"
                task.completed_at = datetime.now()
            
            logger.info(f"⛔ Task iptal edildi: {task_id}")
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> list:
        """
        Task'ları listele.
        
        Args:
            status: Filtre (None = tüm task'lar)
        
        Returns:
            Task listesi
        """
        with self.lock:
            if status:
                return [t for t in self.tasks.values() if t.status == status]
            return list(self.tasks.values())
    
    def cleanup_old_tasks(self, hours: int = 24):
        """
        Eski task'ları sil.
        
        Args:
            hours: Kaç saatlik task'ları tutacağız
        """
        cutoff = datetime.now().timestamp() - (hours * 3600)
        
        with self.lock:
            old_tasks = [
                task_id for task_id, task in self.tasks.items()
                if task.completed_at and task.completed_at.timestamp() < cutoff
            ]
            
            for task_id in old_tasks:
                del self.tasks[task_id]
        
        logger.info(f"🗑️  {len(old_tasks)} eski task silindi")


# Singleton instance (global task manager)
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """Global task manager'ı al (singleton)"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
