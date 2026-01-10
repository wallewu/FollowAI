# MountPoint注册管理功能设计

**更新日期**: 2026-01-10  
**相关文档**: 离散化公共资产仓库技术方案_v2.md

---

## 1. 功能概述

在离散化公共资产仓库系统中，**MountPoint（一级分类）注册管理**是基础设施的核心功能之一。它负责管理公共资产仓库的顶层分类结构，确保所有资产包都挂载到规范、统一的路径下。

### 1.1 核心价值

1. **路径规范化**: 统一管理挂载点路径，避免路径混乱
2. **分类可扩展**: 支持动态添加新的资产分类，无需修改代码
3. **权限控制**: 通过管理端集中管理，防止随意创建分类
4. **数据完整性**: 确保分类与资产包的关联关系正确

### 1.2 设计原则

- **统一挂载**: 同一分类下的所有资产包共享同一个MountPoint
- **路径不可变**: 一旦创建，MountPoint路径不可修改，保证稳定性
- **删除保护**: 有资产包的分类不允许删除，防止数据孤岛
- **自动生成**: MountPoint路径自动生成，格式为`/AssetRepo/{分类名称}/`

---

## 2. 数据库设计

### 2.1 表结构

```sql
CREATE TABLE mount_points (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    mount_point VARCHAR(256) UNIQUE NOT NULL COMMENT '挂载点路径(如/AssetRepo/Scene/)',
    category_name VARCHAR(64) UNIQUE NOT NULL COMMENT '分类名称(如Scene/Character)',
    display_name VARCHAR(128) NOT NULL COMMENT '显示名称(如场景资产/角色资产)',
    description TEXT COMMENT '分类描述',
    icon_url VARCHAR(512) COMMENT '分类图标URL',
    sort_order INT DEFAULT 0 COMMENT '排序权重',
    is_enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    created_by VARCHAR(64) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category_name (category_name),
    INDEX idx_sort_order (sort_order),
    INDEX idx_is_enabled (is_enabled)
) COMMENT='MountPoint一级分类注册表';
```

### 2.2 预置数据

系统预置6个基础分类：

| 分类名称 | 挂载点路径 | 显示名称 | 排序 |
|---------|-----------|---------|------|
| Scene | /AssetRepo/Scene/ | 场景资产 | 1 |
| Character | /AssetRepo/Character/ | 角色资产 | 2 |
| Effect | /AssetRepo/Effect/ | 特效资产 | 3 |
| Audio | /AssetRepo/Audio/ | 音频资产 | 4 |
| UI | /AssetRepo/UI/ | UI资产 | 5 |
| Common | /AssetRepo/Common/ | 通用资产 | 6 |

---

## 3. API接口设计

### 3.1 核心接口列表

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取列表 | GET | /api/v1/mountpoints | 分页查询MountPoint列表 |
| 创建 | POST | /api/v1/mountpoints | 创建新的MountPoint |
| 更新 | PUT | /api/v1/mountpoints/{id} | 更新MountPoint信息 |
| 删除 | DELETE | /api/v1/mountpoints/{id} | 删除MountPoint |
| 获取详情 | GET | /api/v1/mountpoints/{id} | 获取单个MountPoint详情 |
| 获取可用列表 | GET | /api/v1/mountpoints/available | 获取启用的分类列表 |

### 3.2 关键验证逻辑

#### 创建时验证
1. `category_name` 必须唯一，仅支持字母、数字、下划线
2. `mount_point` 自动生成为 `/AssetRepo/{category_name}/`
3. 检查生成的 `mount_point` 是否已存在

#### 更新时限制
1. `category_name` 和 `mount_point` 不允许修改
2. 只能修改 `display_name`、`description`、`icon_url`、`sort_order`、`is_enabled`

#### 删除时检查
1. 查询该分类下是否有资产包（关联 `asset_packages` 表）
2. 如果有资产包，返回错误，要求先迁移或删除资产包
3. 只有空分类才允许删除

---

## 4. 管理端界面设计

### 4.1 MountPoint列表页

**功能**:
- 展示所有MountPoint分类
- 显示每个分类下的资产包数量
- 支持启用/禁用分类
- 支持拖拽排序

**关键字段**:
- 分类名称（英文）
- 显示名称（中文）
- 挂载点路径
- 资产包数量
- 状态（启用/禁用）
- 操作按钮（编辑/删除）

### 4.2 新建/编辑MountPoint页

**表单字段**:
1. **分类名称（英文）**: 必填，用于目录命名，仅支持字母数字下划线
2. **显示名称（中文）**: 必填，用于界面显示
3. **挂载点路径**: 自动生成，不可编辑
4. **分类描述**: 可选，多行文本
5. **分类图标**: 可选，支持选择或上传
6. **排序权重**: 数字，越小越靠前
7. **状态**: 启用/禁用

**验证规则**:
- 分类名称：2-64字符，正则 `^[a-zA-Z0-9_]+$`
- 显示名称：2-128字符
- 挂载点路径：自动生成，格式 `/AssetRepo/{分类名称}/`

### 4.3 MountPoint详情页

**展示内容**:
- 基本信息（分类名称、显示名称、挂载点路径等）
- 统计信息（资产包数量、总资产数、总大小）
- 资产包列表（该分类下的所有资产包）

**操作按钮**:
- 编辑：跳转到编辑页
- 查看资产包：筛选显示该分类下的资产包
- 导出清单：导出该分类下的资产包清单

---

## 5. 与资产包管理的集成

### 5.1 创建资产包时的验证

当创建新资产包时，需要验证：

```javascript
// 伪代码
function createAssetPackage(packageData) {
  // 1. 验证category是否存在
  const mountPoint = await getMountPointByCategory(packageData.category);
  if (!mountPoint) {
    throw new Error(`分类'${packageData.category}'不存在，请先注册MountPoint`);
  }
  
  // 2. 验证MountPoint是否启用
  if (!mountPoint.is_enabled) {
    throw new Error(`分类'${packageData.category}'已禁用`);
  }
  
  // 3. 自动填充mount_point字段
  packageData.mount_point = mountPoint.mount_point;
  
  // 4. 继续创建资产包
  return await saveAssetPackage(packageData);
}
```

### 5.2 资产包列表的分类筛选

在资产包管理界面，提供分类筛选下拉框：

```javascript
// 获取可用分类列表
GET /api/v1/mountpoints/available

// 响应
{
  "data": [
    {"category_name": "Scene", "display_name": "场景资产"},
    {"category_name": "Character", "display_name": "角色资产"},
    ...
  ]
}
```

---

## 6. 客户端使用场景

### 6.1 MOD编辑器集成

MOD编辑器在创建资产包时，需要：

1. **获取可用分类列表**:
```cpp
// 调用API获取分类列表
TArray<FMountPointInfo> Categories = AssetRepoClient->GetAvailableCategories();

// 在UI中展示为下拉框
for (const FMountPointInfo& Category : Categories) {
    ComboBox->AddOption(Category.DisplayName, Category.CategoryName);
}
```

2. **验证分类有效性**:
```cpp
// 用户选择分类后，验证是否有效
bool IsValidCategory(const FString& CategoryName) {
    return AssetRepoClient->IsCategoryEnabled(CategoryName);
}
```

### 6.2 资产包下载

客户端下载资产包时，根据MountPoint挂载：

```cpp
// 下载资产包
FString PakPath = DownloadPak(PakGUID);

// 根据category获取MountPoint
FString MountPoint = GetMountPointByCategory(Package.Category);

// 挂载Pak到指定MountPoint
FPakPlatformFile::Get().Mount(*PakPath, 0, *MountPoint);
```

---

## 7. 实施建议

### 7.1 实施步骤

1. **Phase 1: 数据库和API**（1周）
   - 创建 `mount_points` 表
   - 插入预置数据
   - 实现核心CRUD API
   - 编写单元测试

2. **Phase 2: 管理端界面**（1周）
   - 实现MountPoint列表页
   - 实现新建/编辑页
   - 实现详情页
   - 集成到资产包管理流程

3. **Phase 3: 客户端集成**（3天）
   - 实现客户端API调用
   - 在MOD编辑器中集成分类选择
   - 更新资产包下载和挂载逻辑

### 7.2 测试要点

1. **功能测试**:
   - 创建、更新、删除MountPoint
   - 验证规则是否生效
   - 删除保护是否有效

2. **集成测试**:
   - 创建资产包时的分类验证
   - 资产包列表的分类筛选
   - MOD编辑器的分类选择

3. **边界测试**:
   - 分类名称特殊字符
   - 超长字符串
   - 并发创建相同分类

---

## 8. 注意事项

### 8.1 路径不可变原则

**为什么不允许修改MountPoint路径？**

1. **资产包依赖**: 已发布的资产包的 `mount_point` 字段已固化
2. **客户端缓存**: 客户端可能缓存了MountPoint信息
3. **COS存储结构**: COS上的目录结构已按MountPoint组织

**如果确实需要修改怎么办？**

1. 创建新的MountPoint
2. 逐步迁移资产包到新分类
3. 待所有资产包迁移完成后，删除旧分类

### 8.2 删除保护机制

**为什么不允许删除有资产包的分类？**

1. **数据完整性**: 避免资产包变成孤岛数据
2. **引用完整性**: 其他资产包可能依赖该分类下的资产包
3. **COS清理**: 需要先清理COS上的文件

**正确的删除流程**:

1. 检查该分类下的所有资产包
2. 将资产包迁移到其他分类或删除
3. 确认该分类下无资产包后，才允许删除

### 8.3 扩展性考虑

**未来可能的扩展**:

1. **多级分类**: 支持二级、三级分类（如 `/AssetRepo/Scene/Indoor/`）
2. **权限控制**: 不同用户对不同分类的访问权限
3. **配额管理**: 限制每个分类下的资产包数量或总大小
4. **标签系统**: 为分类添加标签，支持多维度筛选

---

## 9. 总结

MountPoint注册管理功能是离散化公共资产仓库的基础设施，它通过统一管理一级分类，确保了：

1. ✅ **路径规范**: 所有资产包挂载到统一、规范的路径
2. ✅ **可扩展性**: 支持动态添加新分类，无需修改代码
3. ✅ **数据完整性**: 通过验证和保护机制，确保数据关联正确
4. ✅ **易用性**: 通过管理端界面，降低管理成本

这个功能的实现，为后续的资产包管理、依赖管理、发布管理等功能奠定了坚实的基础。
