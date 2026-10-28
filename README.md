# 基于大模型的智能数据库查询与管理平台

2025 年秋季中国人民大学数据库课程大作业（RUC 2023 级）。

面向扶贫产销对接业务的 Web 平台：用户可用自然语言查询和操作数据库，系统自动生成 SQL、按角色校验权限后执行，并由大模型生成数据分析报告；管理后台由 schema 配置驱动自动生成。

## 技术栈

Python · Flask · MySQL · 通义千问（DashScope，OpenAI 兼容接口）

## 运行

```bash
pip install -r requirements.txt
cp .env.example .env        # 填写数据库密码、DashScope API Key、Flask 密钥
mysql -u root -p < data/0_final.sql
python app.py
```

所有敏感配置均从环境变量（或 `.env` 文件）读取，不提交到仓库。
