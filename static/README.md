# Web版静态资源目录说明

## 目录结构
static/
├── js/                     # JavaScript源代码
│   ├── game.js            # 主游戏逻辑
│   ├── pet.js             # 宠物相关逻辑
│   ├── interaction.js      # 交互功能
│   ├── animation.js       # 动画系统
│   ├── ui.js             # 用户界面组件
│   └── utils/            # 工具函数
│       ├── socket.js     # WebSocket通信
│       ├── audio.js      # 音频处理
│       └── storage.js    # 本地存储
├── css/                    # 样式文件
│   ├── main.css          # 主样式
│   ├── animations.css    # 动画样式
│   └── themes/           # 主题样式
│       ├── default.css   # 默认主题
│       └── dark.css      # 深色主题
├── images/                 # 图片资源
│   ├── ui/               # 界面元素
│   │   ├── buttons/     # 按钮图标
│   │   └── icons/       # 功能图标
│   └── backgrounds/      # 背景图片
└── audio/                  # 音频资源
├── bgm/              # 背景音乐
└── sfx/              # 音效文件

## 文件说明

### JavaScript (js/)

#### game.js
- 游戏主循环
- 场景管理
- 状态控制
- 事件分发

#### pet.js
- 宠物状态管理
- 行为系统
- 属性计算
- 成长系统

#### interaction.js
- 用户输入处理
- 语音命令识别
- 触摸事件处理
- 键盘控制

#### animation.js
- 精灵动画系统
- 过渡效果
- 粒子效果
- 动画队列管理

#### ui.js
- UI组件渲染
- 状态栏
- 对话框
- 菜单系统

#### utils/
- socket.js: WebSocket连接管理和消息处理
- audio.js: 音频加载和播放控制
- storage.js: 本地数据存储和读取

### 样式 (css/)
- 响应式布局
- 动画效果
- 主题切换
- UI组件样式

### 资源文件
- images/: 游戏所需的所有图片资源
- audio/: 背景音乐和音效文件

## 开发指南

### 添加新功能
1. 在相应目录创建新的功能模块
2. 更新game.js中的主循环
3. 在ui.js中添加必要的界面元素

### 资源管理
- 所有资源文件应按类型分类存放
- 图片资源推荐使用PNG格式
- 音频文件使用MP3格式

### 性能优化
- 使用精灵图(sprite sheets)减少图片请求
- 实现资源预加载
- 合理使用缓存
- 优化动画性能

### 浏览器兼容
- 支持主流现代浏览器
- 使用CSS前缀
- 进行跨浏览器测试

## 注意事项
1. 所有JavaScript文件使用ES6+语法
2. 确保资源文件经过压缩优化
3. 保持目录结构清晰
4. 定期清理未使用的资源文件