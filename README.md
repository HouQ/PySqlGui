# PySqlGui - 数据库操作可视化工具

## 项目概述
PySqlGui 是一个基于 Python 和 Vue.js 的数据库操作可视化工具，提供自然语言生成 SQL、SQL 执行、数据库结构浏览等功能。

## 功能特性
- 数据库连接管理
- 数据库结构可视化
- 自然语言生成 SQL
- SQL 语句执行
- 查询结果展示
- 数据库表结构浏览

## 技术栈
- 前端：Vue.js + Tailwind CSS
- 后端：FastAPI + SQLAlchemy
- 数据库：MySQL

## 安装与运行

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 安装步骤
1. 克隆项目
   ```bash
   git clone https://github.com/your-repo/pysqlgui.git
   cd pysqlgui
   ```

2. 安装后端依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量
   复制 `.env.example` 为 `.env` 并修改数据库连接信息

4. 启动后端服务
   ```bash
   uvicorn backend.main:app --reload
   ```

5. 启动前端服务
   ```bash
   cd frontend
   npm install
   npm run serve
   ```

## 项目结构
```
.
├── backend/            # 后端代码
│   └── main.py         # 主程序入口
├── frontend/           # 前端代码
│   ├── assets/         # 静态资源
│   ├── static/         # 编译后的静态文件
│   ├── db-config.html  # 数据库配置页面
│   └── db-operate.html # 数据库操作页面
├── .env                # 环境变量
├── .gitignore          # Git忽略文件
├── requirements.txt    # Python依赖
└── README.md           # 项目说明
```

## 环境变量配置
复制 `.env.example` 为 `.env` 并修改以下配置：
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database
```

## 贡献指南
欢迎提交 Issue 和 PR，请遵循以下规范：
1. 提交前运行代码格式化工具
2. 保持代码风格一致
3. 提交信息清晰明确
4. 新功能需附带测试用例
