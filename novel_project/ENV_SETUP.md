# 环境安装指南

## 1. 安装 Java JDK 11
Spark需要Java环境。

### 方式一：手动下载安装
1. 访问 https://adoptium.net/temurin/releases/?version=11
2. 下载 Windows x64 JDK 11
3. 安装并记住安装路径（如：C:\Program Files\Eclipse Adoptium\jdk-11.0.24+8）
4. 设置环境变量：
   - JAVA_HOME = C:\Program Files\Eclipse Adoptium\jdk-11.0.24+8
   - 在PATH中添加 %JAVA_HOME%\bin

### 验证安装
```powershell
java -version
```

## 2. 安装 Hadoop 3.3.6
Spark需要Hadoop。

### 手动下载
1. 访问 https://hadoop.apache.org/releases.html
2. 下载 hadoop-3.3.6.tar.gz
3. 解压到 D:\hadoop
4. 设置环境变量：
   - HADOOP_HOME = D:\hadoop
   - 在PATH中添加 %HADOOP_HOME%\bin

### Hadoop Windows依赖
需要下载winutils.exe和hadoop.dll到 %HADOOP_HOME%\bin

## 3. 安装 Spark 3.4.1
1. 访问 https://spark.apache.org/downloads.html
2. 下载 spark-3.4.1-bin-hadoop3.tgz
3. 解压到 D:\spark
4. 设置环境变量：
   - SPARK_HOME = D:\spark
   - 在PATH中添加 %SPARK_HOME%\bin

## 4. 安装 MySQL 8.0
### 方式一：手动下载
1. 访问 https://dev.mysql.com/downloads/mysql/
2. 下载 MySQL Installer for Windows
3. 安装时选择"Full"安装类型
4. 设置root密码，记住它

### 验证安装
```powershell
mysql --version
```

## 5. Python环境检查
```powershell
python --version  # 应该是 3.10.6 已安装
```

## 6. 安装Python依赖
```powershell
cd d:\NOVEL ANALYSIS\novel_project
pip install django pymysql pyspark pandas numpy matplotlib seaborn scikit-learn
```

## 7. 创建MySQL数据库
```sql
CREATE DATABASE novel_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'novel'@'localhost' IDENTIFIED BY 'novel123';
GRANT ALL PRIVILEGES ON novel_analysis.* TO 'novel'@'localhost';
FLUSH PRIVILEGES;
```

## 环境变量完整配置示例
```
JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-11.0.24+8
HADOOP_HOME=D:\hadoop
SPARK_HOME=D:\spark
Path=%JAVA_HOME%\bin;%HADOOP_HOME%\bin;%SPARK_HOME%\bin;...其他路径
```
