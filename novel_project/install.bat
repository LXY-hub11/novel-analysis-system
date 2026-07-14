@echo off
chcp 65001 > nul
echo ================================================
echo   小说数据分析推荐系统 - 安装向导
echo ================================================
echo.

cd /d "%~dp0"

echo [步骤1] 安装Python依赖包...
echo.
pip install django pymysql pandas numpy matplotlib seaborn scikit-learn requests beautifulsoup4
if errorlevel 1 (
    echo 错误: 安装Python依赖失败
    pause
    exit /b 1
)

echo.
echo [步骤2] 检查Java环境...
java -version > nul 2>&1
if errorlevel 1 (
    echo 警告: Java未安装，Spark功能将不可用
    echo 请参考 ENV_SETUP.md 安装Java JDK 11
) else (
    echo Java已安装
)

echo.
echo [步骤3] 检查MySQL...
echo 请确保MySQL服务正在运行，并执行以下SQL命令:
echo.
echo   CREATE DATABASE novel_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo   CREATE USER 'novel'@'localhost' IDENTIFIED BY 'novel123';
echo   GRANT ALL PRIVILEGES ON novel_analysis.* TO 'novel'@'localhost';
echo   FLUSH PRIVILEGES;
echo.

set /p continue="执行完上述SQL命令后，按回车继续..."

echo.
echo [步骤4] 运行数据库迁移...
python manage.py makemigrations
python manage.py migrate

echo.
echo [步骤5] 导入小说数据...
if exist "..\novels_data.json" (
    cd spark_scripts
    python import_to_db.py
    cd ..
) else (
    echo 警告: 未找到 novels_data.json 文件
)

echo.
echo ================================================
echo   安装完成!
echo ================================================
echo.
echo 启动服务器: 双击运行 start_server.bat
echo 或手动运行: python manage.py runserver
echo.
echo 详细说明请查看: PROJECT_GUIDE.md
echo.

pause
