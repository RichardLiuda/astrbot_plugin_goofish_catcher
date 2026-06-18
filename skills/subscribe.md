# 技能：订阅管理

**工具组**：`goofish_list_subscriptions` / `goofish_create_subscription` / `goofish_update_subscription` / `goofish_delete_subscription` / `goofish_pause_subscription` / `goofish_resume_subscription` / `goofish_check_subscription`

**场景**：用户想对某类商品进行长期监控——新品上架或降价时自动推送通知。

## 工具速查

| 工具 | 作用 | 关键参数 |
|------|------|---------|
| `goofish_list_subscriptions` | 查看所有订阅 | `keyword`（关键词过滤）, `status`（all/enabled/paused） |
| `goofish_create_subscription` | 新建订阅 | `keyword`（必填）, `interval_sec`, `pages`, `price_min`, `price_max` |
| `goofish_update_subscription` | 修改订阅 | `sub_id`（必填），只传需改的字段 |
| `goofish_delete_subscription` | 删除订阅 | `sub_id` |
| `goofish_pause_subscription` | 暂停订阅 | `sub_id` |
| `goofish_resume_subscription` | 恢复订阅 | `sub_id` |
| `goofish_check_subscription` | 立即执行一次 | `sub_id` |

## 参数说明

**`goofish_create_subscription` 参数默认值**：
- `interval_sec=0` → 使用系统配置的默认间隔（通常 300 秒）
- `pages=0` → 使用系统默认页数（通常 1）
- `price_min=0`, `price_max=0` → 不限价格

**`goofish_update_subscription` 特殊规则**：
- `-1` = 不修改该字段（仅 price_min/price_max 支持）
- `0` = 清除该限制（price_min/price_max 设为 NULL）
- 不传 keyword/interval_sec/pages 时保持原值

## 人工确认规则

以下三个工具在调用前**必须先向用户确认**，待用户明确回复"确认"/"好"/"是"等肯定词后再执行：

| 工具 | 原因 |
| ---- | ---- |
| `goofish_create_subscription` | 创建持久化监控任务，会消耗系统资源 |
| `goofish_delete_subscription` | 不可逆，同时删除该订阅下所有历史商品记录 |
| `goofish_update_subscription` | 变更现有订阅配置 |

确认格式示例：
```
即将为您创建订阅：关键词「徕卡M11」，价格上限 ¥5000，每 5 分钟检查一次。确认创建吗？
```
```
即将删除订阅 #7（徕卡M11），同时清除其所有历史记录，此操作不可撤销。确认删除吗？
```

`goofish_pause_subscription` / `goofish_resume_subscription` / `goofish_check_subscription` 无需确认（轻量可逆或不改变数据）。

## 典型流程

**新建监控**
```
用户：帮我监控闲鱼上 5000 以内的徕卡M11，有新品就通知我
LLM：即将创建订阅：关键词「徕卡M11」，价格 ≤¥5000，每 5 分钟检查一次。确认创建吗？
用户：确认
LLM：goofish_create_subscription(keyword="徕卡M11", price_max=5000)
回复：已创建订阅 #7，关键词：徕卡M11，价格 ≤¥5000，每 5 分钟检查一次
```

**修改价格上限**
```
用户：把徕卡M11 的监控预算改到 8000
LLM：goofish_list_subscriptions(keyword="徕卡M11")  → 得到 sub_id=7
     即将修改订阅 #7：价格上限 ¥5000 → ¥8000。确认修改吗？
用户：好的
LLM：goofish_update_subscription(sub_id=7, price_max=8000)
```

**临时暂停**
```
用户：先停一下尼康的订阅
LLM：goofish_list_subscriptions(keyword="尼康") → 得到 id
     goofish_pause_subscription(sub_id=...)
```

**立即触发一次检查**
```
用户：现在检查一下订阅 3 有没有新东西
LLM：goofish_check_subscription(sub_id=3)
```

## 触发通知的条件

系统会在以下情况推送通知：
1. **新商品上架**：该商品 `item_id` 之前未见过
2. **价格降低**：同一 `item_id` 价格下降

通知格式同 `【立即检查】`，同样支持引用回复序号收藏。

## 注意事项

- 订阅绑定创建者的 `unified_msg_origin`，只推送给创建人
- 会话过期时订阅会自动暂停（`AUTH_REQUIRED`）；用户登录后可手动 `goofish_resume_subscription` 恢复
- 删除订阅会同时删除该订阅下的所有历史商品记录
