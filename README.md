# 萌伴精灵 (MoePal) —— AI Native 桌面陪伴宠物

![MoePal](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![PySide6](https://img.shields.io/badge/PySide6-GUI-green) ![AI](https://img.shields.io/badge/AI-DeepSeek_V4_Pro-orange)

萌伴精灵是一款基于 AI 的 Windows 桌面陪伴宠物。一只小猫趴在屏幕边框上，通过检测用户空闲/活跃状态主动表达情绪、提醒休息。本项目从传统的宠物养成游戏重构而来，旨在探索“低打扰、高陪伴感”的 AI 桌面智能体交互新范式。

> **本项目为 4C2026 中国大学生计算机设计大赛参赛作品。**
> 赛道：软件应用与开发专项赛——基于人工智能的多元场景应用设计与开发

---

## 🌟 核心特性

- **🐾 桌面悬浮陪伴**：采用 PySide6 实现透明、无边框、置顶的桌面窗口。小猫默认吸附在屏幕右下角，支持随意拖拽。
- **🧠 AI 情境感知**：
  - **活动检测**：零开销调用 Windows API (GetLastInputInfo) 实时追踪用户空闲与活跃时长。
  - **行为决策引擎**：内置 8 种行为状态与冷却机制。例如：连续工作 45 分钟后，小猫会“轻推”并提醒你喝水；深夜加班时，它会展现“关切”姿态。
- **💬 个性化 AI 文案**：接入 **DeepSeek V4 Pro** 大语言模型，结合用户的实时工作情境（如深夜、久坐），生成温暖、贴心的个性化陪伴文案。
- **🛡️ 极致隐私保护**：采用严格的**白名单隐私机制**。AI 仅接收抽象的状态摘要（如“活跃45分钟”、“深夜”），绝不采集屏幕内容、应用名称或键盘输入。
- **⚡ 零依赖降级体验**：在无网络、未配置 API Key 或 API 超时的情况下，系统将自动无缝回退至本地文案模板，确保陪伴体验不中断。

## 🏗️ 系统架构与技术栈

本项目采用模块化架构，严格分离 UI 渲染、状态管理与 AI 调用：

- **桌面框架**: `PySide6` (透明窗口、系统托盘、多显示器贴边吸附)
- **动画引擎**: 自研状态机 + 像素精灵帧渲染
- **AI 驱动**: `DeepSeek V4 Pro` (Anthropic-compatible API)
- **环境检测**: `Windows API`
- **开发与构建**: `Python 3.12`, `pytest` (184个用例全覆盖), `PyInstaller`

## 📁 目录结构

```text
moepal/
├── companion_app/        # 主程序核心逻辑
│   ├── main.py           # 桌面透明窗口及应用入口
│   ├── tray.py           # 系统托盘与右键菜单
│   ├── activity/         # 用户活动与空闲状态检测
│   ├── core/             # 行为决策引擎与状态机
│   ├── animation/        # 像素帧动画系统
│   └── ai/               # AI Provider 层 (对接 DeepSeek 及本地回退)
├── assets/               # 图像、音效及像素精灵资源
├── tests/                # 自动化测试用例 (pytest)
├── docs/                 # 项目文档及大赛提交材料
└── requirements.txt      # 依赖清单
```
*(注：早期的 Pygame 与 Flask 相关代码已被冻结并归档清理。)*

## 🚀 快速开始

### 1. 环境准备
确保您的系统为 **Windows 10/11 (64位)**，并已安装 **Python 3.12+**。

### 2. 克隆仓库
```bash
git clone https://github.com/xinling147/moepal.git
cd moepal
```

### 3. 安装依赖
建议在虚拟环境中安装依赖：
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 运行萌伴精灵
```bash
python companion_app/main.py
```
*启动后，一只透明背景的小猫将出现在您的屏幕右下角。您可以右键点击系统托盘图标进入“设置”，开启 AI 文案并填入您的 DeepSeek API Key。*

## 🛠️ 打包为独立 EXE

项目支持使用 PyInstaller 打包为单文件可执行程序，方便分发。
```bash
pyinstaller companion_app.spec
```
打包完成后的 `moepal.exe` 将位于 `dist/` 目录下。

## 🤝 贡献与开源

本项目已开源。我们在开发过程中广泛使用了纯国产工具链，包括 **Trae** 进行辅助编程，**Claude Code** 框架进行架构协作，以及 **豆包/即梦** 生成美术素材。欢迎提交 Issue 和 Pull Request 参与共建！

## 📄 许可证

[MIT License](LICENSE)
