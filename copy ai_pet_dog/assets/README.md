# Assets 资源目录说明

## 目录结构
assets/
├── images/
│   ├── pixel_dogs/
│   │   ├── normal/          # 普通状态的狗狗造型
│   │   ├── happy/           # 开心状态的狗狗造型
│   │   ├── sad/             # 伤心状态的狗狗造型
│   │   ├── sleeping/        # 睡眠状态的狗狗造型
│   │   └── sick/            # 生病状态的狗狗造型
│   ├── animations/
│   │   ├── idle/           # 待机动画
│   │   ├── walk/           # 行走动画
│   │   ├── eat/            # 进食动画
│   │   ├── play/           # 玩耍动画
│   │   └── sleep/          # 睡眠动画
│   ├── backgrounds/
│   │   ├── home/           # 主屏幕背景
│   │   ├── garden/         # 花园场景
│   │   ├── park/           # 公园场景
│   │   └── shop/           # 商店场景
│   └── items/
│       ├── food/           # 食物道具
│       ├── toys/           # 玩具道具
│       ├── furniture/      # 家具装饰
│       ├── clothes/        # 宠物服装
│       └── medicine/       # 医疗道具
└── sounds/
├── bgm/               # 背景音乐
│   ├── main_theme/    # 主题音乐
│   ├── happy/         # 欢快场景音乐
│   └── calm/          # 平静场景音乐
├── sfx/               # 音效
│   ├── ui/            # 界面音效
│   ├── pet/           # 宠物音效
│   └── ambient/       # 环境音效
└── voice/             # 语音
└── notifications/ # 通知语音

## 文件格式规范

### 图像资源
- 宠物图像：PNG格式，透明背景
- 动画序列：PNG序列帧，统一尺寸
- 背景图像：JPG/PNG格式
- 道具图像：PNG格式，透明背景

### 音频资源
- 背景音乐：MP3格式，44.1kHz，128-320kbps
- 音效：WAV/OGG格式，44.1kHz
- 语音：MP3格式，44.1kHz，128-192kbps

## 命名规范

### 图像文件
- 宠物图像：`[state]_[action]_[frame].png`
  例：normal_idle_01.png
- 动画：`[action]_[direction]_[frame].png`
  例：walk_right_01.png
- 背景：`[scene]_[variation].jpg`
  例：home_day.jpg
- 道具：`[category]_[item]_[variation].png`
  例：food_bone_gold.png

### 音频文件
- 背景音乐：`bgm_[scene]_[mood].mp3`
  例：bgm_home_happy.mp3
- 音效：`sfx_[category]_[action].wav`
  例：sfx_ui_click.wav
- 语音：`voice_[type]_[message].mp3`
  例：voice_notification_levelup.mp3

## 注意事项
1. 所有资源文件大小应适当优化，避免过大
2. 图像资源建议使用合适的压缩工具处理
3. 确保所有资源文件均具有合适的权限许可
4. 定期备份重要资源文件
5. 新增资源时遵循相应的命名规范