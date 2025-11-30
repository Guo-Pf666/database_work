# ==============================================================================
# 配置文件 (config.py)
# 存储数据库连接、用户角色、LLM API等配置信息
# ==============================================================================

# 业务数据库配置
# 应用程序将统一使用此 MASTER_DB_CONFIG (root 账户) 来执行所有 SQL 操作
MASTER_DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "password": "Gpf040612",  # *** 请替换为您的 MySQL root 密码 ***
    "database": "society"           
}

# 目标业务数据库名称
TARGET_DB_NAME = "society"

# 应用内部用户表名 (用于存储用户名、密码哈希和角色)
USER_TABLE_NAME = "app_users"

# 允许的角色列表
# 注意：角色的键名 (英文) 用于代码逻辑判断，值名 (中文) 用于前端显示
ALLOWED_ROLES = {
    "poor_household": "贫困户", # 农户 (farmer) 已修改为 贫困户 (poor_household)
    "enterprise": "企业",
    "investigator": "调查员",
    "admin": "管理员"
}


# LLM API 配置 (讯飞星火配置)
# *** 请替换为您的实际配置信息 ***
# APPID = "8a734c3b"
# APISecret = "MzliNmU5NWM4YmQ4N2IwNjRkZDY3ZTk0"
# APIKey = "bb13416edf475974dc4b22b8fe07208b"
# LLM_HOST = "wss://spark-api.xf-yun.com/v1/x1"
# DOMAIN = "spark-x"

DASHSCOPE_API_KEY = "sk-69135be7050c4b5d8f0415741e8a4af4" 

# 模型名称 (例如: qwen-turbo, qwen-plus, qwen-max, qwen3-max)
MODEL_NAME = "qwen3-max"