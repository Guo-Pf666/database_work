# ==============================================================================
# 用户认证模块 (auth.py)
# 负责用户表维护、注册和登录逻辑。
# ==============================================================================
from typing import Optional, Dict
from database import Database
from config import USER_TABLE_NAME, ALLOWED_ROLES

class AuthManager:
    """管理应用内部的用户认证和用户表。"""

    @staticmethod
    def initialize_user_table():
        """创建用户表，如果它不存在。"""
        db = None
        try:
            db = Database()
            # 修改：删除了 region 字段，密码改为存储明文
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {USER_TABLE_NAME} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL, 
                role ENUM({', '.join([f"'{r}'" for r in ALLOWED_ROLES.keys()])}) NOT NULL
            );
            """
            db.execute_non_query(create_table_sql)
            print(f"INFO: 确保用户表 '{USER_TABLE_NAME}' 存在。")
        except Exception as e:
            print(f"FATAL ERROR: 初始化用户表失败：{e}")

    @staticmethod
    def register_user(username: str, password: str, role: str) -> bool:
        """注册新用户。"""
        if role not in ALLOWED_ROLES:
            raise ValueError("提供的角色无效。")
        
        db = None
        try:
            db = Database()
            # 直接存储明文密码
            plain_password = password 
            
            # 修改：移除了 region 插入
            insert_sql = f"""
            INSERT INTO {USER_TABLE_NAME} (username, password_hash, role)
            VALUES (%s, %s, %s);
            """
            db.execute_non_query(insert_sql, (username, plain_password, role))
            return True
        except RuntimeError as e:
            if "Duplicate entry" in str(e):
                raise ValueError("该用户名已存在，请选择其他用户名。")
            raise
        finally:
            if db:
                db.close()

    @staticmethod
    def login_user(username: str, password: str) -> Optional[Dict[str, str]]:
        """验证用户凭证。"""
        db = None
        try:
            db = Database()
            plain_password = password
            
            # 修改：移除了 region 查询
            select_sql = f"SELECT role FROM {USER_TABLE_NAME} WHERE username = %s AND password_hash = %s;"
            
            user_data = db.execute_query(select_sql, (username, plain_password))
            
            if user_data:
                return user_data[0] # 返回 { 'role': '...' }
            else:
                return None
        except Exception as e:
            print(f"ERROR: 登录过程中发生数据库错误：{e}")
            raise
        finally:
            if db:
                db.close()