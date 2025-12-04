# 在 Raspberry Pi 上设置步骤

## 第一步：设置脚本权限

连接到 Raspberry Pi 后，运行以下命令设置脚本执行权限：

```bash
cd ~/projects/OAKD_camera_project/display_test

# 设置所有脚本为可执行
chmod +x run_oakd_hdmi.sh
chmod +x start_emoji.sh
chmod +x run_emoji.sh
chmod +x setup_framebuffer.sh
chmod +x fix_opencv_display.sh

# 设置 Python 脚本为可执行（可选）
chmod +x test_display.py
chmod +x emoji_simple.py
chmod +x oakd_to_hdmi.py
```

或者一次性设置所有：

```bash
cd ~/projects/OAKD_camera_project/display_test
chmod +x *.sh *.py
```

## 第二步：运行程序

### 显示 OAKD 相机画面

```bash
cd ~/projects/OAKD_camera_project/display_test
./run_oakd_hdmi.sh
```

或者：

```bash
unset DISPLAY && unset QT_QPA_PLATFORM && python3 oakd_to_hdmi.py
```

### 显示 Emoji

```bash
cd ~/projects/OAKD_camera_project/display_test
./start_emoji.sh --emoji 😊
```

或者：

```bash
unset DISPLAY && unset QT_QPA_PLATFORM && python3 emoji_simple.py --emoji smile
```

## 检查显示

```bash
python3 display_check.py
```

## 常见问题

### 权限被拒绝

如果看到 "Permission denied" 错误：

```bash
chmod +x <script_name>.sh
```

### 脚本不存在

确保你在正确的目录：

```bash
cd ~/projects/OAKD_camera_project/display_test
ls -la *.sh
```

### 找不到 Python

使用 python3 而不是 python：

```bash
python3 oakd_to_hdmi.py
```

## 完整的设置命令（复制粘贴）

```bash
# 1. 进入目录
cd ~/projects/OAKD_camera_project/display_test

# 2. 设置权限
chmod +x *.sh *.py

# 3. 显示 OAKD 相机
unset DISPLAY && unset QT_QPA_PLATFORM && python3 oakd_to_hdmi.py
```

