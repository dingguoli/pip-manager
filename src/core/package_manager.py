import os
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
import json

class PackageManager(QObject):
    """包管理器核心类"""
    
    # 信号定义
    package_loaded = pyqtSignal(dict)  # 包加载完成信号
    package_load_error = pyqtSignal(str)  # 包加载错误信号
    progress_updated = pyqtSignal(int)  # 进度更新信号
    package_installed = pyqtSignal(str)  # 包安装完成信号
    package_install_error = pyqtSignal(str)  # 包安装错误信号
    package_uninstalled = pyqtSignal(str)  # 包卸载完成信号
    package_uninstall_error = pyqtSignal(str)  # 包卸载错误信号
    package_upgraded = pyqtSignal(str)  # 包更新完成信号
    package_upgrade_error = pyqtSignal(str)  # 包更新错误信号
    
    def __init__(self, python_path: str, env_name: str):
        """初始化包管理器
        Args:
            python_path: Python解释器路径
            env_name: 环境名称
        """
        super().__init__()
        self.python_path = python_path
        self.env_name = env_name
        self.package_info: Dict[str, dict] = {}
        self._is_running = True
        
        # 初始化日志
        self.logger = logging.getLogger(f"PipManager.PackageManager.{env_name}")
        self.logger.info(f"初始化包管理器: python_path={python_path}, env_name={env_name}")
        
        # 验证Python解释器
        if not os.path.exists(python_path):
            error_msg = f"Python解释器不存在: {python_path}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        # 测试Python解释器
        try:
            result = subprocess.run(
                [python_path, "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.logger.info(f"Python版本: {result.stdout.strip()}")
            else:
                error_msg = f"Python解释器测试失败: {result.stderr}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"测试Python解释器时出错: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
    def install_package(self, package_name: str):
        """安装包
        Args:
            package_name: 包名（可包含版本号）
        """
        try:
            # 显示进度条
            self.progress_updated.emit(0)
            
            # 构建安装命令
            cmd = [self.python_path, '-m', 'pip', 'install']
            
            # 如果没有指定版本，添加--upgrade参数
            if '==' not in package_name:
                cmd.append('--upgrade')
                
            # 添加包名
            cmd.append(package_name)
            
            # 执行pip install命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # 更新进度
            self.progress_updated.emit(100)
            
            if result.returncode != 0:
                error_msg = f"安装包失败: {result.stderr}"
                logging.error(error_msg)
                self.package_install_error.emit(error_msg)
                return False
                
            # 安装成功后发送信号
            self.package_installed.emit(package_name)
            return True
            
        except Exception as e:
            error_msg = f"安装包时出错: {str(e)}"
            logging.error(error_msg)
            self.package_install_error.emit(error_msg)
            return False
            
    def check_updates(self):
        """检查包更新"""
        try:
            # 显示进度条
            self.progress_updated.emit(0)
            
            # 执行pip list命令获取当前包列表
            result = subprocess.run(
                [self.python_path, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = f"获取包列表失败: {result.stderr}"
                logging.error(error_msg)
                self.package_load_error.emit(error_msg)
                return
                
            # 解析包信息
            packages = json.loads(result.stdout)
            
            # 转换为字典格式
            package_info = {}
            total_packages = len(packages)
            
            for i, pkg in enumerate(packages):
                name = pkg['name']
                
                # 获取最新版本
                latest_result = subprocess.run(
                    [self.python_path, '-m', 'pip', 'index', 'versions', name],
                    capture_output=True,
                    text=True
                )
                
                latest_version = ''
                if latest_result.returncode == 0:
                    for line in latest_result.stdout.split('\n'):
                        if 'LATEST:' in line:
                            latest_version = line.split('LATEST:')[1].strip()
                            break
                
                package_info[name] = {
                    'version': pkg['version'],
                    'latest_version': latest_version,
                    'location': pkg.get('location', ''),
                    'install_time': ''  # TODO: 获取安装时间
                }
                
                # 更新进度
                progress = int((i + 1) / total_packages * 100)
                self.progress_updated.emit(progress)
                
            self.package_loaded.emit(package_info)
            
        except Exception as e:
            error_msg = f"检查更新时出错: {str(e)}"
            logging.error(error_msg)
            self.package_load_error.emit(error_msg)
            
    def load_packages(self) -> None:
        """加载包列表"""
        try:
            self.logger.info("开始加载包列表")
            self.progress_updated.emit(0)
            
            # 执行pip list命令
            cmd = [self.python_path, '-m', 'pip', 'list', '--format=json']
            self.logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.progress_updated.emit(25)
            
            if result.returncode != 0:
                error_msg = f"获取包列表失败: {result.stderr}"
                self.logger.error(error_msg)
                self.package_load_error.emit(error_msg)
                return
                
            # 解析包信息
            try:
                packages = json.loads(result.stdout)
                self.logger.info(f"找到 {len(packages)} 个包")
            except json.JSONDecodeError as e:
                error_msg = f"解析包列表失败: {str(e)}"
                self.logger.error(error_msg)
                self.package_load_error.emit(error_msg)
                return
                
            # 转换为字典格式
            package_info = {}
            total_packages = len(packages)
            
            for i, pkg in enumerate(packages):
                if not self._is_running:
                    self.logger.info("加载包列表被取消")
                    return
                    
                name = pkg['name']
                self.logger.debug(f"处理包 {name}")
                
                # 获取包详细信息
                show_result = subprocess.run(
                    [self.python_path, '-m', 'pip', 'show', name],
                    capture_output=True,
                    text=True
                )
                
                location = ''
                install_time = ''
                
                if show_result.returncode == 0:
                    for line in show_result.stdout.split('\n'):
                        if line.startswith('Location:'):
                            location = line.split(':', 1)[1].strip()
                            self.logger.debug(f"包 {name} 的位置: {location}")
                            
                            # 获取安装时间
                            try:
                                package_path = os.path.join(location, name)
                                if os.path.exists(package_path):
                                    timestamp = os.path.getctime(package_path)
                                    install_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                                    self.logger.debug(f"包 {name} 的安装时间: {install_time}")
                                else:
                                    # 尝试使用下划线替换连字符
                                    package_path = os.path.join(location, name.replace('-', '_'))
                                    if os.path.exists(package_path):
                                        timestamp = os.path.getctime(package_path)
                                        install_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                                        self.logger.debug(f"包 {name} 的安装时间: {install_time}")
                            except Exception as e:
                                self.logger.warning(f"获取包 {name} 安装时间失败: {str(e)}")
                else:
                    self.logger.warning(f"获取包 {name} 详细信息失败: {show_result.stderr}")
                
                package_info[name] = {
                    'version': pkg['version'],
                    'location': location,
                    'install_time': install_time
                }
                
                # 更新进度
                progress = 25 + int((i + 1) / total_packages * 75)
                self.progress_updated.emit(progress)
            
            self.logger.info("包列表加载完成")
            self.package_loaded.emit(package_info)
            
        except Exception as e:
            error_msg = f"加载包列表时出错: {str(e)}"
            self.logger.error(error_msg)
            self.package_load_error.emit(error_msg)
            
        finally:
            self.progress_updated.emit(100)
            
    def _process_package(self, package: str, index: int, total: int) -> None:
        """处理单个包的信息"""
        try:
            # 跳过空行
            if not package.strip():
                return
                
            # 分割包名和版本
            parts = package.strip().split()
            if len(parts) < 2:
                logging.warning(f"跳过无效的包信息: {package}")
                return
                
            name = parts[0]
            version = parts[1]
            
            # 跳过空包名
            if not name:
                return
                
            logging.debug(f"处理包: {name} {version}")
            
            # 获取包信息
            result = subprocess.run(
                [self.python_path, "-m", "pip", "show", name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                location = ""
                requires = []
                for line in result.stdout.split('\n'):
                    if line.startswith('Location:'):
                        location = line.split(':', 1)[1].strip()
                    elif line.startswith('Requires:'):
                        requires_str = line.split(':', 1)[1].strip()
                        if requires_str:
                            requires = [r.strip() for r in requires_str.split(',')]
                            
                # 获取安装时间
                install_time = self._get_package_install_time(location, name)
                
                # 确保包信息完整
                if name and version:
                    self.package_info[name] = {
                        'version': version,
                        'location': location,
                        'install_time': install_time,
                        'requires': requires,
                        'row': index,
                        'parent': None
                    }
                    logging.debug(f"成功处理包: {name} {version}")
                else:
                    logging.warning(f"包信息不完整: {name} {version}")
                
            # 更新进度
            progress = int((index + 1) / total * 100)
            self.progress_updated.emit(progress)
            
        except Exception as e:
            logging.error(f"处理包 {package} 时出错: {str(e)}")
            
    def _process_package_relationships(self) -> None:
        """处理包的父子关系"""
        for name, info in self.package_info.items():
            for req in info['requires']:
                if req in self.package_info:
                    self.package_info[req]['parent'] = name
                    
    def _get_package_install_time(self, location: str, name: str) -> Optional[str]:
        """获取包的安装时间"""
        try:
            if not location or not name:
                return None
                
            package_dir = os.path.join(location, name)
            if os.path.exists(package_dir):
                timestamp = os.path.getctime(package_dir)
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logging.error(f"获取包 {name} 安装时间时出错: {str(e)}")
        return None
        
    def cancel(self) -> None:
        """取消加载"""
        self._is_running = False
        
    def __del__(self) -> None:
        """析构函数"""
        self.cancel()
        
    def uninstall_package(self, package_name: str) -> bool:
        """卸载包"""
        try:
            # 显示进度条
            self.progress_updated.emit(0)
            
            # 执行pip uninstall命令
            result = subprocess.run([
                self.python_path, '-m', 'pip', 'uninstall', '-y', package_name
            ], capture_output=True, text=True)
            
            # 更新进度
            self.progress_updated.emit(100)
            
            if result.returncode != 0:
                error_msg = f"卸载包失败: {result.stderr}"
                logging.error(error_msg)
                self.package_uninstall_error.emit(error_msg)
                return False
            
            self.package_uninstalled.emit(package_name)
            return True
        except Exception as e:
            error_msg = f"卸载包时出错: {str(e)}"
            logging.error(error_msg)
            self.package_uninstall_error.emit(error_msg)
            return False

    def upgrade_package(self, package_name: str) -> bool:
        """更新包"""
        try:
            # 显示进度条
            self.progress_updated.emit(0)
            
            # 执行pip install --upgrade命令
            cmd = [self.python_path, '-m', 'pip', 'install', '--upgrade', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 更新进度
            self.progress_updated.emit(100)
            
            if result.returncode != 0:
                error_msg = f"更新包失败: {result.stderr}"
                logging.error(error_msg)
                self.package_upgrade_error.emit(error_msg)
                return False
            
            self.package_upgraded.emit(package_name)
            return True
        except Exception as e:
            error_msg = f"更新包时出错: {str(e)}"
            logging.error(error_msg)
            self.package_upgrade_error.emit(error_msg)
            return False 