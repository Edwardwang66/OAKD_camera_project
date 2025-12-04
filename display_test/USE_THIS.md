# ✅ 使用这个命令 - 解决 Qt 错误

## 问题

看到 Qt 错误导致程序崩溃：
```
qt.qpa.xcb: could not connect to display
Aborted
```

## ✅ 解决方案

### 第一步：设置脚本权限（在 Raspberry Pi 上运行）

```bash
cd ~/projects/OAKD_camera_project/display_test
chmod +x run_oakd_hdmi.sh start_emoji.sh run_emoji.sh setup_framebuffer.sh
chmod +x test_display.py emoji_simple.py oakd_to_hdmi.py
```

### 第二步：运行程序

**关键：必须在运行 Python 之前从 shell 中 unset DISPLAY！**

### 正确的方法（在 shell 中 unset）：

```bash
cd display_test
unset DISPLAY
unset QT_QPA_PLATFORM
python3 emoji_simple.py --emoji 😊
```

或者一行命令：

```bash
cd display_test
unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py --emoji smile
```

或者使用启动脚本：

```bash
cd display_test
./start_emoji.sh --emoji 😊
```

## 为什么必须 unset DISPLAY？

- Raspberry Pi 的本地显示器使用 framebuffer，不需要 X11
- DISPLAY 环境变量会让 OpenCV 尝试使用 X11/Qt 后端
- 必须在 **运行 Python 之前** unset，不能在 Python 代码中设置（太晚了）

## 测试

快速测试是否工作：

```bash
unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py --emoji 😊
```

如果成功，你会看到 emoji 显示在屏幕上！

## 退出

按 `q` 键退出。

