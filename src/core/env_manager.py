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
    
    def __init__(self, app_dir: str):
        """初始化环境管理器
        Args:
            app_dir: 应用目录
        """
        super().__init__()
        self.app_dir = app_dir
        self.envs_dir = os.path.join(app_dir, 'envs')
        self.envs_config = os.path.join(app_dir, 'config', 'envs.json')
        
        # 创建必要的目录
        os.makedirs(self.envs_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.envs_config), exist_ok=True)
        
        # 加载环境配置
        self.load_config()
        
    def load_config(self):
        """加载环境配置"""
        if os.path.exists(self.envs_config):
            with open(self.envs_config, 'r', encoding='utf-8') as f:
                self.envs = json.load(f)
        else:
            self.envs = {}
            
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
        env_info = self.envs.get(env_name)
        if not env_info:
            return None
            
        path = env_info.get('path')
        if not path:
            return None
            
        # 获取环境中的Python解释器路径
        if os.name == 'nt':
            python_path = os.path.join(path, 'Scripts', 'python.exe')
        else:
            python_path = os.path.join(path, 'bin', 'python')
            
        return python_path if os.path.exists(python_path) else None
        
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