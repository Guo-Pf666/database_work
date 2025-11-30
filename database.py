# ==============================================================================
# 数据库操作模块 (database.py)
# 封装MySQL连接和SQL执行，统一使用 root 权限。
# ==============================================================================
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Tuple, Optional
from config import MASTER_DB_CONFIG, TARGET_DB_NAME

class Database:
    """负责连接MySQL数据库并执行SQL语句的管理类，统一使用MASTER_DB_CONFIG。"""

    def __init__(self):
        """初始化数据库连接，使用 root 凭证。"""
        self.conn = None
        self.cursor = None
        try:
            self.conn = mysql.connector.connect(
                host=MASTER_DB_CONFIG['host'],
                user=MASTER_DB_CONFIG['user'],
                password=MASTER_DB_CONFIG['password'],
                database=TARGET_DB_NAME
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            print(f"ERROR: 数据库连接失败 (使用 root 账户)：{e}")
            raise ConnectionError(f"无法连接到MySQL数据库。请检查config.py中的配置或MySQL服务状态。")

    def execute_query(self, sql_query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """执行 SELECT 查询，返回结果集。"""
        try:
            self.cursor.execute(sql_query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"ERROR: SQL查询失败：{e}")
            raise RuntimeError(f"SQL查询失败：{e}")

    def execute_non_query(self, sql_statement: str, params: Optional[Tuple] = None) -> int:
        """执行 INSERT/UPDATE/DELETE/CREATE 等非查询语句，返回影响的行数。"""
        try:
            self.cursor.execute(sql_statement, params or ())
            self.conn.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"ERROR: SQL操作失败：{e}")
            raise RuntimeError(f"SQL操作失败：{e}")

    def close(self):
        """关闭数据库连接。"""
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

# 静态方法：获取当前数据库的表结构 (Schema)
def get_db_schema(db_name: str) -> str:
    """获取指定数据库的表结构信息 (用于LLM提示词)，包含中文注释。"""
    db = None
    try:
        db = Database()
        tables_query = f"SELECT table_name, table_comment FROM information_schema.tables WHERE table_schema = '{db_name}' AND table_type = 'BASE TABLE';"
        tables = db.execute_query(tables_query)
        
        schema_info = []
        for table in tables:
            table_name = table['table_name']
            table_comment = table.get('table_comment', '无描述') # 提取表注释
            
            # 使用 SHOW FULL COLUMNS 提取字段注释
            columns_query = f"SHOW FULL COLUMNS FROM {table_name}" 
            columns = db.execute_query(columns_query)
            
            column_details = []
            for col in columns:
                field_name = col['Field']
                data_type = col['Type']
                comment = col['Comment'] # 提取字段注释
                column_details.append(f"- {field_name} ({data_type}) COMMENT: {comment}")
            
            schema_info.append(f"表名: {table_name} (描述: {table_comment})\n字段:\n{'\n'.join(column_details)}\n")
        
        return "\n".join(schema_info)
    except Exception as e:
        return f"无法获取数据库结构：{e}"
    finally:
        if db:
            db.close()