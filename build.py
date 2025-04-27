import os
import sys
import shutil
import subprocess
import logging
from datetime import datetime

def setup_logging():
    """配置日志"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("Builder")

def check_python_version():
    """检查Python版本"""
    logger = logging.getLogger("Builder")
    version = sys.version_info
    logger.info(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 6:
        raise RuntimeError("需要Python 3.6或更高版本")

def install_dependencies(logger):
    """安装必要的依赖"""
    logger.info("正在安装必要的依赖...")
    
    dependencies = [
        "pyinstaller",
        "pyqt5",
        "pyqt5-tools",
        "requests"
    ]
    
    for dep in dependencies:
        try:
            logger.info(f"正在安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", dep])
        except subprocess.CalledProcessError as e:
            logger.error(f"安装 {dep} 失败: {str(e)}")
            raise

def clean_build_directories(logger):
    """清理构建目录"""
    logger.info("正在清理构建目录...")
    
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                logger.info(f"已删除 {dir_name} 目录")
            except Exception as e:
                logger.error(f"删除 {dir_name} 目录失败: {str(e)}")
                raise

def create_version_file(logger):
    """创建版本信息文件"""
    logger.info("正在创建版本信息文件...")
    
    version_info = '''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'080404b0',
        [StringStruct(u'CompanyName', u''),
         StringStruct(u'FileDescription', u'Python包管理器'),
         StringStruct(u'FileVersion', u'1.0.0'),
         StringStruct(u'InternalName', u'PackageManager'),
         StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
         StringStruct(u'OriginalFilename', u'PackageManager.exe'),
         StringStruct(u'ProductName', u'Python包管理器'),
         StringStruct(u'ProductVersion', u'1.0.0')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)
'''
    
    try:
        with open('file_version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info)
        logger.info("版本信息文件创建成功")
    except Exception as e:
        logger.error(f"创建版本信息文件失败: {str(e)}")
        raise

def run_pyinstaller(logger):
    """运行PyInstaller打包"""
    logger.info("正在运行PyInstaller打包...")
    
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "PyInstaller",
            "package_manager.spec",
            "--clean"
        ])
        logger.info("PyInstaller打包完成")
    except subprocess.CalledProcessError as e:
        logger.error(f"PyInstaller打包失败: {str(e)}")
        raise

def verify_output(logger):
    """验证输出文件"""
    logger.info("正在验证输出文件...")
    
    exe_path = os.path.join('dist', 'PackageManager.exe')
    if not os.path.exists(exe_path):
        error_msg = f"输出文件不存在: {exe_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    logger.info(f"输出文件验证成功: {exe_path}")
    return exe_path

def main():
    """主函数"""
    try:
        # 设置日志
        logger = setup_logging()
        logger.info("开始构建流程...")
        
        # 检查Python版本
        check_python_version()
        
        # 安装依赖
        install_dependencies(logger)
        
        # 清理构建目录
        clean_build_directories(logger)
        
        # 创建版本信息文件
        create_version_file(logger)
        
        # 运行PyInstaller
        run_pyinstaller(logger)
        
        # 验证输出
        exe_path = verify_output(logger)
        
        logger.info("构建完成！")
        logger.info(f"可执行文件位置: {exe_path}")
        logger.info("\n提示：")
        logger.info("1. 确保系统已安装最新的Visual C++ Redistributable")
        logger.info("2. 如果启动时被杀毒软件拦截，请添加信任或白名单")
        logger.info("3. 如果遇到权限问题，请尝试以管理员身份运行")
        
    except Exception as e:
        logger = logging.getLogger("Builder")
        logger.error(f"构建过程出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 