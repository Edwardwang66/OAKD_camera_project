# 快速启动指南 - Framebuffer 显示

## 你遇到的问题

你看到了：
- ✓ Framebuffer device found: /dev/fb0
- ✓ Resolution: 1024x600
- ✗ Qt 错误导致程序崩溃

## 立即解决方案

使用 **framebuffer 专用版本**，避免 Qt 问题：

```bash
cd display_test
python emoji_display_framebuffer.py --emoji smile
```

就这么简单！

## 完整步骤

### 1. 检查显示状态

```bash
python display_check.py
```

你应该看到：
```
✓ Framebuffer device found: /dev/fb0
✓ Resolution: 1024x600
```

### 2. 显示 Emoji

```bash
python emoji_display_framebuffer.py --emoji smile
```

### 3. 尝试不同的 Emoji

```bash
python emoji_display_framebuffer.py --emoji heart
python emoji_display_framebuffer.py --emoji robot
python emoji_display_framebuffer.py --emoji car
python emoji_display_framebuffer.py --emoji rocket
```

## 可用的 Emoji

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

## 退出程序

按 `q` 键或 `ESC` 键退出。

## 为什么使用 framebuffer 版本？

- ✅ 避免了 Qt 后端问题
- ✅ 直接使用 framebuffer（更快）
- ✅ 自动检测分辨率
- ✅ 全屏显示
- ✅ 专为 Raspberry Pi 本地显示器设计

## 如果还有问题

查看详细文档：
- `FIX_FRAMEBUFFER.md` - Framebuffer 问题修复
- `README.md` - 完整文档

