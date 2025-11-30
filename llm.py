# ==============================================================================
# LLM 客户端模块 (llm.py)
# 负责与阿里云百炼 (DashScope) API 通信
# ==============================================================================
import json
from datetime import datetime as dt_datetime
from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Optional

# 引入 OpenAI SDK
from openai import OpenAI

# 从 config.py 导入配置
from config import DASHSCOPE_API_KEY, MODEL_NAME, TARGET_DB_NAME

# ==============================================================================
# 定义精确的数据库 Schema (保持不变，用于上下文)
# ==============================================================================
DB_SCHEMA_DDL = """
-- 创建项目类别表
CREATE TABLE ProjectCategories (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    CategoryName VARCHAR(50) NOT NULL UNIQUE COMMENT '扶贫种类（手工、水果、养殖等）',
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='扶贫项目类别表';

-- 创建村镇表
CREATE TABLE Villages (
    VillageID INT AUTO_INCREMENT PRIMARY KEY,
    VillageName VARCHAR(100) NOT NULL,
    VillageType ENUM('镇', '乡', '村')  NOT NULL
) COMMENT='村镇基本信息表';

-- 创建企业表
CREATE TABLE Enterprises (
    EnterpriseID INT  PRIMARY KEY COMMENT '企业编号',
    EnterpriseName VARCHAR(200) NOT NULL COMMENT '企业名称',
    Principal VARCHAR(50) NOT NULL COMMENT '企业负责人',
    ContactPhone VARCHAR(20) COMMENT '联系电话',
    PurchaseContent TEXT COMMENT '采购内容',
    TotalPurchaseAmount DECIMAL(12,2) COMMENT '总采购金额',
    PurchaseProgress DECIMAL(5,2) DEFAULT 0.00 COMMENT '采购进度(%)'
) COMMENT='帮扶企业信息表';

-- 创建贫困户表
CREATE TABLE PoorHouseholds (
    HouseholdID INT AUTO_INCREMENT PRIMARY KEY,
    HouseholdName VARCHAR(50) NOT NULL,
    ContactPhone VARCHAR(20),
    VillageID INT NOT NULL,
    IndustryType VARCHAR(50),
    Scale VARCHAR(100),
    IncomeStatus DECIMAL(10,2),
    FOREIGN KEY (VillageID) REFERENCES Villages(VillageID)
) COMMENT='贫困户信息表';

-- 创建负责人表
CREATE TABLE ResponsiblePersons (
    PersonID INT AUTO_INCREMENT PRIMARY KEY,
    PersonName VARCHAR(50) NOT NULL,
    ContactPhone VARCHAR(20),
    CategoryID INT NOT NULL,
    WorkScope TEXT COMMENT '工作范围',
    FOREIGN KEY (CategoryID) REFERENCES ProjectCategories(CategoryID)
) COMMENT='项目负责人信息表';

-- 创建扶贫项目表
CREATE TABLE PovertyAlleviationProjects (
    ProjectID INT AUTO_INCREMENT PRIMARY KEY,
    ProjectName CHAR(20) NOT NULL,
    CategoryID INT NOT NULL,
    SupportFunds DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ProjectStatus ENUM('筹备中', '进行中', '已完成')  NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES ProjectCategories(CategoryID)
) COMMENT='扶贫项目主表';

-- 创建订单表
CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CategoryID INT NOT NULL,
    EnterpriseID INT NOT NULL,
    HouseholdID INT NOT NULL,
    Quantity DECIMAL(10,2) NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    TotalAmount DECIMAL(12,2) AS (Quantity * UnitPrice) STORED,
    OrderStatus INT DEFAULT 1,
    OrderDate DATE NOT NULL, 
    FOREIGN KEY (CategoryID) REFERENCES ProjectCategories(CategoryID),
    FOREIGN KEY (EnterpriseID) REFERENCES Enterprises(EnterpriseID),
    FOREIGN KEY (HouseholdID) REFERENCES PoorHouseholds(HouseholdID)
) COMMENT='订单记录表';
"""

# ==============================================================================
# 通用工具函数
# ==============================================================================
def _datetime_serializer(obj):
    """JSON 序列化辅助函数"""
    if isinstance(obj, (dt_datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# ==============================================================================
# LLM 核心业务逻辑
# ==============================================================================
class LLMClient:
    """阿里云百炼 LLM 客户端，用于SQL生成和报告分析。"""
    
    def __init__(self):
        # 初始化 OpenAI 客户端，配置百炼的 Base URL
        self.client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.schema_info = DB_SCHEMA_DDL

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """调用大模型 API 的通用方法"""
        try:
            completion = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                stream=True,
                temperature=0.5 # 控制随机性
            )
            
            full_content = ""
            for chunk in completion:
                # 检查 chunk 是否有内容
                if chunk.choices and chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            return full_content

        except Exception as e:
            print(f"LLM API 调用失败: {e}")
            return f"Error calling LLM: {e}"

    def generate_sql(self, user_query: str) -> str:
        """根据用户查询和数据库Schema生成SQL语句。"""
        
        available_tables = [
            "ProjectCategories", "Villages", "Enterprises", 
            "PoorHouseholds", "ResponsiblePersons", 
            "PovertyAlleviationProjects", "Orders"
        ]
        table_list_str = ", ".join(available_tables)

        # 提示词：包含之前的所有优化 (细粒度搜索、JOIN约束等)
        system_prompt = f"""
        你是一个专业的SQL转换器。你的任务是将用户的问题转化为一个可以在MySQL数据库上执行的SQL语句。
        
        ## 数据库结构 (SQL DDL)
        {self.schema_info}
        
        ## 核心原则 (必须遵守)
        1. **必须关联名称 (Critical)**: 当查询涉及外键ID（如 EnterpriseID, CategoryID, VillageID）时，**必须**使用 `JOIN` 连接对应的表，并 `SELECT` 出具体的名称字段（如 **EnterpriseName, CategoryName, VillageName**）。禁止只查 ID。
        
        2. **表名约束**: 只能使用以下表名：{table_list_str}。
        
        3. **输出格式**: 仅返回纯 SQL 语句，不要包含 markdown 标记或解释。

        4. **细粒度搜索策略 (Fuzzy Search Strategy)**:
           用户的查询经常涉及具体的农产品或工作内容（如'苹果'、'核桃'、'养牛'），而 `ProjectCategories` 表通常只存储大类（如'种植'、'养殖'）。
           **当用户查询具体事物时，必须使用 `LIKE '%关键词%'` 在以下细化字段中查找：**
           - **查询贫困户具体工作**: 同时检索 `PoorHouseholds.IndustryType` (产业类型) 和 `PoorHouseholds.Scale` (具体规模/工作)。
             * 示例: 搜"种苹果的户"，SQL应包含 `WHERE (ph.IndustryType LIKE '%苹果%' OR ph.Scale LIKE '%苹果%')`
           - **查询负责人具体职责**: 检索 `ResponsiblePersons.WorkScope` (工作范围)。
             * 示例: 搜"管果园的人"，SQL应包含 `WHERE rp.WorkScope LIKE '%果园%'`
           - **查询企业采购明细**: 检索 `Enterprises.PurchaseContent` (采购内容)。
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        sql_statement = self._call_llm(messages)
        
        # 清洗可能存在的 Markdown 标记
        if sql_statement.lower().startswith('```sql'):
            sql_statement = sql_statement.strip().strip('`').replace('sql\n', '').replace('SQL\n', '').strip()
        if sql_statement.lower().startswith('```'):
             sql_statement = sql_statement.strip().strip('`').strip()
            
        return sql_statement

    def generate_report(self, user_query: str, sql_statement: str, db_result: List[Dict[str, Any]], user_role: str = "普通用户") -> str:
        """根据SQL执行结果和用户身份生成分析报告。"""
        
        is_dml = sql_statement.upper().startswith(('INSERT', 'UPDATE', 'DELETE'))
        if is_dml:
            # 对于 DML 操作，db_result 是一个状态字典，检查是否成功
            rows = db_result[0].get('rows_affected', 0) if db_result else 0
            if rows > 0:
                return f"您执行了数据修改操作（{sql_statement.split()[0].upper()}），操作成功完成，影响了 **{rows}** 条记录。"
            else:
                return f"您执行了数据修改操作（{sql_statement.split()[0].upper()}），操作成功，但未影响任何记录（可能条件不匹配）。"
        
        # 【修改点】：移除硬编码的空结果判断，让 LLM 负责处理
        
        # 序列化结果
        # db_result 为空时，result_str 为 '[]'
        result_str = json.dumps(db_result, ensure_ascii=False, indent=2, default=_datetime_serializer)
        
        # 角色定制逻辑 (保持不变)
        role_instructions = ""
        if "贫困户" in user_role:
            role_instructions = """
            - **你的身份**: 贴心的扶贫助手。
            - **用户身份**: 贫困户（农民）。
            - **关注点**: 收入多少、钱有没有到账、自家产品卖得好不好、有没有新的补贴政策。
            - **语气**: 亲切、通俗易懂、鼓励性。把数字转化为用户能懂的“实惠”。
            """
        elif "企业" in user_role:
            role_instructions = """
            - **你的身份**: 专业的商业顾问。
            - **用户身份**: 帮扶企业负责人。
            - **关注点**: 采购规模、供应链稳定性、农产品产量、投资回报、区域分布。
            - **语气**: 专业、干练、客观。
            """
        elif "调查员" in user_role:
            role_instructions = """
            - **你的身份**: 严谨的数据审计员。
            - **用户身份**: 一线扶贫调查员。
            - **关注点**: 数据准确性、异常值、违规情况、资金落实。
            - **语气**: 客观、严肃、注重细节。
            """
        elif "管理员" in user_role:
            role_instructions = """
            - **你的身份**: 全局系统分析师。
            - **用户身份**: 系统超级管理员。
            - **关注点**: 系统整体运行情况、数据总量、宏观趋势。
            - **语气**: 全局视角、概括性强。
            """
        else:
            role_instructions = """- **你的身份**: 数据分析师。- **语气**: 平和、客观。"""

        system_prompt = f"""
        你是一个基于数据库结果生成报告的AI助手。现在请根据**用户的身份**生成一份定制化的分析报告。

        ## 用户信息
        **当前用户身份**: {user_role}
        
        ## 角色定制指南
        {role_instructions}

        ## 原始请求
        {user_query}

        ## 数据库结果 (JSON)
        {result_str}

        ## 通用报告要求 (必须遵守)
        1. **禁止复述 ID**: 绝对不要出现 "EnterpriseID=1" 这种机器语言，必须用**中文名称**代替。如果结果中只有ID，请尝试根据上下文描述。
        2. **深度分析**: 不要只罗列数据，要根据上面的“关注点”进行分析。
        3. **如果结果集为空 (即 JSON 为 [])**: **必须**以该角色的语气和关注点来解释数据缺失的现状。例如，对**贫困户**可以说“您的账户目前没有新的收入记录，请保持关注。”；对**企业**可以说“当前暂无符合条件的采购记录，建议扩大搜索范围或核对时间周期。”
        4. **篇幅**: 控制在 200 字左右。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "请生成这份定制分析报告。"}
        ]
        
        return self._call_llm(messages)