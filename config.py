# ==============================================================================
# 配置文件 (config.py)
# 存储数据库连接、用户角色、LLM API等配置信息
# 所有敏感信息（数据库密码、API Key、Session 密钥）均从环境变量读取，不写入代码仓库。
# 本地开发时可复制 .env.example 为 .env 并填写真实值。
# ==============================================================================
import os

try:
    from dotenv import load_dotenv  # 可选依赖：pip install python-dotenv
    load_dotenv()
except ImportError:
    pass


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"缺少环境变量 {name}，请参考 .env.example 进行配置。")
    return value


# 目标业务数据库名称
TARGET_DB_NAME = os.environ.get("DB_NAME", "society")

# 业务数据库配置
MASTER_DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": _require_env("DB_PASSWORD"),
    "database": TARGET_DB_NAME,
}

# 应用内部用户表名 (用于存储用户名、密码和角色)
USER_TABLE_NAME = "app_users"

# 允许的角色列表
# 注意：角色的键名 (英文) 用于代码逻辑判断，值名 (中文) 用于前端显示
ALLOWED_ROLES = {
    "poor_household": "贫困户",
    "enterprise": "企业",
    "investigator": "调查员",
    "admin": "管理员"
}

# Flask Session 密钥
FLASK_SECRET_KEY = _require_env("FLASK_SECRET_KEY")

# LLM API 配置（阿里云百炼 DashScope）
DASHSCOPE_API_KEY = _require_env("DASHSCOPE_API_KEY")

# 模型名称 (例如: qwen-turbo, qwen-plus, qwen-max, qwen3-max)
MODEL_NAME = os.environ.get("MODEL_NAME", "qwen3-max")
