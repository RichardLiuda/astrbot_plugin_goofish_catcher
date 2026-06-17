# 技能：搜索商品

**工具**：`goofish_search_live`  
**场景**：用户询问某类商品的闲鱼行情、价格区间，或想看看现有挂单情况。

## 工具参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `keyword` | string | 必填 | 搜索关键词 |
| `pages` | int | 1 | 搜索页数，上限 3 |
| `min_price` | float | 0 | 最低价（元），0=不限 |
| `max_price` | float | 0 | 最高价（元），0=不限 |

## 工具行为

1. 调用 `PlaywrightSearchProvider.search()`（纯脚本，不启动 LLM 循环）
2. 对结果按价格过滤（如有）
3. 用 `context.send_message` 将结果**直接发送**到对话，格式如下：
   ```
   【查询推荐】关键词：尼康Z9
   实时搜索 | 共 28 件 → 展示 20 件
   
   1. [¥12000] 尼康Z9 单机身 成色95新
      价格：¥12000.00
      链接：https://www.goofish.com/item?id=123456
   2. ...
   引用本消息回复序号可收藏，支持 1 或 1 3
   ```
4. 返回给 LLM 的是简短摘要（不重复列表），例如：
   `"已搜索「尼康Z9」，共 28 件，已展示前 20 件。用户可引用消息回复序号收藏。"`

## 典型对话

**用户**：帮我查一下闲鱼上尼康 Z9 的价格  
**LLM 动作**：`goofish_search_live(keyword="尼康Z9")`  
**LLM 回复**：上方是实时搜索结果，共 XX 件。如需收藏，引用上方消息回复序号即可。

---

**用户**：找找 3000 以内的佳能 R8  
**LLM 动作**：`goofish_search_live(keyword="佳能R8", max_price=3000)`

## reply-to-favorite 联动

发出的消息符合 `parse_reply_target` 的解析格式：
- 消息头以 `【查询推荐】` 开头
- 条目格式：`{idx}. [{score}] {title}` + `   链接：{url}`

用户**引用该消息**并回复 `1`、`1 3` 等序号时，`intercept_reply_favorite_before_llm` 会拦截并自动触发收藏，无需再调用工具。

## 注意事项

- **优先用此工具**处理搜索需求，不要用 `goofish_browser_task`（速度慢 10 倍）
- 若返回 `AUTH_REQUIRED`：提示用户 `/闲鱼 登录`
- 若返回 `CAPTCHA`：提示用户稍后重试
- 搜索最多展示 20 条；需要更多可增加 `pages` 参数
