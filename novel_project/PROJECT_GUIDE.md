# 小说数据分析推荐系统 - 项目运行指南

## 项目概述
基于Spark+Hadoop的大数据小说数据分析与可视化推荐系统

## 技术栈
- **后端框架**: Django 3.2+
- **大数据处理**: Apache Spark 3.4.1
- **数据存储**: MySQL 8.0
- **推荐算法**: 基于物品协同过滤
- **前端**: HTML5 + CSS3 + JavaScript + ECharts

## 环境安装步骤

### 1. 安装 Java JDK 11
Spark依赖Java环境。

**下载地址**: https://adoptium.net/temurin/releases/?version=11

**安装步骤**:
1. 下载 Windows x64 JDK 11
2. 安装到默认路径或自定义路径（如：D:\Java\jdk-11）
3. 设置环境变量：
   - 新建系统变量 `JAVA_HOME` = `D:\Java\jdk-11`
   - 编辑系统变量 `Path`，添加 `%JAVA_HOME%\bin`

**验证**: 打开PowerShell，运行 `java -version`

### 2. 安装 Hadoop 3.3.6
**下载地址**: https://hadoop.apache.org/releases.html

**安装步骤**:
1. 下载 hadoop-3.3.6.tar.gz
2. 解压到 D:\hadoop
3. 下载Windows依赖：
   - winutils.exe: https://github.com/steveloughran/winutils
   - hadoop.dll: 同上
   - 放入 D:\hadoop\bin
4. 设置环境变量：
   - 新建系统变量 `HADOOP_HOME` = `D:\hadoop`
   - 编辑系统变量 `Path`，添加 `%HADOOP_HOME%\bin`

**验证**: 运行 `hadoop version`

### 3. 安装 Spark 3.4.1
**下载地址**: https://spark.apache.org/downloads.html

**安装步骤**:
1. 下载 spark-3.4.1-bin-hadoop3.tgz
2. 解压到 D:\spark
3. 设置环境变量：
   - 新建系统变量 `SPARK_HOME` = `D:\spark`
   - 编辑系统变量 `Path`，添加 `%SPARK_HOME%\bin`

**验证**: 运行 `spark-submit --version`

### 4. 安装 MySQL 8.0
**下载地址**: https://dev.mysql.com/downloads/mysql/

**安装步骤**:
1. 下载 MySQL Installer for Windows
2. 选择"Full"安装类型
3. 设置root密码（记住这个密码！）
4. 端口保持默认3306

**验证**: 运行 `mysql --version`

### 5. 配置Python依赖
```bash
cd d:\NOVEL ANALYSIS\novel_project
pip install -r requirements.txt
```

## 数据库配置

### 创建数据库
```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE novel_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'novel'@'localhost' IDENTIFIED BY 'novel123';

-- 授权
GRANT ALL PRIVILEGES ON novel_analysis.* TO 'novel'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

### 修改Django settings
如果你的MySQL密码不是novel123，修改：
`d:\NOVEL ANALYSIS\novel_project\novel_analysis\settings.py` 中的 `PASSWORD`

## 项目初始化

### 1. 安装项目依赖
```bash
cd d:\NOVEL ANALYSIS\novel_project
pip install django pymysql pyspark pandas numpy matplotlib seaborn scikit-learn requests beautifulsoup4
```

### 2. 数据库迁移
```bash
cd d:\NOVEL ANALYSIS\novel_project
python manage.py makemigrations
python manage.py migrate
```

### 3. 导入小说数据
```bash
cd d:\NOVEL ANALYSIS\novel_project\spark_scripts
python import_to_db.py
```

### 4. 创建超级管理员（可选）
```bash
python manage.py createsuperuser
```

## 启动项目

### 启动Django开发服务器
```bash
cd d:\NOVEL ANALYSIS\novel_project
python manage.py runserver
```

### 访问系统
- 网站首页: http://127.0.0.1:8000/
- 管理后台: http://127.0.0.1:8000/admin/
- 小说列表: http://127.0.0.1:8000/novels/
- 数据可视化: http://127.0.0.1:8000/visualization/
- 个性化推荐: http://127.0.0.1:8000/recommendations/

## Spark数据分析运行

### 运行数据分析脚本
```bash
cd d:\NOVEL ANALYSIS\novel_project\spark_scripts
python data_analysis.py
```

### 运行推荐算法测试
```bash
cd d:\NOVEL ANALYSIS\novel_project\spark_scripts
python recommendation.py
```

### 注意事项
- 确保JAVA_HOME、HADOOP_HOME、SPARK_HOME环境变量已设置
- Spark需要较大的内存，建议至少4GB可用内存

## 项目结构
```
d:\NOVEL ANALYSIS\novel_project\
├── novel_analysis\          # Django项目配置
│   ├── settings.py         # 项目设置
│   ├── urls.py             # URL路由
│   └── wsgi.py             # WSGI配置
├── apps\                    # 应用目录
│   ├── novels\            # 小说管理应用
│   │   ├── models.py      # 数据模型
│   │   ├── views.py       # 视图函数
│   │   ├── urls.py        # URL路由
│   │   ├── admin.py       # 管理后台
│   │   └── templates\     # 模板文件
│   └── users\             # 用户管理应用
│       ├── models.py      # 用户模型
│       ├── views.py       # 视图函数
│       └── templates\     # 模板文件
├── spark_scripts\          # Spark脚本
│   ├── spark_config.py    # Spark配置
│   ├── data_analysis.py   # 数据分析
│   ├── recommendation.py  # 推荐算法
│   ├── crawler.py         # 数据爬虫
│   └── import_to_db.py    # 数据导入
├── data\                   # 数据目录
├── logs\                   # 日志目录
├── static\                 # 静态文件
│   ├── css\
│   └── js\
├── manage.py              # Django管理脚本
└── requirements.txt       # Python依赖
```

## 功能说明

### 1. 首页
- 系统介绍
- 最新小说展示
- 热门小说排行
- 系统功能概览

### 2. 小说列表
- 分类筛选
- 关键词搜索
- 分页浏览

### 3. 小说详情
- 小说信息展示
- 收藏功能
- 五星评分
- 相似小说推荐

### 4. 分类分析
- 分类数据统计
- 饼图可视化

### 5. 数据可视化
- 分类分布图
- 平台分布图
- 来源分布图

### 6. 个性化推荐
- 基于收藏的推荐
- 基于物品协同过滤
- 混合推荐策略

### 7. 用户管理
- 用户注册/登录
- 个人资料管理
- 收藏管理
- 活动历史

## 常见问题

### 1. Spark连接错误
- 确保JAVA_HOME设置正确
- 确保winutils.exe在HADOOP_HOME\bin下
- 重启终端后生效

### 2. MySQL连接错误
- 检查MySQL服务是否启动
- 检查用户名密码是否正确
- 检查端口3306是否被占用

### 3. 内存不足
- 在spark_config.py中减小spark.driver.memory
- 或关闭其他占用内存的程序

## 技术支持
如有问题，请检查：
1. 环境变量是否正确设置
2. 所有服务是否启动
3. 依赖是否完整安装
