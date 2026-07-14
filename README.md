# 跨平台小说数据分析与混合推荐系统

基于 Spark + Django 构建的小说数据采集、分析、推荐全流程 Web 平台。

## 技术栈

`Python` `Django` `Apache Spark` `Hadoop` `MySQL` `Scikit-learn` `ECharts` `BeautifulSoup`

## 功能架构

```
数据采集（8平台600+小说）→ 数据清洗 → Spark多维分析 → 混合推荐引擎 → Django Web展示
```

## 核心特性

- **数据采集**：多平台爬虫，采集小说标题/作者/分类/简介/点击量/推荐数等字段
- **Spark 数据分析**：6 维度统计分析（分类分布/平台分布/热度排行/作者统计/来源分析/趋势变化）
- **三层混合推荐引擎**：
  - Content-Based：TF-IDF 文本特征 + 分类/作者加权
  - Item-Based CF：Jaccard 相似度 + 协同过滤
  - Hybrid 融合：内容(0.6) + 热度(0.4) 归一化叠加
- **Web 平台**：12 个 RESTful API，用户注册/登录、小说浏览/搜索/收藏/评分、ECharts 可视化仪表盘

## 项目结构

```
novel_project/
├── novel_analysis/          # Django 项目配置
├── apps/
│   ├── novels/              # 小说管理应用（模型/视图/模板）
│   └── users/               # 用户管理应用
├── spark_scripts/           # Spark 数据处理脚本
│   ├── crawler.py           # 数据爬虫
│   ├── data_analysis.py     # 数据分析
│   ├── recommendation.py    # 推荐算法
│   └── spark_config.py      # Spark 配置
├── data/                    # 数据目录
├── static/                  # 静态资源
└── requirements.txt
```

## 快速开始

参考 [PROJECT_GUIDE.md](novel_project/PROJECT_GUIDE.md) 和 [ENV_SETUP.md](novel_project/ENV_SETUP.md)

```bash
cd novel_project
pip install -r requirements.txt
python manage.py runserver
```

## 开发说明

本项目全程使用 Claude Code 辅助开发，涵盖代码框架生成、推荐算法调试、前端模板编写等环节。

---

🤖 部分代码由 Claude Code 辅助生成
