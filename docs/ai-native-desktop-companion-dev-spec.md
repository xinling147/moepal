# AI Native Desktop Companion 开发规格

更新时间：2026-05-02

本文档用于把前期技术方案拆成可执行、可派发、可验收的开发规格。它不是产品宣传文档，而是后续开发任务的统一依据。

## 1. 目标定义

### 1.1 一句话目标

将当前项目重构为 Windows 桌面陪伴型 AI native 像素宠物：一只默认贴在屏幕右下角或底部边缘的像素狗，会根据用户空闲、活跃、时间段和自身性格主动行动、表达情绪，并用低打扰方式提供陪伴反馈。

### 1.2 第一版必须成立的体验闭环

第一版只要求跑通以下闭环：

1. 用户启动程序。
2. 桌面出现一个透明、置顶、无边框的像素宠物窗口。
3. 宠物默认贴在屏幕右下角边缘。
4. 用户可以拖拽宠物位置。
5. 程序本地统计用户空闲时长、连续活跃时长、当前时间段。
6. 行为引擎根据活动状态选择宠物动作。
7. 动画系统播放对应像素动作帧。
8. 文案系统低频显示一句短气泡。
9. 未开启 AI 时使用本地模板文案。
10. 开启 AI 时只把隐私摘要发送给 DeepSeek Anthropic-compatible API，失败时回退到本地模板。

### 1.3 第一版明确不做

以下内容不进入第一版，除非后续重新确认：

- 不做传统养成数值主线，例如喂食、洗澡、金币、等级成长。
- 不做完整聊天窗口。
- 不做 Web 版主入口。
- 不做小游戏驱动成长。
- 不采集窗口标题、应用名称、文件名、键盘输入、浏览器内容、聊天内容。
- 不做点击穿透。
- 不做跨平台，第一版只支持 Windows。
- 不要求正式像素素材全部完成，允许占位帧。

## 2. 技术决策

| 决策项 | 第一版口径 |
| --- | --- |
| 桌面框架 | PySide6 |
| 主平台 | Windows 10/11 |
| 渲染方式 | QLabel / QWidget 显示透明背景 PNG 或 QPixmap 帧动画 |
| 窗口形态 | 透明、无边框、置顶、可拖拽 |
| 默认位置 | 主屏幕右下角贴边，保留 16px 屏幕边距 |
| 点击穿透 | 不支持 |
| 系统托盘 | 支持退出、显示/隐藏、设置入口 |
| 活动检测 | Windows `GetLastInputInfo` |
| AI Provider | DeepSeek Provider 优先，使用 Anthropic-compatible 调用形式 |
| AI 默认状态 | 默认关闭，由用户手动开启 |
| AI 失败策略 | 超时、异常、额度不足时回退本地模板 |
| 默认性格 | 温柔陪伴型 |
| 资源策略 | 先占位像素动作帧，后续替换为 AI 生成统一风格素材 |

除非用户明确变更，后续开发以本表为准。

## 3. 目录结构

建议新增 `companion_app/` 作为新主线，避免和旧 Pygame/Web 代码互相污染。

```text
companion_app/
  __init__.py
  main.py
  window.py
  tray.py
  config.py
  paths.py
  privacy.py

  core/
    __init__.py
    events.py
    pet_state.py
    mood.py
    behavior.py
    cooldown.py

  activity/
    __init__.py
    windows_idle.py
    session_tracker.py

  animation/
    __init__.py
    actions.py
    animator.py
    sprites.py

  ai/
    __init__.py
    provider.py
    deepseek_provider.py
    fallback_provider.py
    prompts.py

assets/
  sprites/
    dog/
      idle_lie/
      tail_wag/
      sleep/
      wake_up/
      stretch/
      look_around/
      nudge/
      concerned/
      happy_bounce/
      peek/
      walk_edge/
      sit_wait/

data/
  config.json
  memory.json
```

旧代码处理口径：

- `main.py`、`ui.py`、`dog.py`、`app.py` 暂不删除。
- 新入口必须放在 `companion_app/main.py`。
- 第一阶段不要求兼容旧 Pygame 主循环。
- 可复用旧代码中的概念，但不要直接把旧 UI 状态耦合进新架构。

## 4. 模块规格

### 4.1 桌面窗口模块

负责人范围：`companion_app/window.py`

职责：

- 创建透明、无边框、置顶窗口。
- 显示当前动画帧。
- 支持鼠标拖拽。
- 拖拽结束后自动吸附到最近屏幕边缘。
- 支持气泡文案显示与自动消失。

必须提供的接口：

```python
class PetWindow:
    def set_frame(self, pixmap) -> None: ...
    def show_bubble(self, text: str, ttl_ms: int = 6000) -> None: ...
    def move_to_default_position(self) -> None: ...
    def snap_to_nearest_edge(self) -> None: ...
```

实现约束：

- 窗口背景必须透明。
- 宠物自身区域可以接收鼠标事件。
- 不启用点击穿透。
- 气泡最多显示两行，超过长度由文案层截断。
- 窗口尺寸由当前动作帧最大尺寸决定，第一版固定为 128x128 或 160x160 二选一。默认建议 128x128。

验收标准：

- 启动后宠物出现在主屏幕右下角。
- 拖动时窗口跟随鼠标移动。
- 松开鼠标后窗口贴到最近屏幕边缘。
- 关闭主窗口不会导致后台进程残留；托盘退出能结束进程。

### 4.2 系统托盘模块

负责人范围：`companion_app/tray.py`

职责：

- 提供系统托盘图标。
- 提供右键菜单。
- 执行退出、显示/隐藏、打开设置操作。

第一版菜单项：

```text
显示/隐藏宠物
设置
退出
```

设置第一版可以是简单窗口，也可以先使用托盘子菜单。若实现设置窗口，必须只包含已支持功能，不能出现无效开关。

验收标准：

- 托盘菜单可以退出程序。
- 显示/隐藏不会重置宠物状态。
- 设置入口存在；未完成的设置项不得显示为可操作功能。

### 4.3 配置模块

负责人范围：`companion_app/config.py`、`companion_app/paths.py`

职责：

- 读取和保存用户配置。
- 提供默认配置。
- 管理数据目录路径。

配置结构：

```json
{
  "personality": "gentle",
  "ai_enabled": false,
  "ai_provider": "deepseek",
  "pet_size": 128,
  "bubble_enabled": true,
  "start_on_boot": false,
  "last_position": null
}
```

字段口径：

- `personality` 允许值：`gentle`、`lively`、`quiet`。
- `ai_enabled` 默认 `false`。
- `ai_provider` 第一版只允许 `deepseek`，但接口保留 provider 扩展能力。
- `pet_size` 第一版允许 `128` 或 `160`。
- `start_on_boot` 第一版可以保存配置，但不要求实现开机启动。
- `last_position` 为 `null` 或 `{ "x": int, "y": int }`。

验收标准：

- 配置文件不存在时能用默认配置启动。
- 配置文件损坏时能回退默认配置，并保留错误日志。
- 不把 API Key 写入配置文件。

### 4.4 活动检测模块

负责人范围：`companion_app/activity/windows_idle.py`、`companion_app/activity/session_tracker.py`

职责：

- 读取 Windows 最近输入时间。
- 计算当前空闲时长。
- 计算连续活跃时长。
- 识别从空闲返回事件。
- 识别当前时间段。

数据结构：

```python
@dataclass(frozen=True)
class ActivitySnapshot:
    idle_seconds: int
    active_seconds: int
    returned_from_idle_seconds: int | None
    time_bucket: str
    timestamp: datetime
```

`time_bucket` 允许值：

```text
morning      06:00-11:59
afternoon    12:00-17:59
evening      18:00-22:59
late_night   23:00-05:59
```

事件结构：

```python
@dataclass(frozen=True)
class ActivityEvent:
    type: str
    snapshot: ActivitySnapshot
```

第一版事件类型：

```text
active_tick
idle_5m
idle_15m
return_from_idle
long_active_25m
long_active_45m
long_active_90m
late_night_active
```

实现约束：

- 采样间隔默认 5 秒。
- 不读取当前窗口标题。
- 不读取进程列表。
- 不记录键盘或鼠标具体输入。
- `returned_from_idle_seconds` 只在刚从空闲返回时有值，其余为 `None`。

验收标准：

- 连续操作电脑时 `active_seconds` 递增。
- 电脑空闲超过 5 分钟后产生 `idle_5m`。
- 电脑空闲超过 15 分钟后产生 `idle_15m`。
- 从 5 分钟以上空闲返回后产生 `return_from_idle`。
- 深夜连续活跃超过 30 分钟可产生 `late_night_active`。

### 4.5 宠物状态模块

负责人范围：`companion_app/core/pet_state.py`、`companion_app/core/mood.py`

职责：

- 保存宠物当前性格、情绪、当前动作。
- 根据事件轻量更新情绪。
- 为行为引擎提供状态输入。

第一版状态结构：

```python
@dataclass
class PetState:
    personality: str
    mood: str
    current_action: str
    last_interaction_at: datetime | None
```

`mood` 允许值：

```text
calm
happy
sleepy
concerned
curious
```

验收标准：

- 默认性格为 `gentle`。
- 默认情绪为 `calm`。
- 空闲较久后情绪可以变为 `sleepy`。
- 用户返回后情绪可以变为 `happy`。
- 长时间工作或深夜工作时情绪可以变为 `concerned`。

### 4.6 行为引擎模块

负责人范围：`companion_app/core/behavior.py`、`companion_app/core/cooldown.py`

职责：

- 接收 `ActivityEvent` 和 `PetState`。
- 选择下一步宠物动作。
- 决定是否需要显示文案。
- 处理动作优先级和冷却。

输出结构：

```python
@dataclass(frozen=True)
class BehaviorDecision:
    action_id: str
    should_speak: bool
    speech_intent: str | None
    priority: int
```

第一版规则：

| 条件 | 动作 | 文案意图 | 优先级 |
| --- | --- | --- | --- |
| 默认待机 | `idle_lie` 或 `look_around` | 无 | 10 |
| 连续活跃 >= 25 分钟 | `stretch` | 可选 `soft_checkin` | 20 |
| 连续活跃 >= 45 分钟 | `nudge` | `rest_reminder` | 50 |
| 连续活跃 >= 90 分钟 | `concerned` | `strong_rest_reminder` | 70 |
| 空闲 >= 5 分钟 | `sit_wait` | 无 | 30 |
| 空闲 >= 15 分钟 | `sleep` | 无 | 40 |
| 从空闲 >= 5 分钟返回 | `wake_up` 后接 `tail_wag` | `welcome_back` | 80 |
| 深夜且连续活跃 >= 30 分钟 | `concerned` | `late_night_care` | 75 |

冷却规则：

- 同一 `speech_intent` 30 分钟内不重复。
- `strong_rest_reminder` 60 分钟内不重复。
- `welcome_back` 5 分钟内不重复。
- 高优先级动作可以打断低优先级循环动作。
- 一次性动作结束后必须回到合适的循环动作。

验收标准：

- 连续活跃 45 分钟时能触发轻提醒。
- 连续活跃 90 分钟时不会频繁重复刷屏。
- 用户从空闲返回时优先播放欢迎动作。
- 行为引擎不直接调用 UI，不直接调用 AI。

### 4.7 动画模块

负责人范围：`companion_app/animation/actions.py`、`companion_app/animation/animator.py`、`companion_app/animation/sprites.py`

职责：

- 加载动作帧。
- 管理当前动作播放进度。
- 支持循环动作和一次性动作。
- 向窗口输出当前帧。

动作定义：

```python
@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    loop: bool
    interruptible: bool
    fps: int
    fallback_action_id: str
```

第一版动作清单：

```text
idle_lie
tail_wag
sleep
wake_up
stretch
look_around
nudge
concerned
happy_bounce
peek
walk_edge
sit_wait
```

资源约定：

```text
assets/sprites/dog/{action_id}/frame_000.png
assets/sprites/dog/{action_id}/frame_001.png
```

占位帧规则：

- 如果某个动作资源不存在，加载 `idle_lie`。
- 如果 `idle_lie` 也不存在，使用程序生成的简单占位图。
- 资源缺失不能导致程序崩溃。

验收标准：

- 所有 12 个动作 ID 都能被行为引擎引用。
- 缺少素材时程序仍能启动。
- 一次性动作播放结束后回到 `idle_lie` 或行为引擎指定的循环动作。

### 4.8 文案模块

负责人范围：`companion_app/ai/fallback_provider.py`、`companion_app/ai/prompts.py`

职责：

- 根据 `speech_intent` 和隐私摘要生成一句短文案。
- AI 关闭或失败时使用本地模板。
- 控制文案长度和语气。

本地模板示例：

```python
{
    "welcome_back": ["你回来啦，我刚才有好好等你。"],
    "rest_reminder": ["已经忙了一会儿了，要不要伸个懒腰？"],
    "strong_rest_reminder": ["我有点担心你，先休息几分钟吧。"],
    "late_night_care": ["已经很晚了，我陪你，但也想你早点休息。"],
    "soft_checkin": ["我在旁边，慢慢来。"]
}
```

文案约束：

- 单条文案不超过 28 个中文字符。
- 不使用命令式、责备式语气。
- 不提具体应用、文件、网页或工作内容。
- 不编造用户正在做什么。

验收标准：

- 每个 `speech_intent` 都有本地模板。
- 文案过长时能截断或重新选择短文案。
- AI 关闭时不发生网络请求。

### 4.9 AI Provider 模块

负责人范围：`companion_app/ai/provider.py`、`companion_app/ai/deepseek_provider.py`

职责：

- 定义统一 AI Provider 接口。
- 实现 DeepSeek Anthropic-compatible Provider。
- 处理超时、异常和回退。

Provider 接口：

```python
class AIProvider(Protocol):
    def generate_companion_line(
        self,
        context: "PrivacyContext",
        speech_intent: str,
        timeout_seconds: int = 8,
    ) -> str:
        ...
```

隐私上下文：

```python
@dataclass(frozen=True)
class PrivacyContext:
    active_minutes: int
    idle_minutes: int
    returned_from_idle_minutes: int | None
    time_bucket: str
    personality: str
    mood: str
    action_id: str
```

允许发送给 AI 的字段：

- 连续活跃分钟数。
- 当前空闲分钟数。
- 刚从几分钟空闲返回。
- 当前时间段。
- 宠物性格。
- 宠物情绪。
- 当前动作 ID。
- 文案意图。

禁止发送给 AI 的字段：

- 应用名。
- 窗口标题。
- 文件路径。
- 文件名。
- 输入内容。
- 浏览器页面内容。
- 聊天内容。
- 截图。

环境变量：

```text
DEEPSEEK_API_KEY=...
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
```

实现约束：

- API Key 只从环境变量读取。
- 默认模型名在实现时必须重新核对 DeepSeek 官方文档。
- 请求超时默认 8 秒。
- 失败时不得弹错误窗口打扰用户，只记录日志并回退本地模板。
- 第一版不使用 tools、web search、文件上传、多模态输入。

验收标准：

- `ai_enabled=false` 时不会调用 DeepSeek。
- API Key 缺失时自动回退本地模板。
- DeepSeek 请求失败时程序不中断。
- AI 请求内容不包含禁止字段。

### 4.10 隐私过滤模块

负责人范围：`companion_app/privacy.py`

职责：

- 从内部状态生成 AI 可见摘要。
- 阻止敏感字段进入 AI Provider。
- 为测试提供可检查的上下文对象。

必须提供的接口：

```python
def build_privacy_context(
    snapshot: ActivitySnapshot,
    pet_state: PetState,
    action_id: str,
) -> PrivacyContext:
    ...
```

验收标准：

- 单元测试覆盖所有允许字段。
- 单元测试确认禁止字段不存在。
- AI Provider 只能接收 `PrivacyContext`，不能接收原始系统状态对象。

## 5. 主循环规格

主循环建议由 Qt Timer 驱动，避免引入独立游戏循环。

默认节奏：

```text
activity_timer: 5s
animation_timer: 100ms
behavior_tick: 5s，跟 activity_timer 合并即可
bubble_ttl: 6s
```

启动顺序：

1. 加载配置。
2. 初始化 `PetState`。
3. 初始化 `SessionTracker`。
4. 初始化 `BehaviorEngine`。
5. 初始化 `Animator`。
6. 初始化 `PetWindow`。
7. 初始化系统托盘。
8. 启动 Qt timers。

主循环禁止事项：

- 不在 UI 线程执行长时间网络请求。
- 不在动画 tick 中访问 AI。
- 不在活动检测中读敏感系统信息。
- 不因资源缺失或 AI 失败退出程序。

## 6. 第一阶段任务拆分

### 6.1 派发原则

所有 MVP 任务默认遵守以下规则：

- 任务实现必须限制在该任务声明的范围内。
- 如果需要修改范围外文件，必须先说明原因。
- 每个任务完成后必须至少提供运行方式或测试方式。
- 新增公共接口时必须写清楚调用方和返回值。
- 涉及隐私、AI、系统 API 的任务必须有失败回退。
- 不允许为了临时跑通而绕过 `PrivacyContext` 直接把系统状态传给 AI。
- 不允许在新主线里继续扩大旧 Pygame/Web 架构。

### 6.2 任务依赖关系

```text
MVP-001
  -> MVP-002
  -> MVP-003
  -> MVP-004
      -> MVP-011

MVP-005
  -> MVP-006
      -> MVP-007
      -> MVP-008
      -> MVP-009
          -> MVP-010

MVP-012 依赖 MVP-001 到 MVP-011 的实际完成情况。
```

可并行任务：

- `MVP-003` 可以和 `MVP-005` 并行。
- `MVP-004` 可以和 `MVP-007` 并行。
- `MVP-008` 可以在 `MVP-006` 接口稳定后并行。
- `MVP-009` 可以在 `ActivitySnapshot` 和 `PetState` 稳定后并行。

不可提前做的任务：

- `MVP-010` 不应早于 `MVP-009`，否则容易绕过隐私上下文。
- `MVP-011` 不应早于 `MVP-004`，否则设置无法持久化。
- `MVP-012` 不应早于核心入口稳定。

### 6.3 通用完成标准

每个开发任务完成时都需要满足：

- 代码可以被导入，不产生语法错误。
- 新增逻辑有最小验证，优先单元测试；桌面窗口类任务可以用手动验收记录。
- 不引入与任务无关的大重构。
- 不删除旧文件，除非任务明确要求。
- 不把密钥、用户隐私、机器路径写入仓库。
- 文档中的运行命令和实际入口一致。

### 6.4 协作角色分工

本项目后续采用 Lead Reviewer + Claude Code Worker 的协作方式。

Lead Reviewer 职责：

- 负责最终架构判断。
- 负责核心模块设计和高风险代码攻坚。
- 负责任务拆分、验收、打回和最终合并判断。
- 负责检查 Claude Code 的实现是否越界。
- 负责隐私、AI、行为引擎、活动检测等高风险链路的最终质量。
- 负责确认测试通过不代表无问题，只代表进入人工复核阶段。

Claude Code Worker 职责：

- 只执行被明确派发的任务。
- 只修改任务允许范围内的文件。
- 为自己实现的逻辑补充测试。
- 提供实际运行过的命令和结果。
- 不自行扩大范围。
- 不自行修改隐私策略、AI 可见字段、主架构边界。

默认任务归属：

| 任务 | 默认归属 | 原因 |
| --- | --- | --- |
| MVP-001 | Claude Code Worker | 应用骨架，风险可控 |
| MVP-002 | Claude Code Worker，Lead 复核 | PySide6 窗口细节较多，但风险主要在体验 |
| MVP-003 | Claude Code Worker | 托盘功能边界明确 |
| MVP-004 | Claude Code Worker，Lead 复核 | 配置读写简单，但涉及密钥边界 |
| MVP-005 | Lead Reviewer 主导 | Windows 活动检测和隐私边界是核心 |
| MVP-006 | Lead Reviewer 主导 | 行为引擎决定产品气质和后续可扩展性 |
| MVP-007 | Claude Code Worker | 动画和占位资源可独立实现 |
| MVP-008 | Claude Code Worker，Lead 复核 | 文案体验需要最终把关 |
| MVP-009 | Lead Reviewer 主导 | 隐私上下文是 AI 安全边界 |
| MVP-010 | Lead Reviewer 主导 | AI Provider 涉及外部 API、密钥、超时和回退 |
| MVP-011 | Claude Code Worker，Lead 复核 | 设置入口可按既定配置接口实现 |
| MVP-012 | Claude Code Worker，Lead 复核 | 文档和运行说明，但需确认不误导 |

如需调整归属，必须先更新本表或在任务派发时明确覆盖。

### 6.5 Claude Code 任务交付协议

每次派发给 Claude Code 的任务必须包含：

```text
任务编号：
目标：
允许修改文件：
禁止修改文件：
必须实现的接口：
必须补充的测试：
必须运行的命令：
手动验收项：
完成后必须汇报的内容：
```

Claude Code 完成后必须返回：

```text
完成的任务编号
实际修改文件列表
新增/修改的接口
新增/修改的测试
实际运行的命令
命令结果摘要
未完成或不确定的点
是否修改了任务范围外文件
```

如果 Claude Code 没有提供上述内容，默认视为不可验收，需要打回补充。

### 6.6 测试门禁

所有代码任务至少需要通过以下基础门禁：

```powershell
python -m py_compile companion_app/**/*.py
python -m pytest tests
```

如果 PowerShell 的 `**` 通配不可用，使用等价命令检查全部 Python 文件。

涉及不同模块时的额外门禁：

| 模块 | 必须验证 |
| --- | --- |
| 配置 | 默认配置、损坏配置、保存后读取 |
| 活动检测 | mock idle seconds，不依赖真实等待 5/15/45/90 分钟 |
| 行为引擎 | 人工构造快照验证动作和冷却 |
| 动画 | 资源缺失 fallback |
| 文案 | 每个 `speech_intent` 有可用模板，长度受控 |
| 隐私 | `PrivacyContext` 不包含禁止字段 |
| AI Provider | mock 网络请求，禁止真实调用外部 API |
| 窗口/托盘 | 至少提供手动验收记录 |

禁止把真实 DeepSeek 请求作为自动测试依赖。外部 API 只能在手动验证或集成验证中使用，并且必须由用户显式提供环境变量。

### 6.7 打回重写标准

出现以下任一情况，直接打回 Claude Code 重写或补齐，不进入合并：

- 未运行指定测试。
- 测试失败。
- 没有测试，但任务属于可单元测试模块。
- 修改了任务范围外文件且未说明理由。
- 删除或重写旧代码，且任务没有要求。
- 引入新依赖但未说明必要性。
- 把 API Key、机器路径、用户隐私写入代码或配置。
- AI Provider 接收了 `PrivacyContext` 以外的原始状态对象。
- AI 请求中包含窗口标题、应用名、文件名、输入内容、网页内容、截图。
- 网络失败、资源缺失或配置损坏会导致程序崩溃。
- 在 UI 线程执行阻塞网络请求。
- 行为引擎直接调用 UI 或 AI。
- 为了通过测试而跳过核心逻辑。
- 文档中的运行命令和实际代码入口不一致。

测试通过后仍必须人工复核：

- 架构边界是否被破坏。
- 模块职责是否混杂。
- 是否出现隐私策略倒退。
- 是否存在体验上的高打扰行为。
- 是否留下后续难以清理的临时实现。

### 6.8 Lead Reviewer 优先攻坚范围

以下内容默认不交给 Claude Code 独立决定：

- `ActivitySnapshot` / `ActivityEvent` 的字段设计。
- `BehaviorDecision` 的字段设计和优先级规则。
- `PrivacyContext` 的字段设计。
- AI 可见信息白名单。
- DeepSeek Provider 的请求边界、超时和回退策略。
- 是否引入新依赖。
- 是否迁移或删除旧代码。
- 是否改变第一版产品闭环。

Claude Code 可以实现这些模块中的局部函数，但必须在 Lead Reviewer 已经给出接口、测试要求和验收标准后执行。

### MVP-001 新建 PySide6 应用骨架

范围：

- 新增 `companion_app/main.py`。
- 新增基础 QApplication 启动逻辑。
- 新增空白透明窗口。

验收：

- 运行新入口能看到透明宠物窗口。
- 关闭/退出后进程结束。

### MVP-002 桌面宠物窗口

范围：

- 实现无边框、置顶、透明窗口。
- 实现默认右下角贴边。
- 实现拖拽与松手吸附。

验收：

- 可拖拽。
- 松手贴边。
- 不点击穿透。

### MVP-003 系统托盘

范围：

- 添加托盘图标。
- 添加显示/隐藏、设置、退出菜单。

验收：

- 托盘退出可用。
- 显示/隐藏可用。

### MVP-004 配置读写

范围：

- 实现默认配置。
- 实现 `data/config.json` 读写。
- 配置损坏时回退默认值。

验收：

- 首次启动无需配置文件。
- 修改配置后重启可保留。
- 不保存 API Key。

### MVP-005 Windows 活动检测

范围：

- 使用 `GetLastInputInfo` 获取 idle seconds。
- 实现 `ActivitySnapshot`。
- 实现 `SessionTracker`。

验收：

- 活跃、空闲、返回事件可在日志中观察。
- 不读取窗口标题和应用名。

### MVP-006 行为引擎

范围：

- 实现 `BehaviorDecision`。
- 实现第一版行为规则。
- 实现提醒冷却。

验收：

- 人工构造活动快照能触发对应动作。
- 同类提醒不会短时间重复。

### MVP-007 动画系统和占位帧

范围：

- 实现动作定义。
- 实现帧加载。
- 实现资源缺失回退。
- 为 12 个动作创建可运行占位资源或程序占位图。

验收：

- 所有动作 ID 都可播放。
- 缺资源不崩溃。

### MVP-008 气泡文案

范围：

- 实现气泡显示。
- 实现本地模板文案。
- 接入行为引擎的 `speech_intent`。

验收：

- 触发提醒时显示短文案。
- 气泡自动消失。
- 文案不超过两行。

### MVP-009 隐私上下文

范围：

- 实现 `PrivacyContext`。
- 实现 `build_privacy_context`。
- 添加测试验证禁止字段不会出现。

验收：

- AI 只能看到摘要字段。
- 测试覆盖隐私字段边界。

### MVP-010 DeepSeek Provider

范围：

- 实现 `AIProvider` 协议。
- 实现 DeepSeek Anthropic-compatible 请求。
- 接入环境变量。
- 实现失败回退。

验收：

- 未启用 AI 时不发请求。
- API Key 缺失时不报错。
- 网络失败时回退本地模板。

### MVP-011 设置入口

范围：

- 第一版设置可简化。
- 必须支持 AI 文案开关。
- 必须支持性格选择，默认温柔陪伴型。

验收：

- 用户可以切换 AI 文案开关。
- 用户可以选择 `gentle`、`lively`、`quiet`。
- 修改后写入配置。

### MVP-012 打包前清理和文档

范围：

- 更新 README 或新增运行说明。
- 标记旧 Pygame/Web 入口状态。
- 补充开发者运行命令。

验收：

- 新开发者能根据文档启动新入口。
- 文档说明 AI 默认关闭和隐私边界。

## 7. 测试策略

第一版至少覆盖以下测试：

- 配置文件不存在、正常、损坏三种情况。
- `SessionTracker` 对 active、idle、return 事件的判断。
- `BehaviorEngine` 对 25/45/90 分钟活跃的动作选择。
- 冷却逻辑避免重复提醒。
- `build_privacy_context` 不包含敏感字段。
- AI Provider 在 API Key 缺失、超时、异常时回退。
- 动画资源缺失时 fallback 生效。

可以先使用 `pytest`。如果项目暂时没有测试框架，第一步任务需要补充测试依赖和最小测试目录。

## 8. 运行与验收命令

建议新增运行命令：

```powershell
python -m companion_app.main
```

建议新增测试命令：

```powershell
python -m pytest tests
```

第一版完成标准：

- 新入口可以在 Windows 桌面启动。
- 宠物窗口可见、可拖拽、可退出。
- 活动检测能驱动至少 5 种动作变化。
- 本地文案可用。
- AI 开关存在且默认关闭。
- DeepSeek Provider 有失败回退。
- 隐私摘要测试通过。

## 9. 仍需讨论的问题

以下问题不阻塞 MVP-001 到 MVP-008，但会影响后续体验质量：

1. 第一版宠物尺寸最终选 128x128 还是 160x160。
2. 默认贴边位置是固定右下角，还是允许记住用户上次位置后优先恢复。
3. 气泡样式采用像素风边框还是系统简洁气泡。
4. 设置入口第一版做完整设置窗口，还是托盘子菜单。
5. DeepSeek 默认模型名在实现时选哪个，需要以当时官方文档为准。
6. 是否第一版就支持开机启动。
7. 是否需要本地长期记忆；如果需要，第一版只建议记录最近提醒时间和用户性格偏好。
8. AI 生成动作帧的资产规范需要单独形成文档，包括尺寸、帧率、命名、透明背景、方向和动作语义。

## 10. 后续素材规范草案

第一版占位素材也要遵守以下命名，避免后续替换成本过高：

- 每个动作一个文件夹。
- 每帧使用透明 PNG。
- 文件名格式固定为 `frame_000.png`、`frame_001.png`。
- 同一动作内所有帧尺寸一致。
- 同一批素材整体像素密度一致。
- 宠物朝向默认面向屏幕内侧。
- 贴右边时可以水平翻转，第一版可不做。

建议后续单独创建：

```text
docs/pixel-dog-asset-spec.md
```

## 11. 官方资料引用

- DeepSeek API 文档：https://api-docs.deepseek.com/zh-cn/
- DeepSeek Anthropic API 兼容文档：https://api-docs.deepseek.com/zh-cn/guides/anthropic_api
- DeepSeek Coding Agents 文档：https://api-docs.deepseek.com/zh-cn/guides/coding_agents
