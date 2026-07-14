@echo off
chcp 65001 > nul
echo ================================================
echo   小说数据分析推荐系统 - 快速启动
echo ================================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo [2/4] 检查Django安装...
python -c "import django" > nul 2>&1
if errorlevel 1 (
    echo 错误: Django未安装
    echo 请运行: pip install django pymysql pandas numpy matplotlib
    pause
    exit /b 1
)

echo [3/4] 检查MySQL连接...
python -c "import pymysql" > nul 2>&1
if errorlevel 1 (
    echo 警告: PyMySQL未安装，数据库功能可能不可用
) else (
    echo PyMySQL已安装
)

echo [4/4] 启动Django开发服务器...
echo.
echo 访问地址:
echo   网站首页: http://127.0.0.1:8000/
echo   管理后台: http://127.0.0.1:8000/admin/
echo.
echo 按 Ctrl+C 停止服务器
echo.

python manage.py runserver

pause
