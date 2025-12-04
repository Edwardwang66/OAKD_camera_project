# Display Test for Raspberry Pi

这个文件夹包含用于检查 Raspberry Pi 显示功能和显示 emoji 的工具。

## 文件说明

- `display_check.py` - 显示检查工具
- `emoji_display.py` - Emoji 显示工具（通用版本）
- `emoji_display_framebuffer.py` - Emoji 显示工具（专用于 framebuffer）
- `test_display.py` - 快速测试脚本
- `setup_framebuffer.sh` - Framebuffer 环境设置脚本
- `README.md` - 本文件

## 快速开始

### 对于 Raspberry Pi 本地显示器（Framebuffer）

如果你有直接连接到 Raspberry Pi 的显示器（如 7 寸触摸屏），使用 framebuffer 版本：

```bash
# 1. 设置环境（可选，但推荐）
source setup_framebuffer.sh

# 2. 显示 emoji
python emoji_display_framebuffer.py --emoji smile
```

或者直接运行（会自动检测分辨率）：

```bash
python emoji_display_framebuffer.py --emoji heart
```

### 1. 检查显示

```bash
cd display_test
python display_check.py
```

这会显示：
- DISPLAY 变量是否设置
- 是否检测到 framebuffer
- OpenCV 是否可以显示窗口
- 显示分辨率（如果可用）

### 2. 显示 Emoji

显示单个 emoji：

```bash
python emoji_display.py --emoji smile
```

可用的 emoji 包括：
- `smile` - 😊
- `heart` - ❤️
- `thumbs_up` - 👍
- `wave` - 👋
- `rocket` - 🚀
- `car` - 🚗
- `robot` - 🤖
- `star` - ⭐
- `fire` - 🔥
- `party` - 🎉

### 3. Emoji 动画

循环显示多个 emoji：

```bash
python emoji_display.py --animate --delay 1.5
```

### 4. 全屏模式

使用全屏显示：

```bash
python emoji_display.py --emoji heart --fullscreen
```

### 5. 自定义分辨率

```bash
python emoji_display.py --emoji smile --width 1280 --height 720
```

## 命令行参数

### emoji_display.py

- `--emoji`: 要显示的 emoji（默认: smile）
- `--fullscreen`: 使用全屏模式
- `--width`: 屏幕宽度（默认: 800）
- `--height`: 屏幕高度（默认: 480）
- `--animate`: 动画模式（循环显示多个 emoji）
- `--delay`: 动画延迟时间（秒，默认: 1.0）

## 依赖

- OpenCV (`opencv-python`)
- NumPy
- PIL/Pillow (可选，用于更好的 emoji 支持)

安装依赖：

```bash
pip install opencv-python numpy pillow
```

## 显示模式

程序会自动检测显示模式：

1. **本地显示** - Raspberry Pi 直接连接的显示器
2. **X11 转发** - 通过 SSH X11 转发显示
3. **Headless** - 无显示器（程序仍然可以运行，但不显示窗口）

## 退出

按 `q` 键或 `ESC` 键退出程序。

## 注意事项

- OpenCV 本身不直接支持 emoji 字符，程序会尝试使用 PIL/Pillow 来渲染 emoji
- 如果 PIL/Pillow 不可用，会回退到 OpenCV 文本渲染（可能无法正确显示 emoji）
- 对于全屏模式，程序会尝试使用 OpenCV 的全屏功能
- 如果显示不可用，程序会继续运行但可能无法显示窗口

## 示例使用

### 检查显示状态

```bash
python display_check.py
```

输出示例：
```
✓ DISPLAY variable set: :0.0
✓ Framebuffer device found: /dev/fb0
✓ Resolution: 800x480
✓ OpenCV display backend available

Display Mode: LOCAL
Status:
  ✓ Display is AVAILABLE
  ✓ OpenCV can display windows
```

### 显示欢迎信息

```bash
python emoji_display.py --emoji wave --fullscreen
```

### 创建动画效果

```bash
python emoji_display.py --animate --delay 0.5 --fullscreen
```

