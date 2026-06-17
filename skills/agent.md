# 技能：浏览器 Agent

**工具**：`goofish_browser_task`  
**定位**：处理现有固定工具（脚手架）覆盖不到的**复杂、不规则任务**。

典型适用场景：

- 查看某个卖家的其他在售商品
- 判断商品图片里描述的瑕疵是否可见
- 多步页面交互（进详情页 → 看描述 → 收藏）
- 任何需要"真人浏览器操作"才能完成的事

**不适用**（有专用工具）：

| 需求 | 用这个 |
| ---- | ------ |
| 搜索商品 | `goofish_search_live` |
| 管理订阅 | `goofish_*_subscription` |
| 查历史数据 | `goofish_list_items` / `goofish_get_item_detail` |
| 从列表收藏 | 引用回复序号 |

## 工具参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `task` | string | 自然语言描述的任务，例如"打开商品 ID=12345678 的详情页并收藏" |

## Agent 内部流程（ReAct 循环）

每步 LLM 决策一个动作，最多 15 步：

| 动作 | 用途 | 何时用 |
|------|------|--------|
| `navigate` | 跳转 URL（仅限 goofish.com） | 第一步 |
| `extract_items` | **快速提取全页商品**（JSON 拦截→DOM，无 LLM） | 搜索页落地后立即用 |
| `click` | 点击按钮/链接 | 收藏、翻页 |
| `type` | 输入文字 | 填写表单 |
| `scroll` | 上下滚动 | 加载更多内容 |
| `wait` | 等待（0.5~5 秒） | 页面动态加载 |
| `extract` | LLM 从 AX 树提取信息 | 无 `extract_items` 可用时 |
| `done` | 任务完成 | 目标达成 |
| `fail` | 任务失败 | 遇到登录墙/验证码/无法完成 |

## 标准搜索路径（最快，3 步）

```json
步骤1: {"action": "navigate", "url": "https://www.goofish.com/search?q=%E5%B0%BC%E5%BA%B7Z9"}
步骤2: {"action": "extract_items"}          ← 直接返回30件商品JSON，无需读AX树
步骤3: {"action": "done", "result": "..."}
```

**注意**：搜索任务优先用 `goofish_search_live`（无需启动 Chromium，更快）。

## 标准收藏路径

```json
步骤1: {"action": "navigate", "url": "https://www.goofish.com/item?id=123456"}
步骤2: {"action": "click", "target": "收藏", "role": "button"}
步骤3: {"action": "done", "result": "商品已收藏"}
```

## 进度反馈

Agent 执行期间会**实时推送进度消息**：
- `[浏览器] 步骤2: 访问 https://www.goofish.com/search?...`
- `[浏览器] 步骤4: 已提取商品列表`

工具 **同步等待** 结果后返回，LLM 收到实际数据再生成最终回复。

## 并发限制

- 默认最多 3 个 Agent 同时运行（`llm_agent_max_concurrent`）
- 超过上限时工具返回排队等待提示
- 每个 Agent 独立 Chromium 进程，用完即销毁

## 失败代码

| `fail.reason` | 含义 | 处理 |
|---------------|------|------|
| `AUTH_REQUIRED` | 需要登录 | 提示用户 `/闲鱼 登录` |
| `CAPTCHA` | 验证码 | 提示稍后重试 |
| 其他文字 | 任务无法完成 | 告知用户具体原因 |

## 不适用场景

- 搜索商品 → 用 `goofish_search_live`（快 10 倍）
- 查看已缓存商品 → 用 `goofish_list_items`
- 查订阅状态 → 用 `goofish_list_subscriptions`
