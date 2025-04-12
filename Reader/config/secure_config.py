import os
from cryptography.fernet import Fernet
import logging
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any

class SecureConfig:
    def __init__(self, config_file: str = "secure_config.json"):
        self.config_file = config_file
        self.key_file = "config_key.key"
        self.fernet = None
        self.config = {}
        self.audit_log_file = "config_audit.log"
        self.key_rotation_days = 90  # Rotate key every 90 days
        
        # Setup logging
        logging.basicConfig(
            filename=self.audit_log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self._load_or_generate_key()
        self._load_config()
        
        # Check if key rotation is needed
        if self._should_rotate_key():
            self._rotate_key()
    
    def _load_or_generate_key(self):
        """Load existing key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            logging.info("Generated new encryption key")
        
        self.fernet = Fernet(key)
    
    def _load_config(self):
        """Load encrypted configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "rb") as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.config = json.loads(decrypted_data)
            logging.info("Loaded existing configuration")
        else:
            self.config = {}
            self._save_config()
            logging.info("Created new configuration file")
    
    def _save_config(self):
        """Save encrypted configuration."""
        encrypted_data = self.fernet.encrypt(json.dumps(self.config).encode())
        with open(self.config_file, "wb") as f:
            f.write(encrypted_data)
    
    def _should_rotate_key(self) -> bool:
        """Check if key rotation is needed."""
        if not os.path.exists(self.key_file):
            return False
        
        key_mtime = datetime.fromtimestamp(os.path.getmtime(self.key_file))
        return (datetime.now() - key_mtime).days >= self.key_rotation_days
    
    def _rotate_key(self):
        """Rotate the encryption key."""
        old_key = self.fernet._signing_key
        new_key = Fernet.generate_key()
        
        # Backup old key
        backup_file = f"{self.key_file}.{datetime.now().strftime('%Y%m%d')}.bak"
        with open(backup_file, "wb") as f:
            f.write(old_key)
        
        # Save new key
        with open(self.key_file, "wb") as f:
            f.write(new_key)
        
        # Re-encrypt all values with new key
        self.fernet = Fernet(new_key)
        self._save_config()
        
        logging.info(f"Rotated encryption key. Old key backed up to {backup_file}")
    
    def _encrypt_value(self, value: Any) -> str:
        """Encrypt a value."""
        if isinstance(value, (str, int, float, bool)):
            return self.fernet.encrypt(str(value).encode()).decode()
        elif isinstance(value, (list, dict)):
            return self.fernet.encrypt(json.dumps(value).encode()).decode()
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
    
    def _decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt a value."""
        try:
            decrypted = self.fernet.decrypt(encrypted_value.encode()).decode()
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
        except Exception as e:
            logging.error(f"Failed to decrypt value: {str(e)}")
            raise
    
    def set_value(self, key: str, value: Any):
        """Set a configuration value."""
        encrypted_value = self._encrypt_value(value)
        self.config[key] = encrypted_value
        self._save_config()
        logging.info(f"Set configuration value for key: {key}")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if key not in self.config:
            return default
        
        try:
            return self._decrypt_value(self.config[key])
        except Exception as e:
            logging.error(f"Failed to get value for key {key}: {str(e)}")
            return default
    
    def get_audit_log(self) -> str:
        """Get the contents of the audit log."""
        if os.path.exists(self.audit_log_file):
            with open(self.audit_log_file, "r") as f:
                return f.read()
        return ""
    
    def force_key_rotation(self):
        """Force immediate key rotation."""
        self._rotate_key()
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return {k: self.get_value(k) for k in self.config.keys()}

# Usage example:
# config = SecureConfig()
# config.initialize_config()
# config.set_value("DATABASE_URL", "your-database-url")
# db_url = config.get_value("DATABASE_URL") 