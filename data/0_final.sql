-- 设置字符集（完整设置）
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;
SET collation_connection = utf8mb4_unicode_ci;
SET NAMES utf8mb4;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS Society 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE Society;

-- 创建项目类别表
CREATE TABLE ProjectCategories (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    CategoryName VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL UNIQUE COMMENT '扶贫种类（手工、水果、养殖等）',
    Description TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='扶贫项目类别表';

-- 创建村镇表
CREATE TABLE Villages (
    VillageID INT AUTO_INCREMENT PRIMARY KEY,
    VillageName VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    VillageType ENUM('镇', '乡', '村')  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='村镇基本信息表';

-- 创建企业表
CREATE TABLE Enterprises (
    EnterpriseID INT  PRIMARY KEY COMMENT '企业编号',
    EnterpriseName VARCHAR(200) NOT NULL COMMENT '企业名称',
    Principal VARCHAR(50) NOT NULL COMMENT '企业负责人',
    ContactPhone VARCHAR(20) COMMENT '联系电话',
    PurchaseContent TEXT COMMENT '采购内容',
    TotalPurchaseAmount DECIMAL(12,2) COMMENT '总采购金额',
    PurchaseProgress DECIMAL(5,2) DEFAULT 0.00 COMMENT '采购进度(%)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='帮扶企业信息表';

-- 创建贫困户表
CREATE TABLE PoorHouseholds (
    HouseholdID INT AUTO_INCREMENT PRIMARY KEY,
    HouseholdName VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    ContactPhone VARCHAR(20),
    VillageID INT NOT NULL,
    IndustryType VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    Scale VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    IncomeStatus DECIMAL(10,2),
    FOREIGN KEY (VillageID) REFERENCES Villages(VillageID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='贫困户信息表';

-- 创建负责人表
CREATE TABLE ResponsiblePersons (
    PersonID INT AUTO_INCREMENT PRIMARY KEY,
    PersonName VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    ContactPhone VARCHAR(20),
    CategoryID INT NOT NULL,
    WorkScope TEXT COMMENT '工作范围',
    FOREIGN KEY (CategoryID) REFERENCES ProjectCategories(CategoryID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目负责人信息表';

-- 创建扶贫项目表
CREATE TABLE PovertyAlleviationProjects (
    ProjectID INT AUTO_INCREMENT PRIMARY KEY,
    ProjectName CHAR(20) NOT NULL,
    CategoryID INT NOT NULL,
    SupportFunds DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ProjectStatus ENUM('筹备中', '进行中', '已完成')  NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES ProjectCategories(CategoryID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='扶贫项目主表';

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单记录表';


-- 验证表创建
SHOW TABLES;

