import os
import sys
import shutil
import datetime
import subprocess
from pathlib import Path

def create_source_backup():
    """创建源代码备份"""
    print("正在创建源代码备份...")
    
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"package_manager_source_{timestamp}"
    
    # 要包含的目录和文件
    include_paths = [
        "src",
        "config",
        "requirements.txt",
        "README.md",
        "run.bat",
        "run.sh",
        ".gitignore"
    ]
    
    # 创建临时目录
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    backup_dir = os.path.join("dist", backup_name)
    os.makedirs(backup_dir)
    
    # 复制文件和目录
    for path in include_paths:
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(backup_dir, path))
        elif os.path.isfile(path):
            shutil.copy2(path, backup_dir)
    
    # 创建zip文件
    shutil.make_archive(os.path.join("dist", backup_name), 'zip', backup_dir)
    
    # 清理临时目录
    shutil.rmtree(backup_dir)
    
    print(f"源代码备份已创建: dist/{backup_name}.zip")

def create_executable():
    """创建可执行文件"""
    print("正在创建可执行文件...")
    
    # 确保dist目录存在
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # 安装必要的依赖
    print("正在安装必要的依赖...")
    dependencies = [
        "pyinstaller",
        "pywin32",
        "pyqt5",
        "requests"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", dep])
        except Exception as e:
            print(f"警告: 安装 {dep} 时出错: {str(e)}")
    
    # 直接运行pyinstaller
    print("正在打包应用程序...")
    try:
        # 清理旧的构建文件
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        
        # 使用最基本的配置
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "PyInstaller",
            "src/main.py",
            "--name=PackageManager",
            "--onefile",
            "--windowed"
        ])
        
        print("可执行文件已创建: dist/PackageManager.exe")
        print("提示：如果程序仍然无法运行，请尝试以下步骤：")
        print("1. 确保系统已安装最新的Visual C++ Redistributable")
        print("2. 检查是否有杀毒软件拦截")
        print("3. 尝试以管理员身份运行程序")
        
    except subprocess.CalledProcessError as e:
        print(f"打包过程出错: {str(e)}")
        raise

def main():
    print("开始打包流程...")
    
    try:
        # 创建源代码备份
        create_source_backup()
        
        # 创建可执行文件
        create_executable()
        
        print("\n打包完成！")
        print("您可以在dist目录下找到以下文件：")
        print("1. 源代码备份zip文件")
        print("2. PackageManager.exe可执行文件")
        
    except Exception as e:
        print(f"打包过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 