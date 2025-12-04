# 🚀 立即开始 - 显示 Emoji

## 问题

如果遇到 Qt 错误：
```
qt.qpa.xcb: could not connect to display
Aborted
```

## ✅ 解决方案：使用启动脚本

**使用提供的启动脚本**（它会自动配置环境变量）：

```bash
cd display_test
./start_emoji.sh --emoji 😊
```

或者直接使用 emoji 名称：

```bash
./start_emoji.sh --emoji smile
```

## 快速命令

```bash
# 使用启动脚本（推荐）
./start_emoji.sh --emoji smile      # 😊
./start_emoji.sh --emoji heart      # ❤️
./start_emoji.sh --emoji robot      # 🤖
./start_emoji.sh --emoji car        # 🚗
./start_emoji.sh --emoji rocket     # 🚀
```

## 如果启动脚本不起作用

### 方法 1: 手动设置环境变量

```bash
unset DISPLAY
unset QT_QPA_PLATFORM
python3 emoji_simple.py --emoji 😊
```

### 方法 2: 使用环境变量前缀

```bash
DISPLAY= QT_QPA_PLATFORM= python3 emoji_simple.py --emoji 😊
```

### 方法 3: 一行命令

```bash
unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py --emoji smile
```

## 可用的 Emoji

直接在命令行中使用 emoji 字符：

```bash
./start_emoji.sh --emoji 😊
./start_emoji.sh --emoji ❤️
./start_emoji.sh --emoji 🤖
./start_emoji.sh --emoji 🚗
./start_emoji.sh --emoji 🚀
./start_emoji.sh --emoji ⭐
./start_emoji.sh --emoji 🔥
./start_emoji.sh --emoji 🎉
```

或者使用名称：

```bash
./start_emoji.sh --emoji smile
./start_emoji.sh --emoji heart
./start_emoji.sh --emoji robot
```

## 退出

按 `q` 键或 `ESC` 键退出程序。

## 如果仍然有问题

查看详细文档：
- `QUICKSTART.md` - 快速开始指南
- `FIX_FRAMEBUFFER.md` - 问题修复说明

