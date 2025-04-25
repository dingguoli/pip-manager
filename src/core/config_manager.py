import os
import json
import logging
from typing import Dict, Any, Optional, List
from PyQt5.QtCore import QObject, pyqtSignal

class ConfigManager(QObject):
    """配置管理器核心类"""
    
    # 信号定义
    config_changed = pyqtSignal(str)  # 配置变更信号
    operation_error = pyqtSignal(str)  # 操作错误信号
    
    def __init__(self, config_dir: str):
        super().__init__()
        self.config_dir = config_dir
        self.configs: Dict[str, Dict[str, Any]] = {}
        os.makedirs(config_dir, exist_ok=True)
        
    def load_config(self, name: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            if name in self.configs:
                return self.configs[name]
                
            config_file = os.path.join(self.config_dir, f"{name}.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.configs[name] = config
                    return config
            return {}
            
        except Exception as e:
            logging.error(f"加载配置 {name} 时出错: {str(e)}")
            return {}
            
    def save_config(self, name: str, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            config_file = os.path.join(self.config_dir, f"{name}.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            self.configs[name] = config
            self.config_changed.emit(name)
            return True
            
        except Exception as e:
            error_msg = f"保存配置 {name} 时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
    def get_config_value(self, name: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            config = self.load_config(name)
            return config.get(key, default)
        except Exception as e:
            logging.error(f"获取配置值 {name}.{key} 时出错: {str(e)}")
            return default
            
    def set_config_value(self, name: str, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            config = self.load_config(name)
            config[key] = value
            return self.save_config(name, config)
        except Exception as e:
            error_msg = f"设置配置值 {name}.{key} 时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
    def delete_config(self, name: str) -> bool:
        """删除配置"""
        try:
            config_file = os.path.join(self.config_dir, f"{name}.json")
            if os.path.exists(config_file):
                os.remove(config_file)
                
            if name in self.configs:
                del self.configs[name]
                
            self.config_changed.emit(name)
            return True
            
        except Exception as e:
            error_msg = f"删除配置 {name} 时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
    def list_configs(self) -> List[str]:
        """列出所有配置"""
        try:
            return [f[:-5] for f in os.listdir(self.config_dir) 
                   if f.endswith('.json')]
        except Exception as e:
            logging.error(f"列出配置时出错: {str(e)}")
            return [] 