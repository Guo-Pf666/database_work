# ==============================================================================
# 权限检查模块 (permission.py)
# ==============================================================================
from typing import Dict, Any

class PermissionChecker:
    """根据用户角色和SQL语句判断用户是否有权执行。"""

    # 角色权限映射
    # 贫困户、企业、调查员：仅限 SELECT
    # 管理员：所有权限
    ROLE_PERMISSIONS = {
        "poor_household": { "__ALL__": ["SELECT"] },
        "enterprise": { "__ALL__": ["SELECT"] },
        "investigator": { "__ALL__": ["SELECT"] },
        "admin": { "__ALL__": ["SELECT", "INSERT", "UPDATE", "DELETE"] }
    }

    @staticmethod
    def _parse_sql_type(sql_statement: str) -> str:
        sql_upper = sql_statement.strip().upper()
        if sql_upper.startswith("SELECT"): return "SELECT"
        elif sql_upper.startswith("INSERT INTO"): return "INSERT"
        elif sql_upper.startswith("UPDATE"): return "UPDATE"
        elif sql_upper.startswith("DELETE FROM"): return "DELETE"
        return "OTHER"

    @staticmethod
    def _parse_sql_table(sql_statement: str) -> str:
        sql_upper = sql_statement.strip().upper()
        try:
            if " FROM " in sql_upper:
                parts = sql_upper.split(" FROM ")[1].strip().split()
                return parts[0].replace('`', '').replace(';', '').split(',')[0].strip()
            elif sql_upper.startswith("UPDATE"):
                parts = sql_upper.split()[1:]
                return parts[0].replace('`', '').replace(';', '')
            elif sql_upper.startswith("INSERT INTO"):
                parts = sql_upper.split(" INTO ")[1].strip().split()
                return parts[0].replace('`', '').replace(';', '')
        except:
            return "__UNKNOWN__"
        return "__UNKNOWN__"

    @staticmethod
    def check_permission(role: str, sql_statement: str) -> str:
        """
        检查给定角色的用户是否有权执行此SQL。
        修改：移除了 region 参数。
        """
        sql_type = PermissionChecker._parse_sql_type(sql_statement)
        
        if sql_type == "OTHER":
            return f"权限拒绝：不支持执行 '{sql_type}' 类型的语句。"

        permissions = PermissionChecker.ROLE_PERMISSIONS.get(role, {})
        allowed_ops = permissions.get("__ALL__", [])

        if sql_type not in allowed_ops:
            if sql_type == "SELECT":
                 return f"权限拒绝：您的角色 ('{role}') 无权执行查询操作。"
            else:
                 return f"权限拒绝：您的角色 ('{role}') 只能执行查询 (SELECT)，不能执行修改操作 ({sql_type})。"

        return "OK"