# 🚀 开始使用 - 在 Raspberry Pi 上

## 第一步：设置权限（必须在 Raspberry Pi 上运行）

```bash
cd ~/projects/OAKD_camera_project/display_test

# 设置所有脚本和 Python 文件为可执行
chmod +x run_oakd_hdmi.sh
chmod +x start_emoji.sh
chmod +x run_emoji.sh
chmod +x setup_framebuffer.sh
chmod +x fix_opencv_display.sh
chmod +x test_display.py
chmod +x emoji_simple.py
chmod +x oakd_to_hdmi.py
```

或者一次性设置：

```bash
cd ~/projects/OAKD_camera_project/display_test
chmod +x *.sh *.py
```

## 第二步：显示 OAKD 相机画面

```bash
cd ~/projects/OAKD_camera_project/display_test

# 方法 1: 使用启动脚本
./run_oakd_hdmi.sh

# 方法 2: 直接运行（推荐）
unset DISPLAY && unset QT_QPA_PLATFORM && python3 oakd_to_hdmi.py
```

## 第三步：显示 Emoji（测试显示）

```bash
cd ~/projects/OAKD_camera_project/display_test

# 使用启动脚本
./start_emoji.sh --emoji 😊

# 或直接运行
unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py --emoji smile
```

## 完整命令（复制粘贴）

```bash
# 1. 进入目录
cd ~/projects/OAKD_camera_project/display_test

# 2. 设置权限
chmod +x *.sh *.py

# 3. 显示 OAKD 相机
unset DISPLAY && unset QT_QPA_PLATFORM && python3 oakd_to_hdmi.py
```

## 退出

按 `q` 键退出程序。

## 文档

- `CHMOD_COMMANDS.md` - chmod 命令清单
- `SETUP_ON_PI.md` - 完整设置步骤
- `README_OAKD_HDMI.md` - OAKD 相机显示说明

