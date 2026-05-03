# AI Native Desktop Companion 重构方案

更新时间：2026-05-02

## 1. 项目新定位

本项目从传统“宠物养成游戏”转向 Windows 桌面陪伴型 AI 宠物。

目标不是让用户打开一个独立 App 反复喂食、洗澡、刷数值，而是在电脑桌面边缘常驻一只像素狗。它会根据用户的电脑使用节奏主动陪伴、表达情绪、提醒休息，并在后续通过 AI 文案和长期记忆形成更自然的陪伴感。

一句话定位：

> 一只趴在电脑边框上的 AI native 像素宠物，根据用户空闲、活跃和时间段变化做出低打扰、高陪伴感的反馈。

## 2. 已确认产品决策

| 决策项 | 当前决定 |
| --- | --- |
| 第一版主平台 | Windows 桌面端 |
| 技术方向 | PySide6 / PyQt 桌面悬浮窗口，优先选择实现简单、稳定的方案 |
| 宠物位置 | 默认屏幕底部/右下角贴边，支持拖拽 |
| 点击穿透 | 第一版不做点击穿透 |
| 数据采集 | 只采集空闲时长、连续活跃时长、时间段 |
| 隐私边界 | 不采集窗口标题、应用名称、文件名、输入内容、浏览内容 |
| AI 可见信息 | 只给 AI 摘要，不给原始桌面信息 |
| 默认性格 | 温柔陪伴型 |
| 性格扩展 | 第一版预留温柔陪伴型、活泼撒娇型、安静守护型 |
| 游戏目标 | 治愈陪伴型，没有强目标，重情绪和陪伴 |
| 动作风格 | 像素风，先用占位帧，未来支持 AI 生成统一风格动作帧 |
| AI API | 使用 DeepSeek API，优先采用 Anthropic API 兼容格式；预留原生 Anthropic Provider 扩展 |

## 3. 不再作为第一阶段主线的内容

以下内容暂时不作为第一版重点：

- 传统喂食、洗澡、数值养成循环
- 独立 Web 版宠物 App
- 小游戏驱动成长
- 完整聊天窗口
- 复杂成就系统
- 采集当前应用、窗口标题、文件名等敏感上下文

旧代码不立即删除，但后续主入口不再基于现有 `main.py` / `ui.py` 的 Pygame 菜单式结构推进。

## 4. 技术架构草案

建议新增以下模块，旧代码逐步迁移或冻结：

```text
companion/
  app.py                 # PySide6 启动入口
  window.py              # 透明置顶宠物窗口、贴边、拖拽
  tray.py                # 系统托盘、菜单、退出
  config.py              # 用户配置
  privacy.py             # AI 可见信息过滤

core/
  pet.py                 # 宠物状态，不再是传统养成数值模型
  mood.py                # 情绪系统
  behavior.py            # 行为决策
  memory.py              # 本地陪伴记忆
  events.py              # 用户活动事件定义

activity/
  windows_idle.py        # Windows GetLastInputInfo 空闲检测
  session_tracker.py     # 连续活跃、空闲恢复、时间段判断

animation/
  animator.py            # 动画状态机
  actions.py             # 动作定义、优先级、可中断规则
  sprites.py             # 像素帧加载

ai/
  client.py              # AI Provider 抽象
  deepseek_provider.py   # DeepSeek Anthropic-compatible Provider
  anthropic_provider.py  # 原生 Anthropic Provider，后续可选
  prompts.py             # 隐私摘要提示词
  fallback.py            # 本地模板文案

assets/
  sprites/
    dog/
      idle_lie/
      sleep/
      wake_up/
      tail_wag/
      nudge/
      stretch/
      concerned/
      happy_bounce/

data/
  config.json
  memory.json
```

## 5. 第一版交互闭环

MVP 需要先跑通这个闭环：

1. 启动一个 Windows 桌面悬浮宠物窗口。
2. 窗口透明、无边框、置顶。
3. 宠物默认吸附在屏幕右下角或底部边缘。
4. 用户可以拖拽宠物位置。
5. 支持右键菜单退出、切换设置。
6. 本地检测空闲时长、连续活跃时长、当前时间段。
7. 行为引擎根据活动状态选择动作。
8. 动画系统播放对应像素动作。
9. 文案系统低频显示一句短气泡。
10. AI 文案可选启用；未启用时使用本地模板。

## 6. 行为规则 MVP

第一阶段先用本地规则决定行为，不让大模型直接控制游戏主循环。

| 用户状态 | 宠物行为 |
| --- | --- |
| 空闲 < 60 秒 | `idle_lie` / `look_around` |
| 连续活跃 >= 25 分钟 | 低概率 `stretch` / `look_around` |
| 连续活跃 >= 45 分钟 | `nudge` + 温柔提醒 |
| 连续活跃 >= 90 分钟 | `concerned` + 更明确休息建议 |
| 空闲 >= 5 分钟 | `sit_wait` |
| 空闲 >= 15 分钟 | `sleep` |
| 从空闲 >= 5 分钟后回来 | `wake_up` + `tail_wag` |
| 深夜 23:00-06:00 且连续活跃 >= 30 分钟 | `concerned` + 深夜陪伴文案 |

提醒去重建议：

- 同类提醒 30 分钟内不重复。
- 温柔陪伴型默认低打扰。
- 气泡文案尽量一行内完成。

## 7. 第一批动作清单

第一版先实现 8 到 12 个动作，素材可用占位帧，后续用 AI 统一生成像素动作帧。

| 动作 ID | 说明 | 触发场景 |
| --- | --- | --- |
| `idle_lie` | 趴在屏幕边框上 | 默认状态 |
| `tail_wag` | 轻微摇尾巴 | 用户回来、单击互动 |
| `sleep` | 睡着 | 用户长时间空闲 |
| `wake_up` | 醒来 | 用户从空闲回来 |
| `stretch` | 伸懒腰 | 连续陪伴或工作一段时间 |
| `look_around` | 左右观察 | 普通待机 |
| `nudge` | 轻提醒 | 工作 45 分钟 |
| `concerned` | 担心/关切 | 深夜或超长工作 |
| `happy_bounce` | 开心小跳 | 用户完成一段专注 |
| `peek` | 从边缘探头 | 轻度吸引注意 |
| `walk_edge` | 沿屏幕边缘移动 | 自主活动 |
| `sit_wait` | 安静等待 | 用户短时间离开 |

动作系统需要支持：

- 动作优先级
- 是否可打断
- 一次性动作与循环动作
- 动作结束后回到默认状态
- 后续接入 sprite sheet 或 AI 生成帧

## 8. AI 接入方案

### 8.1 Provider 设计

代码层不直接绑定某一家模型厂商，使用统一接口：

```text
AIProvider.generate_companion_line(context_summary) -> str
```

第一阶段实现：

- `DeepSeekProvider`：主 Provider。
- `FallbackProvider`：本地模板，永远可用。

预留：

- `AnthropicProvider`：后续可接原生 Anthropic API。

### 8.2 DeepSeek 接入方式

根据 DeepSeek 官方文档，DeepSeek API 支持 OpenAI / Anthropic 兼容格式。项目优先使用 Anthropic API 兼容格式，便于未来和 Anthropic SDK 生态对齐。

建议配置：

```text
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_API_KEY=${DEEPSEEK_API_KEY}
```

模型名使用 DeepSeek 当前文档中的可用模型，后续实现前再以官方文档为准确认最终默认值。

注意：

- DeepSeek 的 Anthropic 兼容 API 并不等同于原生 Anthropic API 全功能。
- 部分 Anthropic 字段会被忽略或不支持。
- 第一版只需要简单文本生成，不依赖图像、文档、server tool、web search 等高级能力。

### 8.3 AI 可见信息

AI 只接收隐私摘要，例如：

```text
用户连续活跃 52 分钟。
用户刚从 18 分钟空闲回来。
当前是深夜。
宠物性格是温柔陪伴型。
当前动作是 concerned。
```

AI 不接收：

- 当前窗口标题
- 当前应用名称
- 文件路径
- 文件名
- 键盘输入内容
- 浏览器页面内容
- 聊天内容

### 8.4 AI 文案默认策略

建议第一版：

- AI 文案默认关闭。
- 设置页允许用户手动开启。
- 即使开启，也只发送隐私摘要。
- 网络失败、额度不足、超时均回退到本地模板。

## 9. 旧代码保留与冻结建议

### 可保留思路

- `dog.py` 中性格、状态、情绪变化的部分概念。
- `interaction/emotion.py` 的情绪系统思路。
- `assets/images/pixel_dogs/` 中已有像素资源。
- 部分文案和宠物反馈思路。

### 暂时冻结

- `app.py` Web 版。
- `templates/index.html` 和 `static/game.js`。
- `ui.py` 中大菜单式 Pygame UI。
- `main.py` 中传统 Pygame 主循环。
- `minigames/` 小游戏模块。

冻结不等于删除。第一阶段先新建桌面陪伴主线，等新架构稳定后再决定迁移或移除旧模块。

## 10. 第一阶段实施计划

### Phase 1：桌面壳

- 引入 PySide6。
- 新建透明、无边框、置顶窗口。
- 默认贴屏幕右下角。
- 支持拖拽和吸附。
- 支持右键菜单退出。

### Phase 2：用户活动检测

- Windows 空闲检测。
- 连续活跃时长统计。
- 从空闲恢复事件。
- 时间段判断。

### Phase 3：行为引擎

- 定义用户活动事件。
- 定义宠物动作事件。
- 根据规则选择动作。
- 加提醒去重和冷却。

### Phase 4：动画系统

- 定义动作状态机。
- 使用占位像素帧。
- 支持循环动作和一次性动作。
- 接入 8 到 12 个 MVP 动作。

### Phase 5：文案系统

- 本地模板文案。
- 气泡显示。
- AI Provider 抽象。
- DeepSeek Anthropic-compatible Provider。
- AI 开关和失败回退。

## 11. 待继续讨论

以下问题后续实现前还需要确认：

1. PySide6 还是 PyQt6：当前建议 PySide6。
2. 默认贴边位置：右下角还是底部中央。
3. 气泡文字样式：是否只显示一行，是否自动消失。
4. 设置入口：只做托盘菜单，还是做小设置窗口。
5. AI 文案是否保持默认关闭。
6. 第一批占位动作是用现有像素图变换，还是生成简单程序化占位帧。
7. DeepSeek 默认模型名在实现时最终选择哪个。
8. 是否需要开机启动，第一版是否做。
9. 是否需要本地长期记忆，第一版是否只记录最近一次提醒和偏好。

## 12. 官方资料引用

- DeepSeek API 首次调用文档：https://api-docs.deepseek.com/zh-cn/
- DeepSeek Anthropic API 兼容文档：https://api-docs.deepseek.com/zh-cn/guides/anthropic_api
- DeepSeek Coding Agents 接入文档：https://api-docs.deepseek.com/zh-cn/guides/coding_agents

