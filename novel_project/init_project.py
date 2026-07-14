"""
Project initialization script.
Run this script after installing all dependencies and setting up environments.
"""
import os
import sys

def check_environment():
    """Check if all required environments are set up"""
    print("\n" + "="*60)
    print("检查环境配置")
    print("="*60)

    issues = []

    java_home = os.environ.get('JAVA_HOME')
    if not java_home:
        issues.append("JAVA_HOME 未设置")
        print("⚠️  JAVA_HOME 未设置 (Spark需要)")
    else:
        print(f"✓ JAVA_HOME: {java_home}")

    hadoop_home = os.environ.get('HADOOP_HOME')
    if not hadoop_home:
        issues.append("HADOOP_HOME 未设置")
        print("⚠️  HADOOP_HOME 未设置 (Spark需要)")
    else:
        print(f"✓ HADOOP_HOME: {hadoop_home}")

    spark_home = os.environ.get('SPARK_HOME')
    if not spark_home:
        issues.append("SPARK_HOME 未设置")
        print("⚠️  SPARK_HOME 未设置")
    else:
        print(f"✓ SPARK_HOME: {spark_home}")

    try:
        import django
        print(f"✓ Django: {django.__version__}")
    except ImportError:
        issues.append("Django 未安装")
        print("⚠️  Django 未安装")

    try:
        import pymysql
        print(f"✓ PyMySQL: 已安装")
    except ImportError:
        issues.append("PyMySQL 未安装")
        print("⚠️  PyMySQL 未安装")

    try:
        import pyspark
        print(f"✓ PySpark: {pyspark.__version__}")
    except ImportError:
        issues.append("PySpark 未安装")
        print("⚠️  PySpark 未安装")

    if issues:
        print("\n⚠️  发现问题:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n请先解决以上问题后再继续")
        return False
    else:
        print("\n✓ 所有环境检查通过!")
        return True


def setup_database():
    """Setup database"""
    print("\n" + "="*60)
    print("数据库设置")
    print("="*60)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("\n1. 创建MySQL数据库...")
    print("请确保MySQL服务已启动，并执行以下SQL命令：")
    print("""
    CREATE DATABASE novel_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'novel'@'localhost' IDENTIFIED BY 'novel123';
    GRANT ALL PRIVILEGES ON novel_analysis.* TO 'novel'@'localhost';
    FLUSH PRIVILEGES;
    """)

    input("\n执行上述SQL命令后，按回车继续...")


def run_migrations():
    """Run Django migrations"""
    print("\n" + "="*60)
    print("Django数据库迁移")
    print("="*60)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("\n1. 创建迁移文件...")
    os.system("python manage.py makemigrations")

    print("\n2. 执行迁移...")
    os.system("python manage.py migrate")

    print("\n3. 创建超级管理员...")
    print("(可选)按回车跳过，或输入用户名创建管理员")
    choice = input("是否创建管理员账号? (y/n): ")
    if choice.lower() == 'y':
        os.system("python manage.py createsuperuser")


def import_data():
    """Import novel data"""
    print("\n" + "="*60)
    print("导入小说数据")
    print("="*60)

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'novels_data.json')

    if not os.path.exists(json_path):
        print(f"⚠️  小说数据文件不存在: {json_path}")
        return

    print(f"发现小说数据文件: {json_path}")

    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spark_scripts'))

    print("\n运行数据导入脚本...")
    os.system("python import_to_db.py")


def start_server():
    """Start Django development server"""
    print("\n" + "="*60)
    print("启动Django开发服务器")
    print("="*60)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("\n启动服务器...")
    print("访问 http://127.0.0.1:8000 查看网站")
    print("访问 http://127.0.0.1:8000/admin 查看管理后台")
    print("\n按 Ctrl+C 停止服务器")

    os.system("python manage.py runserver")


def main():
    """Main initialization process"""
    print("\n" + "="*60)
    print("小说数据分析推荐系统 - 项目初始化")
    print("="*60)

    if not check_environment():
        print("\n环境检查未通过，请先安装缺失的组件")
        print("参考 ENV_SETUP.md 获取详细的安装指南")
        return

    print("\n" + "="*60)
    print("初始化选项")
    print("="*60)
    print("1. 完整初始化 (数据库设置 + 迁移 + 导入数据)")
    print("2. 仅检查环境")
    print("3. 仅设置数据库")
    print("4. 仅运行迁移")
    print("5. 仅导入数据")
    print("6. 启动服务器")
    print("0. 退出")

    choice = input("\n请选择操作 (0-6): ")

    if choice == '1':
        if check_environment():
            setup_database()
            run_migrations()
            import_data()
            print("\n" + "="*60)
            print("✓ 初始化完成!")
            print("="*60)

            start_now = input("\n是否立即启动服务器? (y/n): ")
            if start_now.lower() == 'y':
                start_server()
    elif choice == '2':
        check_environment()
    elif choice == '3':
        setup_database()
    elif choice == '4':
        run_migrations()
    elif choice == '5':
        import_data()
    elif choice == '6':
        start_server()
    else:
        print("退出")


if __name__ == '__main__':
    main()
