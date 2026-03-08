"""
PalCloudy Authentication Handler
API anahtarlarının şifreleme ile güvenli saklanması ve yönetimi
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict
import hashlib
import base64
from cryptography.fernet import Fernet
import configparser


class AuthHandler:
    """
    API anahtarlarını güvenli şekilde saklar ve yönetir.
    """
    
    # Ayarlar klasörü (cross-platform)
    CONFIG_DIR = Path.home() / ".config" / "palcloudy"
    CREDENTIALS_FILE = CONFIG_DIR / "credentials.enc"
    MASTER_KEY_FILE = CONFIG_DIR / ".master"
    
    def __init__(self):
        """AuthHandler'ı başlat ve config klasörünü oluştur."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.cipher = self._get_or_create_cipher()
    
    @staticmethod
    def _generate_master_key() -> str:
        """
        Master key üretir (sistem kimliğine göre unique).
        Her sistem için farklı key, güvenlik artar.
        """
        system_id = os.urandom(32)
        master_key = base64.urlsafe_b64encode(system_id)
        return master_key.decode()
    
    def _get_or_create_cipher(self) -> Fernet:
        """
        Master key'i al veya oluştur, cipher nesnesi dön.
        """
        if self.MASTER_KEY_FILE.exists():
            # Varolan master key'i oku
            with open(self.MASTER_KEY_FILE, 'rb') as f:
                master_key = f.read()
        else:
            # Yeni master key oluştur
            master_key = Fernet.generate_key()
            with open(self.MASTER_KEY_FILE, 'wb') as f:
                f.write(master_key)
            # Dosya izinlerini sınırla (owner only: 600)
            os.chmod(self.MASTER_KEY_FILE, 0o600)
        
        return Fernet(master_key)
    
    def save_credentials(
        self,
        endpoint: str,
        app_key: str,
        app_secret: str,
        consumer_key: str,
        nickname: Optional[str] = None
    ) -> bool:
        """
        API anahtarlarını şifreli şekilde kaydeder.
        
        Args:
            endpoint: API endpoint (ovh-eu, soyoustart-ca, vb.)
            app_key: OVH Application Key
            app_secret: OVH Application Secret
            consumer_key: OVH Consumer Key
            nickname: İsteğe bağlı hesap takma adı
        
        Returns:
            bool: Başarıyla kaydedildi ise True
        """
        try:
            # Mevcut credentials'ı yükle
            credentials = self.load_all_credentials() or {}
            
            # Yeni credential'ı ekle
            cred_id = hashlib.md5(
                f"{endpoint}{app_key}".encode()
            ).hexdigest()[:8]
            
            credentials[cred_id] = {
                "endpoint": endpoint,
                "app_key": app_key,
                "app_secret": app_secret,
                "consumer_key": consumer_key,
                "nickname": nickname or f"Account-{cred_id}",
                "created_at": str(Path.home().stat()), # timestamp
            }
            
            # Şifrele ve kaydet
            json_data = json.dumps(credentials, indent=2)
            encrypted = self.cipher.encrypt(json_data.encode())
            
            with open(self.CREDENTIALS_FILE, 'wb') as f:
                f.write(encrypted)
            
            # Dosya izinlerini sınırla
            os.chmod(self.CREDENTIALS_FILE, 0o600)
            
            return True
        
        except Exception as e:
            print(f"❌ Credential kaydetme hatası: {str(e)}")
            return False
    
    def load_all_credentials(self) -> Optional[Dict]:
        """
        Tüm kaydedilmiş credentials'ı yükler.
        
        Returns:
            dict: Şifresi çözülmüş credentials veya None
        """
        if not self.CREDENTIALS_FILE.exists():
            return None
        
        try:
            with open(self.CREDENTIALS_FILE, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted = self.cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted.decode())
            
            return credentials
        
        except Exception as e:
            print(f"❌ Credential yükleme hatası: {str(e)}")
            return None
    
    def get_credential(self, cred_id: str) -> Optional[Dict]:
        """
        Belirli bir credential'ı ID ile getirir.
        
        Args:
            cred_id: Credential tanımlayıcısı
        
        Returns:
            dict: Credential bilgileri veya None
        """
        credentials = self.load_all_credentials()
        
        if credentials and cred_id in credentials:
            return credentials[cred_id]
        
        return None
    
    def delete_credential(self, cred_id: str) -> bool:
        """
        Belirli bir credential'ı siler.
        
        Args:
            cred_id: Silinecek credential tanımlayıcısı
        
        Returns:
            bool: Başarıyla silindi ise True
        """
        try:
            credentials = self.load_all_credentials() or {}
            
            if cred_id in credentials:
                del credentials[cred_id]
                
                # Geri kalanları kaydet
                json_data = json.dumps(credentials, indent=2)
                encrypted = self.cipher.encrypt(json_data.encode())
                
                with open(self.CREDENTIALS_FILE, 'wb') as f:
                    f.write(encrypted)
                
                return True
            
            return False
        
        except Exception as e:
            print(f"❌ Credential silme hatası: {str(e)}")
            return False
    
    def list_credentials(self) -> list:
        """
        Kaydedilmiş tüm hesapları listeler (sensitif veriler hariç).
        
        Returns:
            list: Hesap listesi [{id, nickname, endpoint}, ...]
        """
        credentials = self.load_all_credentials() or {}
        
        return [
            {
                "id": cred_id,
                "nickname": cred.get("nickname", "Unknown"),
                "endpoint": cred.get("endpoint", ""),
            }
            for cred_id, cred in credentials.items()
        ]
    
    def validate_credentials(
        self,
        app_key: str,
        app_secret: str,
        consumer_key: str
    ) -> bool:
        """
        Credential'ların geçerli format olup olmadığını kontrol eder.
        
        Args:
            app_key: Application Key
            app_secret: Application Secret
            consumer_key: Consumer Key
        
        Returns:
            bool: Geçerli format ise True
        """
        # Basit format validasyonu
        if not all([app_key, app_secret, consumer_key]):
            return False
        
        # En az 10 karakter olmalı
        if len(app_key) < 10 or len(app_secret) < 10:
            return False
        
        return True
    
    def clear_all_credentials(self) -> bool:
        """
        Tüm kaydedilmiş credentials'ı siler.
        
        ⚠️ Uyarı: Bu işlem geri alınamaz!
        
        Returns:
            bool: Başarıyla temizlendi ise True
        """
        try:
            if self.CREDENTIALS_FILE.exists():
                self.CREDENTIALS_FILE.unlink()
            return True
        except Exception as e:
            print(f"❌ Temizleme hatası: {str(e)}")
            return False


# Singleton instance (global)
auth_handler = AuthHandler()


def get_auth_handler() -> AuthHandler:
    """Global auth handler'ı döndür."""
    return auth_handler
