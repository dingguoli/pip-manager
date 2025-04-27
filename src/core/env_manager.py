import os
import subprocess
import logging
import json
import shutil
from typing import List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class EnvManager(QObject):
    """环境管理器核心类"""
    
    # 信号定义
    env_created = pyqtSignal(str)  # 环境创建完成信号
    env_deleted = pyqtSignal(str)  # 环境删除完成信号
    env_imported = pyqtSignal(str)  # 环境导入完成信号
    operation_error = pyqtSignal(str)  # 操作错误信号
    
    def __init__(self, app_data_dir: str):
        """初始化环境管理器
        Args:
            app_data_dir: 应用数据目录
        """
        super().__init__()
        self.app_data_dir = app_data_dir
        self.envs_dir = os.path.join(app_data_dir, 'envs')
        self.envs_config = os.path.join(app_data_dir, 'config', 'envs.json')
        
        # 初始化日志
        self.logger = logging.getLogger("PipManager.EnvManager")
        
        try:
            # 创建必要的目录
            os.makedirs(self.envs_dir, exist_ok=True)
            os.makedirs(os.path.dirname(self.envs_config), exist_ok=True)
            self.logger.info(f"创建目录成功: {self.envs_dir}, {os.path.dirname(self.envs_config)}")
            
            # 加载环境配置
            self.load_config()
            
        except Exception as e:
            self.logger.error(f"初始化环境管理器失败: {str(e)}")
            raise
            
    def load_config(self):
        """加载环境配置"""
        try:
            if os.path.exists(self.envs_config):
                with open(self.envs_config, 'r', encoding='utf-8') as f:
                    self.envs = json.load(f)
                self.logger.info(f"加载环境配置成功: {len(self.envs)} 个环境")
            else:
                self.envs = {}
                self.logger.info("环境配置文件不存在，使用空配置")
        except Exception as e:
            self.logger.error(f"加载环境配置失败: {str(e)}")
            self.envs = {}
            raise
            
    def save_config(self):
        """保存环境配置"""
        with open(self.envs_config, 'w', encoding='utf-8') as f:
            json.dump(self.envs, f, ensure_ascii=False, indent=2)
            
    def get_env_list(self) -> List[str]:
        """获取环境列表"""
        return list(self.envs.keys())
        
    def get_env_info(self, env_name: str) -> Optional[Dict]:
        """获取环境信息
        Args:
            env_name: 环境名称
        Returns:
            Dict: 环境信息
        """
        env_info = self.envs.get(env_name)
        if not env_info:
            return None
            
        try:
            # 获取Python路径
            python_path = self.get_env_python_path(env_name)
            if not python_path:
                return None
                
            # 获取Python版本
            result = subprocess.run(
                [python_path, "--version"],
                capture_output=True,
                text=True
            )
            
            version = result.stdout.strip() if result.returncode == 0 else "未知"
            
            # 合并信息
            return {
                'name': env_name,
                'path': env_info.get('path', ''),
                'python_path': python_path,
                'version': version,
                'description': env_info.get('description', ''),
                'created_at': env_info.get('created_at', '')
            }
            
        except Exception as e:
            logging.error(f"获取环境信息时出错: {str(e)}")
            return None
        
    def get_env_python_path(self, env_name: str) -> Optional[str]:
        """获取环境Python路径
        Args:
            env_name: 环境名称
        Returns:
            str: Python路径
        """
        try:
            env_info = self.envs.get(env_name)
            if not env_info:
                error_msg = f"环境 {env_name} 不存在"
                self.logger.error(error_msg)
                self.operation_error.emit(error_msg)
                return None
                
            path = env_info.get('path')
            if not path:
                error_msg = f"环境 {env_name} 的路径未设置"
                self.logger.error(error_msg)
                self.operation_error.emit(error_msg)
                return None
                
            self.logger.info(f"正在检查环境 {env_name} 的Python解释器")
            
            # 获取环境中的Python解释器路径
            possible_paths = []
            if os.name == 'nt':
                possible_paths = [
                    os.path.join(path, 'Scripts', 'python.exe'),
                    os.path.join(path, 'python.exe'),
                    os.path.join(path, 'bin', 'python.exe')
                ]
            else:
                possible_paths = [
                    os.path.join(path, 'bin', 'python'),
                    os.path.join(path, 'python')
                ]
            
            # 检查所有可能的路径
            for python_path in possible_paths:
                if os.path.exists(python_path):
                    self.logger.info(f"找到Python解释器: {python_path}")
                    return python_path
                else:
                    self.logger.debug(f"路径不存在: {python_path}")
                
            error_msg = f"在环境 {env_name} 中未找到Python解释器，已检查路径: {', '.join(possible_paths)}"
            self.logger.error(error_msg)
            self.operation_error.emit(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"获取环境 {env_name} 的Python路径时出错: {str(e)}"
            self.logger.error(error_msg)
            self.operation_error.emit(error_msg)
            return None
        
    def create_env(self, env_name: str, path: str, description: str = "") -> bool:
        """创建环境
        Args:
            env_name: 环境名称
            path: 环境路径
            description: 环境备注
        Returns:
            bool: 是否成功
        """
        # 检查环境是否已存在
        if env_name in self.envs:
            self.operation_error.emit(f"环境 {env_name} 已存在")
            return False
            
        try:
            # 在选择的路径下创建虚拟环境
            venv_path = os.path.join(path, env_name)
            
            # 创建虚拟环境
            result = subprocess.run(
                ['python', '-m', 'venv', venv_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = f"创建虚拟环境失败: {result.stderr}"
                logging.error(error_msg)
                self.operation_error.emit(error_msg)
                return False
                
            # 保存环境信息
            self.envs[env_name] = {
                'path': venv_path,  # 保存虚拟环境的路径
                'description': description,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.save_config()
            
            self.env_created.emit(env_name)
            return True
            
        except Exception as e:
            error_msg = f"创建环境时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
        
    def delete_env(self, env_name: str) -> bool:
        """删除环境
        Args:
            env_name: 环境名称
        Returns:
            bool: 是否成功
        """
        # 检查环境是否存在
        if env_name not in self.envs:
            self.operation_error.emit(f"环境 {env_name} 不存在")
            return False
            
        # 删除环境目录
        env_dir = os.path.join(self.envs_dir, env_name)
        if os.path.exists(env_dir):
            try:
                # 在Windows上需要先删除所有文件
                if os.name == 'nt':
                    for root, dirs, files in os.walk(env_dir, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(env_dir)
                else:
                    import shutil
                    shutil.rmtree(env_dir)
            except Exception as e:
                error_msg = f"删除环境时出错: {str(e)}"
                logging.error(error_msg)
                self.operation_error.emit(error_msg)
                return False
                
        # 删除环境信息
        del self.envs[env_name]
        self.save_config()
        
        self.env_deleted.emit(env_name)
        return True
        
    def import_env(self, source_path: str, env_name: str) -> bool:
        """导入环境
        Args:
            source_path: 源环境路径
            env_name: 环境名称
        Returns:
            bool: 是否成功
        """
        # 检查环境是否已存在
        if env_name in self.envs:
            self.operation_error.emit(f"环境 {env_name} 已存在")
            return False
            
        # 创建环境目录
        env_dir = os.path.join(self.envs_dir, env_name)
        if not os.path.exists(env_dir):
            os.makedirs(env_dir)
            
        # 复制环境文件
        try:
            shutil.copytree(source_path, env_dir, dirs_exist_ok=True)
        except Exception as e:
            error_msg = f"导入环境时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
        # 保存环境信息
        self.envs[env_name] = {
            'path': env_dir,
            'description': f"从 {source_path} 导入",
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_config()
        
        self.env_imported.emit(env_name)
        return True 