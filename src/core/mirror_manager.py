import os
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal

class MirrorManager(QObject):
    """镜像源管理器核心类"""
    
    # 官方源
    OFFICIAL_MIRROR = ("PyPI官方", "https://pypi.org/simple")
    
    # 默认镜像源
    DEFAULT_MIRRORS = {
        "清华大学": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "阿里云": "https://mirrors.aliyun.com/pypi/simple",
        "华为云": "https://repo.huaweicloud.com/repository/pypi/simple",
        "中国科技大学": "https://pypi.mirrors.ustc.edu.cn/simple",
        "豆瓣": "https://pypi.doubanio.com/simple"
    }
    
    # 信号定义
    mirror_added = pyqtSignal(str)  # 镜像源添加完成信号
    mirror_removed = pyqtSignal(str)  # 镜像源删除完成信号
    mirror_changed = pyqtSignal(str, str)  # 镜像源切换完成信号(name, url)
    speed_test_finished = pyqtSignal(list)  # 测速完成信号
    operation_error = pyqtSignal(str)  # 操作错误信号
    
    def __init__(self, config_file: str):
        super().__init__()
        self.config_file = config_file
        self.mirrors: Dict[str, str] = {}
        self.current_mirror: Optional[Tuple[str, str]] = None
        self.load_mirrors()
        
    def load_mirrors(self) -> None:
        """加载镜像源配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.mirrors = config.get('mirrors', {})
                    current = config.get('current', None)
                    if current == self.OFFICIAL_MIRROR[0]:
                        self.current_mirror = self.OFFICIAL_MIRROR
                    elif current and current in self.mirrors:
                        self.current_mirror = (current, self.mirrors[current])
            
            # 如果没有镜像源，添加默认镜像源
            if not self.mirrors:
                self.mirrors = self.DEFAULT_MIRRORS.copy()
                if not self.current_mirror:
                    self.current_mirror = ("清华大学", self.mirrors["清华大学"])
                self.save_mirrors()
                
        except Exception as e:
            logging.error(f"加载镜像源配置时出错: {str(e)}")
            self.mirrors = self.DEFAULT_MIRRORS.copy()
            self.current_mirror = ("清华大学", self.mirrors["清华大学"])
            self.save_mirrors()
            
    def save_mirrors(self) -> None:
        """保存镜像源配置"""
        try:
            config = {
                'mirrors': self.mirrors,
                'current': self.current_mirror[0] if self.current_mirror else None
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存镜像源配置时出错: {str(e)}")
            
    def add_mirror(self, name: str, url: str) -> bool:
        """添加镜像源"""
        try:
            if name in self.mirrors:
                self.operation_error.emit(f"镜像源 {name} 已存在")
                return False
                
            # 验证URL格式
            if not url.startswith(('http://', 'https://')):
                self.operation_error.emit("镜像源URL必须以http://或https://开头")
                return False
                
            self.mirrors[name] = url
            self.save_mirrors()
            self.mirror_added.emit(name)
            return True
            
        except Exception as e:
            error_msg = f"添加镜像源时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
    def remove_mirror(self, name: str) -> bool:
        """删除镜像源"""
        try:
            if name not in self.mirrors:
                self.operation_error.emit(f"镜像源 {name} 不存在")
                return False
                
            del self.mirrors[name]
            self.save_mirrors()
            self.mirror_removed.emit(name)
            return True
            
        except Exception as e:
            error_msg = f"删除镜像源时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
    def get_mirror_list(self) -> List[Tuple[str, str]]:
        """获取镜像源列表，包括官方源"""
        mirrors = [(name, url) for name, url in self.mirrors.items()]
        return [self.OFFICIAL_MIRROR] + mirrors
        
    def test_mirror_speed(self) -> None:
        """测试镜像源速度"""
        try:
            results = []
            for name, url in self.mirrors.items():
                try:
                    # 测试连接速度
                    start_time = time.time()
                    response = requests.get(url, timeout=5)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        delay = (end_time - start_time) * 1000  # 转换为毫秒
                        results.append((name, url, delay))
                    else:
                        results.append((name, url, float('inf')))
                        
                except Exception as e:
                    logging.error(f"测试镜像源 {name} 时出错: {str(e)}")
                    results.append((name, url, float('inf')))
                    
            # 按延迟排序
            results.sort(key=lambda x: x[2])
            self.speed_test_finished.emit(results)
            
        except Exception as e:
            error_msg = f"测试镜像源速度时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            
    def get_fastest_mirror(self) -> Optional[Tuple[str, str]]:
        """获取最快的镜像源"""
        try:
            if not self.mirrors:
                return None
                
            results = []
            for name, url in self.mirrors.items():
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=5)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        delay = (end_time - start_time) * 1000
                        results.append((name, url, delay))
                        
                except Exception:
                    continue
                    
            if not results:
                return None
                
            # 按延迟排序
            results.sort(key=lambda x: x[2])
            return (results[0][0], results[0][1])
            
        except Exception as e:
            logging.error(f"获取最快镜像源时出错: {str(e)}")
            return None

    def get_current_mirror(self) -> Optional[Tuple[str, str]]:
        """获取当前使用的镜像源"""
        return self.current_mirror
        
    def set_current_mirror(self, name: str) -> bool:
        """设置当前使用的镜像源"""
        try:
            if name == self.OFFICIAL_MIRROR[0]:
                self.current_mirror = self.OFFICIAL_MIRROR
                self.save_mirrors()
                self.mirror_changed.emit(name, self.OFFICIAL_MIRROR[1])
                return True
            elif name not in self.mirrors:
                self.operation_error.emit(f"镜像源 {name} 不存在")
                return False
                
            self.current_mirror = (name, self.mirrors[name])
            self.save_mirrors()
            self.mirror_changed.emit(name, self.mirrors[name])
            return True
            
        except Exception as e:
            error_msg = f"设置镜像源时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False
            
    def reset_to_default(self) -> bool:
        """重置为默认镜像源"""
        try:
            self.mirrors = self.DEFAULT_MIRRORS.copy()
            self.current_mirror = ("清华大学", self.mirrors["清华大学"])
            self.save_mirrors()
            return True
            
        except Exception as e:
            error_msg = f"重置镜像源时出错: {str(e)}"
            logging.error(error_msg)
            self.operation_error.emit(error_msg)
            return False 