# 在 Raspberry Pi 上运行的 chmod 命令

## 完整命令（复制粘贴）

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

## 或者一次性设置所有

```bash
cd ~/projects/OAKD_camera_project/display_test
chmod +x *.sh *.py
```

## 验证权限

检查文件是否可执行：

```bash
ls -la *.sh *.py
```

应该看到 `-rwxr-xr-x`（有 x 表示可执行）

## 如果权限被拒绝

如果仍然看到 "Permission denied"，可能需要：

```bash
# 检查文件所有权
ls -la

# 如果文件不是你的，可能需要
sudo chown $USER:$USER *.sh *.py
chmod +x *.sh *.py
```

