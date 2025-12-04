# 修复 Framebuffer 显示问题

## 问题

如果你看到类似错误：
```
qt.qpa.xcb: could not connect to display
Aborted
```

这是 OpenCV 尝试使用 Qt 后端导致的。对于 Raspberry Pi 上的本地 framebuffer 显示器，我们需要禁用 Qt。

## 解决方案

### 方法 1: 使用 Framebuffer 专用脚本（推荐）

直接使用专为 framebuffer 设计的脚本：

```bash
python emoji_display_framebuffer.py --emoji smile
```

这个脚本会自动：
- 设置正确的环境变量
- 禁用 Qt 后端
- 使用 framebuffer 直接显示

### 方法 2: 设置环境变量

```bash
export DISPLAY=:0.0
unset QT_QPA_PLATFORM
export OPENCV_VIDEOIO_PRIORITY_LIST=V4L2,FFMPEG

python emoji_display.py --emoji smile
```

或者使用提供的脚本：

```bash
source setup_framebuffer.sh
python emoji_display.py --emoji smile
```

### 方法 3: 在代码中设置（已自动处理）

`emoji_display_framebuffer.py` 已经在代码开头设置了正确的环境变量，所以直接运行即可。

## 检查显示状态

首先检查你的显示配置：

```bash
python display_check.py
```

如果看到：
- ✓ Framebuffer device found: /dev/fb0
- ✓ Resolution: 1024x600（或你的分辨率）

说明检测到了本地显示器。

## 推荐工作流程

1. **检查显示**：
   ```bash
   python display_check.py
   ```

2. **显示 emoji**（使用 framebuffer 版本）：
   ```bash
   python emoji_display_framebuffer.py --emoji smile
   ```

3. **测试不同 emoji**：
   ```bash
   python emoji_display_framebuffer.py --emoji heart
   python emoji_display_framebuffer.py --emoji robot
   ```

## 可用 Emoji

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

## 退出

按 `q` 键或 `ESC` 键退出程序。

## 注意事项

- Framebuffer 版本会自动检测分辨率
- 如果分辨率不是 1024x600，脚本会自动调整
- 程序会在全屏模式下显示
- 如果遇到问题，检查是否有权限访问 /dev/fb0

