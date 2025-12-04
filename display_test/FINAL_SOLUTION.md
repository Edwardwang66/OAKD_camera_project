# 最终解决方案 - 完全避免 Qt 错误

## 问题

OpenCV 在导入时会尝试初始化 Qt 后端，导致程序崩溃。

## ✅ 最佳解决方案

使用 **启动脚本**，它会从外部设置环境变量（在 Python 导入之前）：

```bash
cd display_test
./start_emoji.sh --emoji 😊
```

## 如果启动脚本不工作

### 方法 1: 直接在命令行设置环境变量

```bash
cd display_test
unset DISPLAY
unset QT_QPA_PLATFORM
python3 emoji_simple.py --emoji 😊
```

### 方法 2: 使用环境变量前缀（一行命令）

```bash
cd display_test
DISPLAY= QT_QPA_PLATFORM= python3 emoji_simple.py --emoji 😊
```

### 方法 3: 创建别名（永久解决）

在你的 `~/.bashrc` 中添加：

```bash
alias emoji='cd ~/projects/OAKD_camera_project/display_test && unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py'
```

然后使用：

```bash
emoji --emoji 😊
```

## 快速测试

测试显示是否工作：

```bash
cd display_test
DISPLAY= QT_QPA_PLATFORM= python3 -c "import cv2; print('OpenCV loaded successfully'); import numpy as np; img = np.zeros((600, 1024, 3), dtype=np.uint8); cv2.namedWindow('test'); cv2.imshow('test', img); print('Press any key...'); cv2.waitKey(2000); cv2.destroyAllWindows()"
```

如果这个测试成功，说明环境配置正确。

## 推荐工作流程

1. **使用启动脚本**（最简单）：
   ```bash
   ./start_emoji.sh --emoji smile
   ```

2. **如果失败，手动设置环境变量**：
   ```bash
   unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py --emoji smile
   ```

## 为什么需要 unset DISPLAY？

- Raspberry Pi 上的本地显示器使用 framebuffer，不需要 X11
- 设置 DISPLAY 会让 OpenCV 尝试使用 X11/Qt 后端
- 移除 DISPLAY 让 OpenCV 使用更简单的后端

## 可用的 Emoji

```bash
./start_emoji.sh --emoji 😊    # smile
./start_emoji.sh --emoji ❤️    # heart  
./start_emoji.sh --emoji 🤖    # robot
./start_emoji.sh --emoji 🚗    # car
./start_emoji.sh --emoji 🚀    # rocket
./start_emoji.sh --emoji ⭐    # star
./start_emoji.sh --emoji 🔥    # fire
./start_emoji.sh --emoji 🎉    # party
```

## 退出

按 `q` 键或 `ESC` 键退出。

## 如果所有方法都失败

如果仍然遇到 Qt 错误，可能需要：
1. 重新安装 OpenCV（使用不包含 Qt 的版本）
2. 或者使用其他显示库（如 pygame、tkinter）

但通常使用 `unset DISPLAY` 应该能解决问题。

