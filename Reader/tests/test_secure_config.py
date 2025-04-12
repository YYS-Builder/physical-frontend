import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from config.secure_config import SecureConfig

class TestSecureConfig:
    def setup_method(self):
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "secure_config.json")
        self.key_file = os.path.join(self.test_dir, "config_key.key")
        self.audit_log = os.path.join(self.test_dir, "config_audit.log")
        
        # Initialize config
        self.config = SecureConfig(self.config_file)
    
    def teardown_method(self):
        # Clean up test files
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that initialization creates necessary files"""
        assert os.path.exists(self.config_file)
        assert os.path.exists(self.key_file)
        assert os.path.exists(self.audit_log)
    
    def test_set_get_string(self):
        """Test setting and getting string values"""
        test_key = "test_string"
        test_value = "Hello, World!"
        
        self.config.set_value(test_key, test_value)
        assert self.config.get_value(test_key) == test_value
    
    def test_set_get_number(self):
        """Test setting and getting numeric values"""
        test_key = "test_number"
        test_value = 42
        
        self.config.set_value(test_key, test_value)
        assert self.config.get_value(test_key) == test_value
    
    def test_set_get_list(self):
        """Test setting and getting list values"""
        test_key = "test_list"
        test_value = [1, 2, 3, "four"]
        
        self.config.set_value(test_key, test_value)
        assert self.config.get_value(test_key) == test_value
    
    def test_set_get_dict(self):
        """Test setting and getting dictionary values"""
        test_key = "test_dict"
        test_value = {"key1": "value1", "key2": 2}
        
        self.config.set_value(test_key, test_value)
        assert self.config.get_value(test_key) == test_value
    
    def test_default_value(self):
        """Test getting default values for non-existent keys"""
        default_value = "default"
        assert self.config.get_value("non_existent_key", default_value) == default_value
    
    def test_key_rotation(self):
        """Test key rotation functionality"""
        # Set some test values
        self.config.set_value("key1", "value1")
        self.config.set_value("key2", "value2")
        
        # Force key rotation
        self.config.force_key_rotation()
        
        # Verify values are still accessible
        assert self.config.get_value("key1") == "value1"
        assert self.config.get_value("key2") == "value2"
        
        # Verify old key was backed up
        backup_files = [f for f in os.listdir(self.test_dir) if f.endswith(".bak")]
        assert len(backup_files) == 1
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        # Perform some operations
        self.config.set_value("test_key", "test_value")
        self.config.get_value("test_key")
        self.config.force_key_rotation()
        
        # Read audit log
        log_content = self.config.get_audit_log()
        
        # Verify log contains expected entries
        assert "Set configuration value for key: test_key" in log_content
        assert "Rotated encryption key" in log_content
    
    def test_get_all_config(self):
        """Test retrieving all configuration values"""
        # Set multiple values
        test_values = {
            "key1": "value1",
            "key2": 42,
            "key3": [1, 2, 3],
            "key4": {"a": 1, "b": 2}
        }
        
        for key, value in test_values.items():
            self.config.set_value(key, value)
        
        # Get all config
        all_config = self.config.get_all_config()
        
        # Verify all values are present and correct
        for key, value in test_values.items():
            assert key in all_config
            assert all_config[key] == value 