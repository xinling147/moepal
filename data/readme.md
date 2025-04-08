# 数据存储说明文档

## 目录结构

```plaintext
data/
├── saves/              # 存档文件目录
│   ├── desktop/        # 桌面版存档
│   │   ├── dogs/      # 宠物存档
│   │   │   └── dog_[id].json    # 具体宠物存档
│   │   └── settings.json        # 桌面版设置
│   └── web/           # Web版存档
│       ├── users/     # 用户数据
│       │   └── user_[id]/
│       │       ├── dogs/        # 该用户的宠物存档
│       │       │   └── dog_[id].json
│       │       └── settings.json
│       └── global_settings.json
├── templates/         # 预设模板
│   ├── dog_breeds/   # 狗狗品种预设
│   └── skills/       # 技能预设
└── logs/             # 日志文件
    ├── game.log      # 游戏运行日志
    └── error.log     # 错误日志

## 文件说明
### 1. 存档文件 (saves/) 1.1 桌面版存档 (desktop/)
- dogs/dog_[id].json : 单个宠物的存档文件，包含：
  
  - 基本信息（品种、名字、创建时间等）
  - 属性状态（健康值、心情值、能量等）
  - 技能列表及等级
  - 互动历史记录
  - 成就进度
- settings.json : 桌面版全局设置
  
  - 游戏音效设置
  - 显示设置
  - 操作键位设置
  - 上次退出状态 1.2 Web版存档 (web/)
- users/user_[id]/ : 每个用户的独立数据目录
  
  - dogs/ : 该用户拥有的所有宠物存档
  - settings.json : 用户个人设置
- global_settings.json : Web版全局设置
  
  - 服务器配置
  - 全局游戏参数
  - 活动配置
### 2. 预设模板 (templates/) 2.1 狗狗品种预设 (dog_breeds/)
- 各品种的默认属性
- 外观配置
- 特殊技能倾向
- 性格特征 2.2 技能预设 (skills/)
- 技能定义
- 升级要求
- 效果参数
- 动画配置
### 3. 日志文件 (logs/)
- game.log : 记录游戏运行状态、玩家行为等信息
- error.log : 记录错误和异常信息