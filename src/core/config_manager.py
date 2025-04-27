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
        self.logger = logging.getLogger("PipManager.ConfigManager")
        
    def get_config_path(self, config_name: str) -> str:
        """
        获取配置文件路径
        
        Args:
            config_name: 配置文件名
            
        Returns:
            str: 配置文件完整路径
        """
        return os.path.join(self.config_dir, f"{config_name}.json")
    
    def config_exists(self, config_name: str) -> bool:
        """
        检查配置文件是否存在
        
        Args:
            config_name: 配置文件名
            
        Returns:
            bool: 是否存在
        """
        return os.path.exists(self.get_config_path(config_name))
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        加载配置文件
        
        Args:
            config_name: 配置文件名
            
        Returns:
            Dict[str, Any]: 配置数据，如果文件不存在或出错则返回None
        """
        config_path = self.get_config_path(config_name)
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"配置文件不存在: {config_path}")
                return None
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            return None
            
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        保存配置文件
        
        Args:
            config_name: 配置文件名
            config_data: 配置数据
            
        Returns:
            bool: 是否保存成功
        """
        config_path = self.get_config_path(config_name)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            self.logger.info(f"配置已保存: {config_path}")
            self.configs[config_name] = config_data
            self.config_changed.emit(config_name)
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {str(e)}")
            self.operation_error.emit(f"保存配置文件失败: {str(e)}")
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
            config_path = self.get_config_path(name)
            if os.path.exists(config_path):
                os.remove(config_path)
                
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
            
    def update_config(self, config_name: str, updates: Dict[str, Any]) -> bool:
        """
        更新配置文件
        
        Args:
            config_name: 配置文件名
            updates: 要更新的配置项
            
        Returns:
            bool: 是否更新成功
        """
        current_config = self.load_config(config_name)
        if current_config is None:
            return False
        
        current_config.update(updates)
        return self.save_config(config_name, current_config) 