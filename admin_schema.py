# ==============================================================================
# 管理后台表单配置 (admin_schema.py)
# 定义每个表在后台管理界面显示的字段、中文标签和输入类型
# ==============================================================================

ADMIN_TABLE_CONFIG = {
    "ProjectCategories": {
        "label": "扶贫项目类别",
        "pk": "CategoryID",
        "columns": [
            # 注意：CategoryID 是自增主键，通常不需要手动输入，除非想强制指定
            {"name": "CategoryName", "label": "类别名称", "type": "text", "placeholder": "例如：水果种植"},
            {"name": "Description", "label": "描述", "type": "text", "placeholder": "项目类别的详细描述"},
        ]
    },
    "Villages": {
        "label": "村镇信息",
        "pk": "VillageID",
        "columns": [
            {"name": "VillageName", "label": "村镇名称", "type": "text", "placeholder": "例如：大河村"},
            {"name": "VillageType", "label": "行政级别", "type": "select", "options": ["镇", "乡", "村"]},
        ]
    },
    "Enterprises": {
        "label": "帮扶企业",
        "pk": "EnterpriseID",
        "columns": [
            {"name": "EnterpriseID", "label": "企业ID", "type": "number", "placeholder": "请输入数字ID"},
            {"name": "EnterpriseName", "label": "企业名称", "type": "text", "placeholder": "例如：恒大集团"},
            {"name": "Principal", "label": "负责人", "type": "text", "placeholder": "企业负责人姓名"},
            {"name": "ContactPhone", "label": "联系电话", "type": "text", "placeholder": "手机或座机"},
            {"name": "PurchaseContent", "label": "采购内容", "type": "text", "placeholder": "例如：苹果、生猪"},
            {"name": "TotalPurchaseAmount", "label": "总采购金额", "type": "number", "placeholder": "单位：元"},
            {"name": "PurchaseProgress", "label": "采购进度(%)", "type": "number", "step": "0.01", "placeholder": "0-100"},
        ]
    },
    "PoorHouseholds": {
        "label": "贫困户信息",
        "pk": "HouseholdID",
        "columns": [
            {"name": "HouseholdName", "label": "户主姓名", "type": "text", "placeholder": "姓名"},
            {"name": "ContactPhone", "label": "联系电话", "type": "text", "placeholder": "电话号码"},
            {"name": "VillageID", "label": "所属村镇ID", "type": "number", "placeholder": "对应的 VillageID"},
            {"name": "IndustryType", "label": "产业类型", "type": "text", "placeholder": "例如：养殖业"},
            {"name": "Scale", "label": "规模", "type": "text", "placeholder": "例如：5亩、10头"},
            {"name": "IncomeStatus", "label": "收入状况", "type": "number", "placeholder": "年收入(元)"},
        ]
    },
    "ResponsiblePersons": {
        "label": "项目负责人",
        "pk": "PersonID",
        "columns": [
            {"name": "PersonName", "label": "姓名", "type": "text", "placeholder": ""},
            {"name": "ContactPhone", "label": "电话", "type": "text", "placeholder": ""},
            {"name": "CategoryID", "label": "负责类别ID", "type": "number", "placeholder": "对应的 CategoryID"},
            {"name": "WorkScope", "label": "工作职责", "type": "text", "placeholder": ""},
        ]
    },
    "PovertyAlleviationProjects": {
        "label": "扶贫项目",
        "pk": "ProjectID",
        "columns": [
            {"name": "ProjectName", "label": "项目名称", "type": "text", "placeholder": ""},
            {"name": "CategoryID", "label": "类别ID", "type": "number", "placeholder": ""},
            {"name": "SupportFunds", "label": "扶持资金", "type": "number", "placeholder": "金额(元)"},
            {"name": "ProjectStatus", "label": "状态", "type": "select", "options": ["筹备中", "进行中", "已完成"]},
        ]
    },
    "Orders": {
        "label": "订单记录",
        "pk": "OrderID",
        "columns": [
            {"name": "CategoryID", "label": "类别ID", "type": "number", "placeholder": ""},
            {"name": "EnterpriseID", "label": "企业ID", "type": "number", "placeholder": ""},
            {"name": "HouseholdID", "label": "农户ID", "type": "number", "placeholder": ""},
            {"name": "Quantity", "label": "数量", "type": "number", "placeholder": ""},
            {"name": "UnitPrice", "label": "单价", "type": "number", "placeholder": ""},
            {"name": "OrderStatus", "label": "订单状态", "type": "number", "placeholder": "1=正常, 0=取消"},
            {"name": "OrderDate", "label": "日期", "type": "date", "placeholder": ""},
        ]
    }
}