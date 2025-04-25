import requests
import threading
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QCheckBox, QPushButton, QComboBox,
                            QFormLayout, QSpinBox, QMessageBox, QProgressDialog)
from PyQt5.QtCore import Qt, QTimer

class ProxyDialog(QDialog):
    """代理设置对话框"""
    
    # 测试目标URL列表
    TEST_URLS = [
        "https://pypi.org",
        "https://pypi.tuna.tsinghua.edu.cn",
        "https://www.python.org"
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("代理设置")
        self.setMinimumWidth(400)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 代理启用选项
        self.enable_proxy = QCheckBox("启用代理")
        layout.addWidget(self.enable_proxy)
        
        # 代理类型选择
        form_layout = QFormLayout()
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["HTTP", "SOCKS5"])
        form_layout.addRow("代理类型:", self.proxy_type)
        
        # 代理服务器地址
        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("例如: 127.0.0.1")
        form_layout.addRow("服务器:", self.proxy_host)
        
        # 代理服务器端口
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(1080)
        form_layout.addRow("端口:", self.proxy_port)
        
        # 认证信息
        self.auth_group = QCheckBox("需要认证")
        form_layout.addRow(self.auth_group)
        
        self.proxy_username = QLineEdit()
        self.proxy_username.setEnabled(False)
        form_layout.addRow("用户名:", self.proxy_username)
        
        self.proxy_password = QLineEdit()
        self.proxy_password.setEnabled(False)
        self.proxy_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.proxy_password)
        
        layout.addLayout(form_layout)
        
        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        layout.addWidget(test_btn)
        
        # 确定和取消按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # 连接信号
        self.enable_proxy.toggled.connect(self.on_proxy_enabled)
        self.auth_group.toggled.connect(self.on_auth_enabled)
        
    def on_proxy_enabled(self, enabled: bool):
        """代理启用状态变更处理"""
        self.proxy_type.setEnabled(enabled)
        self.proxy_host.setEnabled(enabled)
        self.proxy_port.setEnabled(enabled)
        self.auth_group.setEnabled(enabled)
        if not enabled:
            self.auth_group.setChecked(False)
            
    def on_auth_enabled(self, enabled: bool):
        """认证启用状态变更处理"""
        self.proxy_username.setEnabled(enabled)
        self.proxy_password.setEnabled(enabled)
        
    def test_connection(self):
        """测试代理连接"""
        if not self.enable_proxy.isChecked():
            QMessageBox.warning(self, "提示", "请先启用代理")
            return
            
        if not self.proxy_host.text():
            QMessageBox.warning(self, "提示", "请输入代理服务器地址")
            return
            
        # 创建进度对话框
        progress = QProgressDialog("正在测试代理连接...", "取消", 0, len(self.TEST_URLS) + 1, self)
        progress.setWindowTitle("连接测试")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        # 准备代理配置
        proxy_type = self.proxy_type.currentText().lower()
        proxy_host = self.proxy_host.text()
        proxy_port = self.proxy_port.value()
        
        if self.auth_group.isChecked():
            auth = f"{self.proxy_username.text()}:{self.proxy_password.text()}@"
        else:
            auth = ""
            
        proxy_url = f"{proxy_type}://{auth}{proxy_host}:{proxy_port}"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        results = []
        current_url_index = 0
        
        def test_url():
            nonlocal current_url_index
            
            # 首先测试代理服务器是否可访问
            if current_url_index == 0:
                import socket
                try:
                    # 创建socket连接测试代理服务器是否在线
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((proxy_host, proxy_port))
                    sock.close()
                    
                    if result != 0:
                        results.append(("代理服务器", False, 
                            f"代理服务器无法连接 (错误代码: {result})\n"
                            f"请检查：\n"
                            f"1. 代理服务器 {proxy_host}:{proxy_port} 是否已启动\n"
                            f"2. 防火墙是否允许该连接\n"
                            f"3. 代理服务器地址和端口是否正确"))
                        progress.close()
                        self.show_test_results(results)
                        return
                    else:
                        results.append(("代理服务器", True, "代理服务器连接成功"))
                except Exception as e:
                    results.append(("代理服务器", False, f"连接代理服务器时出错: {str(e)}"))
                    progress.close()
                    self.show_test_results(results)
                    return
                    
                current_url_index += 1
                progress.setValue(current_url_index)
                if not progress.wasCanceled():
                    QTimer.singleShot(0, test_url)
                return
                
            # 测试外部连接
            if current_url_index > len(self.TEST_URLS) or progress.wasCanceled():
                progress.close()
                self.show_test_results(results)
                return
                
            url = self.TEST_URLS[current_url_index - 1]
            try:
                session = requests.Session()
                session.trust_env = False  # 禁用系统代理设置
                
                # 设置详细的请求选项
                response = session.get(
                    url,
                    proxies=proxies,
                    timeout=5,
                    verify=True,  # 验证SSL证书
                    allow_redirects=True,  # 允许重定向
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                )
                
                if response.status_code == 200:
                    results.append((url, True, "连接成功"))
                else:
                    results.append((url, False, f"HTTP状态码: {response.status_code}"))
                    
            except requests.exceptions.ProxyError as e:
                error_msg = str(e)
                if "NewConnectionError" in error_msg:
                    error_msg = (
                        "无法连接到代理服务器。可能的原因：\n"
                        "1. 代理服务器未运行或地址错误\n"
                        "2. 代理服务器拒绝连接\n"
                        "3. 防火墙阻止了连接"
                    )
                results.append((url, False, error_msg))
            except requests.exceptions.SSLError:
                results.append((url, False, "SSL证书验证失败"))
            except requests.exceptions.Timeout:
                results.append((url, False, "连接超时"))
            except requests.exceptions.ConnectionError as e:
                results.append((url, False, f"连接错误: {str(e)}"))
            except Exception as e:
                results.append((url, False, f"未知错误: {str(e)}"))
                
            current_url_index += 1
            progress.setValue(current_url_index)
            
            if not progress.wasCanceled():
                QTimer.singleShot(0, test_url)
                
        # 开始测试
        QTimer.singleShot(0, test_url)
        
    def show_test_results(self, results):
        """显示测试结果"""
        success_count = sum(1 for _, success, _ in results if success)
        message = f"测试完成 ({success_count}/{len(results)} 成功):\n\n"
        
        # 首先显示代理服务器测试结果
        proxy_result = next((r for r in results if r[0] == "代理服务器"), None)
        if proxy_result:
            status = "✓" if proxy_result[1] else "✗"
            message += f"{status} {proxy_result[0]}\n"
            if not proxy_result[1]:
                message += f"   {proxy_result[2]}\n\n"
            else:
                message += "\n"
                
        # 然后显示外部连接测试结果
        for url, success, detail in results:
            if url != "代理服务器":
                status = "✓" if success else "✗"
                message += f"{status} {url}\n"
                if not success:
                    message += f"   {detail}\n"
                    
        if success_count == len(results):
            QMessageBox.information(self, "测试结果", message)
        else:
            QMessageBox.warning(self, "测试结果", message)
            
    def get_proxy_config(self) -> dict:
        """获取代理配置"""
        return {
            'enabled': self.enable_proxy.isChecked(),
            'type': self.proxy_type.currentText(),
            'host': self.proxy_host.text(),
            'port': self.proxy_port.value(),
            'auth_enabled': self.auth_group.isChecked(),
            'username': self.proxy_username.text() if self.auth_group.isChecked() else '',
            'password': self.proxy_password.text() if self.auth_group.isChecked() else ''
        }
        
    def set_proxy_config(self, config: dict):
        """设置代理配置"""
        self.enable_proxy.setChecked(config.get('enabled', False))
        self.proxy_type.setCurrentText(config.get('type', 'HTTP'))
        self.proxy_host.setText(config.get('host', ''))
        self.proxy_port.setValue(config.get('port', 1080))
        self.auth_group.setChecked(config.get('auth_enabled', False))
        self.proxy_username.setText(config.get('username', ''))
        self.proxy_password.setText(config.get('password', '')) 