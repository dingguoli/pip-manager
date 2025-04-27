import os
import sys
from typing import Dict, List, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QLineEdit, QTableWidget,
                            QTableWidgetItem, QMessageBox, QComboBox, QMenu,
                            QAction, QStatusBar, QToolBar, QDialog, QFormLayout,
                            QSpinBox, QCheckBox, QToolTip, QHeaderView, QProgressBar,
                            QFileDialog, QListWidget, QListWidgetItem, QInputDialog,
                            QTextEdit, QGroupBox, QActionGroup, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QCursor
from datetime import datetime
import logging

from src.core.package_manager import PackageManager
from src.core.env_manager import EnvManager
from src.core.mirror_manager import MirrorManager
from src.core.config_manager import ConfigManager
from src.ui.dialogs.create_env_dialog import CreateEnvDialog
from src.ui.dialogs.install_package_dialog import InstallPackageDialog
from src.ui.dialogs.proxy_dialog import ProxyDialog
from src.ui.dialogs.theme_dialog import ThemeDialog

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self, config_manager: ConfigManager):
        """初始化主窗口"""
        try:
            super().__init__()
            self.setWindowTitle("Python包管理器")
            self.setMinimumSize(800, 600)
            
            # 初始化日志
            self.logger = logging.getLogger("PipManager.MainWindow")
            self.logger.info("初始化主窗口")
            
            # 保存配置管理器实例
            self.config_manager = config_manager
            
            # 初始化管理器（在UI之前）
            self.init_managers()
            
            # 初始化UI
            self.setup_ui()
            
            # 加载设置
            self.load_settings()
            
            # 刷新环境列表
            self.refresh_env_list()
            
            self.logger.info("主窗口初始化完成")
            
        except Exception as e:
            self.logger.error(f"主窗口创建失败: {str(e)}")
            raise
        
    def init_managers(self):
        """初始化各个管理器"""
        try:
            # 获取应用数据目录
            app_data = os.path.join(os.environ['APPDATA'], 'PipManager') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), '.pipmanager')
        
            # 初始化环境管理器
            self.env_manager = EnvManager(app_data)
            self.logger.info("环境管理器初始化完成")
        
            # 初始化镜像源管理器
            self.mirror_manager = MirrorManager(self.config_manager)
            self.logger.info("镜像源管理器初始化完成")
        
            # 初始化包管理器
            self.package_manager = None  # 将在选择环境后初始化
        
        except Exception as e:
            self.logger.error(f"初始化管理器时出错: {str(e)}")
            raise
        
    def setup_ui(self):
        """初始化UI"""
        try:
            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 创建主布局
            main_layout = QVBoxLayout(central_widget)
            
            # 创建工具栏
            self.create_toolbar()
            
            # 创建环境选择区域
            self.create_env_section(main_layout)
            
            # 创建包列表区域
            self.create_package_section(main_layout)
            
            # 创建状态栏
            self.statusBar = QStatusBar()
            self.setStatusBar(self.statusBar)
            
        except Exception as e:
            self.logger.error(f"初始化UI时出错: {str(e)}")
            raise
        
    def create_toolbar(self):
        """创建工具栏"""
        try:
            toolbar = QToolBar()
            self.addToolBar(toolbar)
            
            # 添加环境操作按钮
            env_menu = QMenu()
            env_menu.addAction("创建环境", self.create_env)
            env_menu.addAction("导入环境", self.import_env)
            env_menu.addAction("删除环境", self.delete_env)
            
            env_btn = QPushButton("环境")
            env_btn.setMenu(env_menu)
            toolbar.addWidget(env_btn)
            
            # 添加包操作按钮
            package_menu = QMenu()
            package_menu.addAction("安装包", self.install_package)
            package_menu.addAction("卸载包", self.uninstall_package)
            package_menu.addAction("更新包", self.upgrade_package)
            package_menu.addAction("导出requirements", self.export_requirements)
            package_menu.addAction("导入requirements", self.import_requirements)
            
            package_btn = QPushButton("包")
            package_btn.setMenu(package_menu)
            toolbar.addWidget(package_btn)
            
            # 添加镜像源操作按钮
            mirror_menu = QMenu()
            
            # 创建切换镜像源子菜单
            self.switch_mirror_menu = QMenu("切换镜像源")
            self.update_mirror_menu()  # 更新镜像源列表
            mirror_menu.addMenu(self.switch_mirror_menu)
            
            mirror_menu.addSeparator()
            mirror_menu.addAction("添加镜像源", self.add_mirror)
            mirror_menu.addAction("删除镜像源", self.remove_mirror)
            mirror_menu.addAction("测试速度", self.test_mirror_speed)
            mirror_menu.addAction("重置为默认", self.reset_mirror)
            
            mirror_btn = QPushButton("镜像源")
            mirror_btn.setMenu(mirror_menu)
            toolbar.addWidget(mirror_btn)
            
            # 添加设置按钮
            settings_menu = QMenu()
            settings_menu.addAction("代理设置", self.configure_proxy)
            settings_menu.addAction("主题设置", self.configure_theme)
            
            settings_btn = QPushButton("设置")
            settings_btn.setMenu(settings_menu)
            toolbar.addWidget(settings_btn)
            
        except Exception as e:
            self.logger.error(f"创建工具栏时出错: {str(e)}")
            raise
        
    def create_env_section(self, parent_layout):
        """创建环境选择区域"""
        env_group = QGroupBox("环境")
        env_layout = QHBoxLayout(env_group)
        
        # 环境选择下拉框
        self.env_combo = QComboBox()
        self.env_combo.currentTextChanged.connect(self.on_env_changed)
        env_layout.addWidget(QLabel("当前环境:"))
        env_layout.addWidget(self.env_combo)
        
        # 环境操作按钮
        env_btn_layout = QHBoxLayout()
        
        create_btn = QPushButton("创建")
        create_btn.clicked.connect(self.create_env)
        env_btn_layout.addWidget(create_btn)
        
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.import_env)
        env_btn_layout.addWidget(import_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_env)
        env_btn_layout.addWidget(delete_btn)
        
        env_layout.addLayout(env_btn_layout)
        parent_layout.addWidget(env_group)
        
    def create_package_section(self, parent_layout):
        """创建包列表区域"""
        package_group = QGroupBox("包列表")
        package_layout = QVBoxLayout(package_group)
        
        # 搜索框和按钮布局
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索包...")
        self.search_input.textChanged.connect(self.filter_packages)
        search_layout.addWidget(self.search_input)
        
        # 高级搜索按钮
        advanced_btn = QPushButton("高级搜索")
        advanced_btn.clicked.connect(self.show_advanced_search)
        search_layout.addWidget(advanced_btn)
        
        # 添加刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_packages)
        search_layout.addWidget(refresh_btn)
        
        # 添加检查更新按钮
        check_update_btn = QPushButton("检查更新")
        check_update_btn.clicked.connect(self.check_updates)
        search_layout.addWidget(check_update_btn)
        
        package_layout.addLayout(search_layout)
        
        # 包列表表格
        self.package_table = QTableWidget()
        self.package_table.setColumnCount(5)
        self.package_table.setHorizontalHeaderLabels(["包名", "当前版本", "最新版本", "位置", "安装时间"])
        self.package_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.package_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.package_table.customContextMenuRequested.connect(self.show_context_menu)
        package_layout.addWidget(self.package_table)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        package_layout.addWidget(self.progress_bar)
        
        # 设置包列表区域的拉伸因子为7
        parent_layout.addWidget(package_group, 7)
        
        # 添加通知区域
        self.create_notification_section(parent_layout)
        
    def create_notification_section(self, parent_layout):
        """创建通知区域"""
        notification_group = QGroupBox("通知")
        notification_layout = QVBoxLayout(notification_group)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(80)  # 减小最小高度
        scroll_area.setMaximumHeight(120)  # 设置最大高度
        
        # 创建通知容器
        self.notification_container = QWidget()
        self.notification_layout = QVBoxLayout(self.notification_container)
        self.notification_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.notification_container)
        notification_layout.addWidget(scroll_area)
        
        # 添加清除按钮
        clear_btn = QPushButton("清除通知")
        clear_btn.clicked.connect(self.clear_notifications)
        notification_layout.addWidget(clear_btn)
        
        # 设置通知区域的拉伸因子为3
        parent_layout.addWidget(notification_group, 3)
        
    def delayed_init(self):
        """延迟初始化"""
        # 加载环境列表
        self.refresh_env_list()
        
        # 加载设置
        self.load_settings()
        
    def load_settings(self):
        """加载设置"""
        try:
            # 加载代理设置
            proxy_config = self.config_manager.load_config('proxy')
            if proxy_config:
                self.apply_proxy_settings(proxy_config)
            
            # 加载主题设置
            theme_config = self.config_manager.load_config('theme')
            if theme_config:
                self.apply_theme(theme_config)
            else:
                # 使用默认浅色主题
                self.apply_theme(ThemeDialog.PREDEFINED_THEMES["浅色"])
                
        except Exception as e:
            self.logger.error(f"加载设置时出错: {str(e)}")
            # 使用默认主题
            self.apply_theme(ThemeDialog.PREDEFINED_THEMES["浅色"])
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存当前设置
            settings = {
                "theme": self.current_theme,
                "language": self.current_language,
                "auto_update": self.auto_update_enabled
            }
            self.config_manager.save_config("settings", settings)
            
        except Exception as e:
            self.logger.error(f"保存设置时出错: {str(e)}")
            self.add_notification("保存设置失败", "error")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 保存所有设置
            self.save_settings()
            event.accept()
        except Exception as e:
            self.logger.error(f"关闭窗口时出错: {str(e)}")
            event.accept()
        
    def refresh_env_list(self):
        """刷新环境列表"""
        self.env_combo.clear()
        envs = self.env_manager.get_env_list()
        self.env_combo.addItems(envs)
        
    def on_env_changed(self, env_name: str):
        """环境变更处理"""
        if not env_name:
            return
            
        # 获取环境Python路径
        python_path = self.env_manager.get_env_python_path(env_name)
        if not python_path:
            QMessageBox.warning(self, "错误", f"无法获取环境 {env_name} 的Python路径")
            self.add_notification(f"无法获取环境 {env_name} 的Python路径", "error")
            return
            
        # 初始化包管理器
        self.package_manager = PackageManager(python_path, env_name)
        self.package_manager.package_loaded.connect(self.on_packages_loaded)
        self.package_manager.package_load_error.connect(self.on_package_load_error)
        self.package_manager.progress_updated.connect(self.update_progress)
        self.package_manager.package_installed.connect(self.on_package_installed)
        self.package_manager.package_install_error.connect(self.on_package_install_error)
        self.package_manager.package_uninstalled.connect(self.on_package_uninstalled)
        self.package_manager.package_uninstall_error.connect(self.on_package_uninstall_error)
        self.package_manager.package_upgraded.connect(self.on_package_upgraded)
        self.package_manager.package_upgrade_error.connect(self.on_package_upgrade_error)
        
        # 加载包列表
        self.load_packages()
        self.add_notification(f"已切换到环境: {env_name}", "info")
        
    def load_packages(self):
        """加载包列表"""
        if not self.package_manager:
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.package_manager.load_packages()
        
    def on_packages_loaded(self, package_info: Dict[str, dict]):
        """包加载完成处理"""
        self.package_table.setRowCount(0)
        
        for name, info in package_info.items():
            row = self.package_table.rowCount()
            self.package_table.insertRow(row)
            
            self.package_table.setItem(row, 0, QTableWidgetItem(name))
            self.package_table.setItem(row, 1, QTableWidgetItem(info['version']))
            self.package_table.setItem(row, 2, QTableWidgetItem(info.get('latest_version', '')))
            self.package_table.setItem(row, 3, QTableWidgetItem(info['location']))
            self.package_table.setItem(row, 4, QTableWidgetItem(info['install_time'] or ''))
            
        self.progress_bar.setVisible(False)
        self.add_notification(f"已加载 {len(package_info)} 个包", "info")
        
    def on_package_load_error(self, error_msg: str):
        """包加载错误处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(error_msg, "error")
        
    def update_progress(self, progress: int):
        """更新进度条"""
        self.progress_bar.setValue(progress)
        
    def filter_packages(self):
        """过滤包列表"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.package_table.rowCount()):
            name_item = self.package_table.item(row, 0)
            if name_item and search_text in name_item.text().lower():
                self.package_table.setRowHidden(row, False)
            else:
                self.package_table.setRowHidden(row, True)
                
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        
        install_action = menu.addAction("安装包")
        uninstall_action = menu.addAction("卸载包")
        upgrade_action = menu.addAction("更新包")
        menu.addSeparator()
        show_info_action = menu.addAction("显示信息")
        
        action = menu.exec_(self.package_table.mapToGlobal(position))
        
        if action == install_action:
            self.install_package()
        elif action == uninstall_action:
            self.uninstall_package()
        elif action == upgrade_action:
            self.upgrade_package()
        elif action == show_info_action:
            self.show_package_info()
            
    def create_env(self):
        """创建环境"""
        dialog = CreateEnvDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            env_info = dialog.get_env_info()
            
            if self.env_manager.create_env(
                env_info['name'],
                env_info['path'],
                env_info['description']
            ):
                self.refresh_env_list()
                self.env_combo.setCurrentText(env_info['name'])
                self.add_notification(f"已创建环境: {env_info['name']}", "info")
            else:
                self.add_notification(f"创建环境失败: {env_info['name']}", "error")
            
    def import_env(self):
        """导入环境"""
        source_path = QFileDialog.getExistingDirectory(
            self, "选择源环境目录"
        )
        if not source_path:
            return
            
        name, ok = QInputDialog.getText(self, "导入环境", "请输入环境名称:")
        if not ok or not name:
            return
            
        if self.env_manager.import_env(source_path, name):
            self.refresh_env_list()
            self.env_combo.setCurrentText(name)
            self.add_notification(f"已导入环境: {name}", "info")
        else:
            self.add_notification(f"导入环境失败: {name}", "error")
            
    def delete_env(self):
        """删除环境"""
        current_env = self.env_combo.currentText()
        if not current_env:
            return
            
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除环境 {current_env} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.env_manager.delete_env(current_env):
                self.refresh_env_list()
                self.add_notification(f"已删除环境: {current_env}", "info")
            else:
                self.add_notification(f"删除环境失败: {current_env}", "error")
                
    def install_package(self):
        """安装包"""
        if not self.package_manager:
            self.add_notification("请先选择环境", "warning")
            return
            
        dialog = InstallPackageDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            package_name = dialog.get_package_info()
            
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 安装包
            if self.package_manager.install_package(package_name):
                self.add_notification(f"正在安装包: {package_name}", "info")
            else:
                self.add_notification(f"安装包失败: {package_name}", "error")
                self.progress_bar.setVisible(False)
                
    def on_package_installed(self, package_name: str):
        """包安装完成处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(f"包 {package_name} 安装完成", "info")
        self.load_packages()  # 刷新包列表
        
    def on_package_install_error(self, error_msg: str):
        """包安装错误处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(error_msg, "error")
        
    def on_package_uninstalled(self, package_name: str):
        """包卸载完成处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(f"包 {package_name} 卸载完成", "info")
        self.load_packages()
        
    def on_package_uninstall_error(self, error_msg: str):
        """包卸载错误处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(error_msg, "error")
        
    def on_package_upgraded(self, package_name: str):
        """包更新完成处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(f"包 {package_name} 更新完成", "info")
        self.load_packages()
        
    def on_package_upgrade_error(self, error_msg: str):
        """包更新错误处理"""
        self.progress_bar.setVisible(False)
        self.add_notification(error_msg, "error")
        
    def uninstall_package(self):
        """卸载包"""
        if not self.package_manager:
            self.add_notification("请先选择环境", "warning")
            return
            
        current_row = self.package_table.currentRow()
        if current_row < 0:
            self.add_notification("请先选择要卸载的包", "warning")
            return
            
        name = self.package_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "确认卸载",
            f"确定要卸载包 {name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 开始卸载包
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            if self.package_manager.uninstall_package(name):
                self.add_notification(f"正在卸载包: {name}", "info")
            else:
                self.add_notification(f"卸载包失败: {name}", "error")
                
    def upgrade_package(self):
        """更新包"""
        if not self.package_manager:
            self.add_notification("请先选择环境", "warning")
            return
            
        current_row = self.package_table.currentRow()
        if current_row < 0:
            self.add_notification("请先选择要更新的包", "warning")
            return
            
        name = self.package_table.item(current_row, 0).text()
        
        # 开始更新包
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        if self.package_manager.upgrade_package(name):
            self.add_notification(f"正在更新包: {name}", "info")
        else:
            self.add_notification(f"更新包失败: {name}", "error")
            self.progress_bar.setVisible(False)
        
    def export_requirements(self):
        """导出requirements.txt"""
        if not self.package_manager:
            self.add_notification("请先选择环境", "warning")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出requirements.txt", "requirements.txt", "Text Files (*.txt)"
        )
        if not file_path:
            return
            
        try:
            # 获取所有已安装的包
            packages = []
            for row in range(self.package_table.rowCount()):
                name = self.package_table.item(row, 0).text()
                version = self.package_table.item(row, 1).text()
                packages.append(f"{name}=={version}")
                
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(packages))
                
            self.add_notification(f"已导出requirements到: {file_path}", "info")
            
        except Exception as e:
            self.add_notification(f"导出requirements失败: {str(e)}", "error")
        
    def import_requirements(self):
        """导入requirements.txt"""
        if not self.package_manager:
            self.add_notification("请先选择环境", "warning")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入requirements.txt", "", "Text Files (*.txt)"
        )
        if not file_path:
            return
            
        try:
            # 读取requirements文件
            with open(file_path, 'r', encoding='utf-8') as f:
                requirements = f.readlines()
            
            # 解析包名和版本
            packages = []
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#'):  # 忽略空行和注释
                    packages.append(line)
            
            if not packages:
                self.add_notification("requirements文件为空", "warning")
                return
                
            # 显示确认对话框
            reply = QMessageBox.question(
                self, "确认导入",
                f"将要安装以下{len(packages)}个包:\n" + "\n".join(packages[:5]) + 
                ("\n..." if len(packages) > 5 else ""),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 开始安装包
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                # 逐个安装包
                total = len(packages)
                for i, package in enumerate(packages, 1):
                    self.add_notification(f"正在安装 ({i}/{total}): {package}", "info")
                    if not self.package_manager.install_package(package):
                        self.add_notification(f"安装失败: {package}", "error")
                    self.progress_bar.setValue(int(i * 100 / total))
                
                self.progress_bar.setVisible(False)
                self.add_notification("requirements导入完成", "info")
                self.load_packages()  # 刷新包列表
                
        except Exception as e:
            self.add_notification(f"导入requirements失败: {str(e)}", "error")
            self.progress_bar.setVisible(False)
        
    def update_mirror_menu(self):
        """更新镜像源菜单"""
        if not hasattr(self, 'switch_mirror_menu'):
            return
            
        self.switch_mirror_menu.clear()
        current_mirror = self.mirror_manager.get_current_mirror()
        
        # 添加所有镜像源到菜单
        for name, url in self.mirror_manager.get_mirror_list():
            # 为官方源添加分隔线
            if name != self.mirror_manager.OFFICIAL_MIRROR[0] and \
               self.switch_mirror_menu.actions() and \
               self.switch_mirror_menu.actions()[0].text() == self.mirror_manager.OFFICIAL_MIRROR[0]:
                self.switch_mirror_menu.addSeparator()
                
            action = self.switch_mirror_menu.addAction(name)
            action.setCheckable(True)
            if current_mirror and current_mirror[0] == name:
                action.setChecked(True)
            # 为官方源添加提示
            if name == self.mirror_manager.OFFICIAL_MIRROR[0]:
                action.setToolTip("使用PyPI官方源（国外服务器，速度可能较慢）")
            action.triggered.connect(lambda checked, n=name: self.switch_mirror(n))
            
    def switch_mirror(self, name: str):
        """切换镜像源"""
        if name == self.mirror_manager.OFFICIAL_MIRROR[0]:
            reply = QMessageBox.question(
                self, "确认切换",
                "您确定要切换到PyPI官方源吗？\n" +
                "官方源服务器在国外，下载速度可能较慢。",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.update_mirror_menu()  # 恢复之前的选中状态
                return
                
        if self.mirror_manager.set_current_mirror(name):
            self.add_notification(f"已切换到镜像源: {name}", "info")
            self.update_mirror_menu()  # 更新菜单选中状态
        
    def reset_mirror(self):
        """重置为默认镜像源"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置为默认镜像源吗？这将删除所有自定义镜像源。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.mirror_manager.reset_to_default():
                self.add_notification("已重置为默认镜像源", "info")
                self.update_mirror_menu()  # 更新镜像源菜单
                
    def add_mirror(self):
        """添加镜像源"""
        name, ok = QInputDialog.getText(self, "添加镜像源", "请输入镜像源名称:")
        if not ok or not name:
            return
            
        url, ok = QInputDialog.getText(
            self, "添加镜像源", 
            "请输入镜像源URL:\n(必须以http://或https://开头)",
            text="https://"
        )
        if not ok or not url:
            return
            
        if self.mirror_manager.add_mirror(name, url):
            self.add_notification(f"已添加镜像源: {name}", "info")
            self.update_mirror_menu()  # 更新镜像源菜单
                    
    def remove_mirror(self):
        """删除镜像源"""
        mirrors = self.mirror_manager.get_mirror_list()
        if not mirrors:
            self.add_notification("没有可删除的镜像源", "warning")
            return
            
        name, ok = QInputDialog.getItem(
            self, "删除镜像源", "请选择要删除的镜像源:",
            [m[0] for m in mirrors]
        )
        if not ok or not name:
            return
            
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除镜像源 {name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.mirror_manager.remove_mirror(name):
                self.add_notification(f"已删除镜像源: {name}", "info")
                self.update_mirror_menu()  # 更新镜像源菜单
        
    def test_mirror_speed(self):
        """测试镜像源速度"""
        mirrors = self.mirror_manager.get_mirror_list()
        if not mirrors:
            self.add_notification("没有可测试的镜像源", "warning")
            return
            
        self.add_notification("正在测试镜像源速度...", "info")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        def on_speed_test_finished(results):
            self.progress_bar.setVisible(False)
            if not results:
                self.add_notification("镜像源速度测试失败", "error")
                return
                
            # 显示测试结果
            result_text = "镜像源速度测试结果:\n\n"
            for name, url, delay in results:
                if delay == float('inf'):
                    result_text += f"{name}: 连接失败\n"
                else:
                    result_text += f"{name}: {delay:.2f}ms\n"
                    
            QMessageBox.information(self, "测速结果", result_text)
            self.add_notification("镜像源速度测试完成", "info")
            
        # 连接信号
        self.mirror_manager.speed_test_finished.connect(on_speed_test_finished)
        self.mirror_manager.test_mirror_speed()
        # 测试完成后断开信号
        self.mirror_manager.speed_test_finished.disconnect(on_speed_test_finished)
        
    def configure_proxy(self):
        """配置代理"""
        dialog = ProxyDialog(self)
        
        # 加载当前配置
        proxy_config = self.config_manager.load_config('proxy')
        dialog.set_proxy_config(proxy_config)
        
        if dialog.exec_() == ProxyDialog.Accepted:
            # 保存新配置
            new_config = dialog.get_proxy_config()
            if self.config_manager.save_config('proxy', new_config):
                self.add_notification("代理设置已保存", "info")
                self.apply_proxy_settings(new_config)
            else:
                self.add_notification("保存代理设置失败", "error")
                
    def configure_theme(self):
        """配置主题"""
        dialog = ThemeDialog(self)
        
        # 加载当前配置
        theme_config = self.config_manager.load_config('theme')
        dialog.set_theme_config(theme_config)
        
        if dialog.exec_() == ThemeDialog.Accepted:
            # 保存新配置
            new_config = dialog.get_theme_config()
            if self.config_manager.save_config('theme', new_config):
                self.add_notification("主题设置已保存", "info")
                self.apply_theme(new_config)
            else:
                self.add_notification("保存主题设置失败", "error")
                
    def apply_proxy_settings(self, config: dict):
        """应用代理设置"""
        try:
            if config.get('enabled', False):
                proxy_type = config.get('type', 'HTTP').lower()
                host = config.get('host', '')
                port = config.get('port', 1080)
                
                if config.get('auth_enabled', False):
                    username = config.get('username', '')
                    password = config.get('password', '')
                    proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
                else:
                    proxy_url = f"{proxy_type}://{host}:{port}"
                    
                # 设置环境变量
                os.environ['HTTP_PROXY'] = proxy_url if proxy_type == 'http' else ''
                os.environ['HTTPS_PROXY'] = proxy_url if proxy_type == 'http' else ''
                os.environ['SOCKS_PROXY'] = proxy_url if proxy_type == 'socks5' else ''
                
            else:
                # 清除代理设置
                os.environ.pop('HTTP_PROXY', None)
                os.environ.pop('HTTPS_PROXY', None)
                os.environ.pop('SOCKS_PROXY', None)
                
        except Exception as e:
            logging.error(f"应用代理设置时出错: {str(e)}")
            
    def apply_theme(self, config: dict):
        """应用主题设置"""
        try:
            if not config:
                return
                
            # 构建样式表
            style = f"""
            QMainWindow, QDialog {{
                background-color: {config.get('background', '#FFFFFF')};
                color: {config.get('text', '#000000')};
            }}
            
            QPushButton {{
                background-color: {config.get('primary', '#1976D2')};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {config.get('secondary', '#424242')};
            }}
            
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
            }}
            
            QTableWidget {{
                background-color: {config.get('background', '#FFFFFF')};
                color: {config.get('text', '#000000')};
                gridline-color: {config.get('secondary', '#424242')};
                border: 1px solid {config.get('secondary', '#424242')};
            }}
            
            QTableWidget::item:selected {{
                background-color: {config.get('primary', '#1976D2')};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {config.get('secondary', '#424242')};
                color: white;
                padding: 5px;
                border: none;
            }}
            
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {config.get('background', '#FFFFFF')};
                color: {config.get('text', '#000000')};
                border: 1px solid {config.get('secondary', '#424242')};
                padding: 5px;
                border-radius: 3px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: {config.get('primary', '#1976D2')};
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                background: white;
            }}
            
            QCheckBox {{
                color: {config.get('text', '#000000')};
            }}
            
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {config.get('primary', '#1976D2')};
                border: 2px solid {config.get('primary', '#1976D2')};
            }}
            
            QCheckBox::indicator:unchecked {{
                background-color: white;
                border: 2px solid {config.get('secondary', '#424242')};
            }}
            
            QMenu {{
                background-color: {config.get('background', '#FFFFFF')};
                color: {config.get('text', '#000000')};
                border: 1px solid {config.get('secondary', '#424242')};
            }}
            
            QMenu::item:selected {{
                background-color: {config.get('primary', '#1976D2')};
                color: white;
            }}
            
            QScrollBar:vertical {{
                background-color: {config.get('background', '#FFFFFF')};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {config.get('secondary', '#424242')};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            """
            
            # 应用样式表
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"应用主题设置时出错: {str(e)}")
            # 出错时使用基本样式
            self.setStyleSheet("")
        
    def show_advanced_search(self):
        """显示高级搜索对话框"""
        # TODO: 实现高级搜索界面
        
    def show_package_info(self):
        """显示包信息"""
        current_row = self.package_table.currentRow()
        if current_row < 0:
            return
            
        name = self.package_table.item(current_row, 0).text()
        version = self.package_table.item(current_row, 1).text()
        location = self.package_table.item(current_row, 2).text()
        install_time = self.package_table.item(current_row, 3).text()
        requires = self.package_table.item(current_row, 4).text()
        
        info = f"""包名: {name}
版本: {version}
位置: {location}
安装时间: {install_time}
依赖: {requires}"""
        
        QMessageBox.information(self, "包信息", info)
        
    def add_notification(self, message: str, level: str = "info"):
        """添加通知
        Args:
            message: 通知消息
            level: 通知级别 (info/warning/error)
        """
        notification = QLabel(message)
        notification.setWordWrap(True)
        notification.setStyleSheet(self.get_notification_style(level))
        
        # 添加时间戳
        timestamp = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp.setStyleSheet("color: gray; font-size: 10px;")
        
        # 创建通知项容器
        notification_item = QWidget()
        item_layout = QVBoxLayout(notification_item)
        item_layout.addWidget(notification)
        item_layout.addWidget(timestamp)
        
        self.notification_layout.insertWidget(0, notification_item)
        
    def get_notification_style(self, level: str) -> str:
        """获取通知样式
        Args:
            level: 通知级别
        Returns:
            str: CSS样式
        """
        styles = {
            "info": "background-color: #e3f2fd; color: #0d47a1; padding: 5px; border-radius: 3px;",
            "warning": "background-color: #fff3e0; color: #e65100; padding: 5px; border-radius: 3px;",
            "error": "background-color: #ffebee; color: #c62828; padding: 5px; border-radius: 3px;"
        }
        return styles.get(level, styles["info"])
        
    def clear_notifications(self):
        """清除所有通知"""
        while self.notification_layout.count():
            item = self.notification_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
    def check_updates(self):
        """检查包更新"""
        if not self.package_manager:
            self.add_notification("请先选择环境", "warning")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.package_manager.check_updates() 