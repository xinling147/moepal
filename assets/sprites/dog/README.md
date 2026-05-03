# 宠物动作精灵帧目录

## 命名约定

- 目录名 = 动作 ID（见 `companion_app/animation/actions.py`）
- 帧文件 = `frame_000.png`, `frame_001.png`, ...
- 推荐尺寸：128×128 或 256×256 像素 PNG

## 12 个动作

| 动作 ID | 说明 | 循环 |
|---------|------|------|
| idle_lie | 趴在屏幕边框上（默认状态） | 是 |
| tail_wag | 轻微摇尾巴 | 是 |
| sleep | 睡着 | 是 |
| wake_up | 醒来 | 否 |
| stretch | 伸懒腰 | 否 |
| look_around | 左右观察 | 是 |
| nudge | 轻提醒 | 否 |
| concerned | 担心/关切 | 否 |
| happy_bounce | 开心小跳 | 否 |
| peek | 从边缘探头 | 否 |
| walk_edge | 沿屏幕边缘移动 | 否 |
| sit_wait | 安静等待 | 是 |

## 占位说明

当前阶段使用程序生成的占位图。将 PNG 帧放入对应目录后，动画系统会自动加载。
