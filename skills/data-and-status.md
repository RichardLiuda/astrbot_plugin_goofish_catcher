# 技能：数据查询与系统状态

**工具组**：`goofish_list_items` / `goofish_get_item_detail` / `goofish_get_overview` / `goofish_check_login` / `goofish_start_login`

## 商品数据库查询

### `goofish_list_items` — 查已缓存商品

查询订阅调度器抓取并存入数据库的历史商品。

| 参数 | 类型 | 说明 |
|------|------|------|
| `search` | string | 标题模糊匹配 |
| `sub_id` | int | 按订阅 ID 过滤，0=不限 |
| `min_price` | float | 最低价，0=不限 |
| `max_price` | float | 最高价，0=不限 |
| `sort_by` | string | `last_seen_at`/`first_seen_at`/`price` |
| `limit` | int | 上限 20 |

**与 `goofish_search_live` 的区别**：
- `goofish_list_items` → 查本地数据库（快，无网络），结果可能不是最新
- `goofish_search_live` → 实时爬取闲鱼（慢，结果最新）

### `goofish_get_item_detail` — 查单个商品详情

```
goofish_get_item_detail(item_id="12345678")
```

返回：基本信息 + 最近 10 条价格历史 + 最近 5 条通知记录 + 订阅关联数

## 系统状态

### `goofish_get_overview`

返回插件运行状态摘要：
- 总订阅数、运行中/暂停数
- 最近 24 小时抓取成功率
- 调度器状态、Provider 类型

适合用户询问「系统状态怎么样」「有几个订阅在跑」等问题。

## 登录管理

### `goofish_check_login`

检查当前闲鱼会话状态。返回值：
- `"ok"` — 会话有效
- `"auth_required"` — 需要重新登录
- `"captcha"` — 遇到验证码
- `"error: ..."` — 其他错误

### `goofish_start_login`

启动登录流程，返回二维码或登录链接供用户扫码/点击。

## 典型场景

**用户询问历史价格**
```
用户：之前抓到的尼康Z9最低多少钱？
LLM：goofish_list_items(search="尼康Z9", sort_by="price", limit=20)
     → 按价格排序展示历史记录
```

**会话失效处理**
```
用户：好像搜不到东西了
LLM：goofish_check_login()
     → 返回 "auth_required"
回复：会话已过期，请点击以下链接重新登录：[goofish_start_login()]
```

**系统概览**
```
用户：现在有几个商品在监控？
LLM：goofish_get_overview()
     → 返回订阅数量、运行状态
```
