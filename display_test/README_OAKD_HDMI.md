# OAKD 相机输出到 HDMI 显示器

直接显示 OAKD 相机画面到 HDMI 屏幕，完全绕过 OpenCV 窗口系统问题。

## 快速开始

### 第一步：设置脚本权限（在 Raspberry Pi 上运行）

```bash
cd ~/projects/OAKD_camera_project/display_test
chmod +x run_oakd_hdmi.sh
chmod +x start_emoji.sh
chmod +x run_emoji.sh
chmod +x setup_framebuffer.sh
chmod +x test_display.py
chmod +x emoji_simple.py
chmod +x oakd_to_hdmi.py
```

### 方法 1: 使用启动脚本（推荐）

```bash
cd display_test
./run_oakd_hdmi.sh
```

### 方法 2: 手动运行

```bash
cd display_test
unset DISPLAY
unset QT_QPA_PLATFORM
python3 oakd_to_hdmi.py
```

## 功能

- ✅ 直接显示 OAKD 相机画面
- ✅ 自动全屏显示
- ✅ 显示 FPS 信息
- ✅ 完全绕过 Qt/X11 问题
- ✅ 自动检测显示器分辨率

## 控制

- 按 `q` 键或 `ESC` 键退出

## 显示信息

屏幕会显示：
- 相机实时画面
- FPS 计数
- 提示信息

## 故障排除

### 如果相机无法初始化

1. 检查 OAKD 相机是否连接
2. 检查权限：`sudo usermod -a -G dialout $USER`
3. 重新登录

### 如果显示器没有输出

1. 确认 HDMI 连接正常
2. 检查 framebuffer：`ls -l /dev/fb0`
3. 检查分辨率：`fbset -s`

## 下一步

可以在此基础上添加：
- 人员检测叠加显示
- 深度图可视化
- 障碍检测信息
- 控制命令显示

