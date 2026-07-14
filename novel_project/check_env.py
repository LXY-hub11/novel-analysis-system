"""
Environment check and validation script.
Run this to verify all dependencies are properly installed.
"""
import os
import sys


def check_python_version():
    """Check Python version"""
    print("\n=== Python 版本检查 ===")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 8:
        print("✓ Python版本符合要求")
        return True
    else:
        print("⚠️ 建议使用Python 3.8+")
        return True


def check_java():
    """Check Java installation"""
    print("\n=== Java 检查 ===")
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        print(f"✓ JAVA_HOME: {java_home}")
        java_bin = os.path.join(java_home, 'bin', 'java.exe')
        if os.path.exists(java_bin):
            print("✓ Java可执行文件已找到")
            return True
        else:
            print("⚠️ Java可执行文件未找到")
            return False
    else:
        print("⚠️ JAVA_HOME未设置")
        print("  Spark需要Java环境")
        return False


def check_hadoop():
    """Check Hadoop installation"""
    print("\n=== Hadoop 检查 ===")
    hadoop_home = os.environ.get('HADOOP_HOME')
    if hadoop_home:
        print(f"✓ HADOOP_HOME: {hadoop_home}")
        hadoop_bin = os.path.join(hadoop_home, 'bin', 'hadoop.exe')
        if os.path.exists(hadoop_bin):
            print("✓ Hadoop可执行文件已找到")
            return True
        else:
            print("⚠️ Hadoop可执行文件未找到")
            return False
    else:
        print("⚠️ HADOOP_HOME未设置")
        return False


def check_spark():
    """Check Spark installation"""
    print("\n=== Spark 检查 ===")
    spark_home = os.environ.get('SPARK_HOME')
    if spark_home:
        print(f"✓ SPARK_HOME: {spark_home}")
        spark_bin = os.path.join(spark_home, 'bin', 'spark-submit.cmd')
        if os.path.exists(spark_bin):
            print("✓ Spark可执行文件已找到")
            return True
        else:
            print("⚠️ Spark可执行文件未找到")
            return False
    else:
        print("⚠️ SPARK_HOME未设置")
        return False


def check_python_packages():
    """Check Python packages"""
    print("\n=== Python 包检查 ===")
    packages = {
        'django': 'Django',
        'pymysql': 'PyMySQL',
        'pyspark': 'pyspark',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
    }

    all_installed = True
    for package, display_name in packages.items():
        try:
            if package == 'bs4':
                import bs4
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✓ {display_name}: {version}")
        except ImportError:
            print(f"✗ {display_name}: 未安装")
            all_installed = False

    return all_installed


def check_mysql():
    """Check MySQL installation"""
    print("\n=== MySQL 检查 ===")
    try:
        import pymysql
        print("✓ PyMySQL库已安装")
        print("  注意: 请确保MySQL服务正在运行")
        print("  默认配置:")
        print("    Host: localhost")
        print("    Port: 3306")
        print("    User: novel")
        print("    Password: novel123")
        print("    Database: novel_analysis")
        return True
    except ImportError:
        print("✗ PyMySQL未安装")
        return False


def check_project_structure():
    """Check project structure"""
    print("\n=== 项目结构检查 ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_dirs = [
        'novel_analysis',
        'apps',
        'apps/novels',
        'apps/users',
        'spark_scripts',
        'data',
        'logs',
    ]

    required_files = [
        'manage.py',
        'requirements.txt',
        'novel_analysis/settings.py',
        'novel_analysis/urls.py',
        'apps/novels/models.py',
        'apps/novels/views.py',
        'apps/users/models.py',
        'apps/users/views.py',
    ]

    all_good = True

    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✓ 目录: {dir_name}")
        else:
            print(f"✗ 目录缺失: {dir_name}")
            all_good = False

    for file_name in required_files:
        file_path = os.path.join(base_dir, file_name)
        if os.path.exists(file_path):
            print(f"✓ 文件: {file_name}")
        else:
            print(f"✗ 文件缺失: {file_name}")
            all_good = False

    return all_good


def main():
    """Main check function"""
    print("="*60)
    print("小说数据分析推荐系统 - 环境检查")
    print("="*60)

    results = []

    results.append(("Python版本", check_python_version()))
    results.append(("Java环境", check_java()))
    results.append(("Hadoop环境", check_hadoop()))
    results.append(("Spark环境", check_spark()))
    results.append(("Python包", check_python_packages()))
    results.append(("MySQL", check_mysql()))
    results.append(("项目结构", check_project_structure()))

    print("\n" + "="*60)
    print("检查结果汇总")
    print("="*60)

    for name, result in results:
        status = "✓ 通过" if result else "⚠️ 需要关注"
        print(f"{name}: {status}")

    print("\n" + "="*60)
    if all(r for _, r in results):
        print("✓ 所有检查通过！可以开始使用项目")
        print("\n启动项目:")
        print("  cd d:\\NOVEL ANALYSIS\\novel_project")
        print("  python manage.py runserver")
    else:
        print("⚠️ 部分检查未通过，请先解决环境问题")
        print("\n参考文档:")
        print("  - ENV_SETUP.md: 详细环境安装指南")
        print("  - PROJECT_GUIDE.md: 项目运行指南")

    print("="*60)


if __name__ == '__main__':
    main()
