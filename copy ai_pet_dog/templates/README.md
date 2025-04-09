# Templates 目录说明

## 目录结构
templates/
├── base/                # 基础模板
│   ├── base.html       # 基础布局模板
│   └── header.html     # 通用头部组件
├── components/          # 可复用组件
│   ├── pet_status.html # 宠物状态显示组件
│   ├── controls.html   # 互动控制面板组件
│   ├── inventory.html  # 物品栏组件
│   └── dialog.html     # 对话框组件
├── game/               # 游戏相关页面
│   ├── main.html      # 主游戏界面
│   └── minigames/     # 迷你游戏模板
│       ├── fetch.html  # 接飞盘游戏界面
│       ├── maze.html   # 迷宫游戏界面
│       └── race.html   # 障碍跑游戏界面
├── auth/               # 认证相关页面
│   ├── login.html     # 登录页面
│   └── register.html  # 注册页面
├── error/             # 错误页面
│   ├── 404.html      # 404错误页面
│   └── 500.html      # 500错误页面
└── index.html         # 主页面

## 模板说明

### base/base.html
- 定义网站的基本HTML结构
- 包含通用的CSS和JavaScript引用
- 定义主要布局区块
- 集成响应式设计支持

### base/header.html
- 包含导航栏
- 用户状态显示
- 主要功能入口

### components/
所有组件模板都设计为可复用的模块：
- **pet_status.html**: 显示宠物的各项状态指标
- **controls.html**: 包含所有互动按钮和控制选项
- **inventory.html**: 显示和管理物品栏
- **dialog.html**: 通用对话框模板

### game/main.html
主要游戏界面，包含：
- 游戏画布区域
- 状态显示区
- 控制面板
- 物品栏
- 互动按钮

### game/minigames/
每个迷你游戏模板都包含：
- 游戏专用画布
- 计分板
- 控制说明
- 返回主界面选项

### auth/
认证相关页面采用简洁的设计：
- **login.html**: 登录表单和社交媒体登录选项
- **register.html**: 注册表单和用户协议

### error/
错误页面包含：
- 错误说明
- 返回主页选项
- 友好的提示信息

### index.html
网站主页面，包含：
- 欢迎信息
- 功能介绍
- 快速开始选项
- 新闻公告区域

## 开发指南

### 模板继承
- 所有页面都应继承自 `base.html`
- 使用 block 标签定义可覆盖的内容区域

### 组件使用
- 使用 `{% include %}` 引入组件
- 组件应该支持参数传递

### 响应式设计
- 所有模板都应支持响应式设计
- 使用 Bootstrap 网格系统
- 针对移动设备优化布局

### JavaScript集成
- 使用 data-* 属性进行DOM选择
- 避免在模板中直接写入JavaScript代码
- 使用事件委托处理动态元素

### 注意事项
1. 保持模板结构清晰，避免过度嵌套
2. 注释关键的模板块和复杂的逻辑部分
3. 确保所有模板都正确继承基础模板
4. 保持组件的独立性和可复用性