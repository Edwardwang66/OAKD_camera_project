# 修复 OpenCV Qt/X11 显示问题

如果遇到以下错误：
```
qt.qpa.xcb: could not connect to display localhost:10.0
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

这是 OpenCV 尝试使用 Qt 后端与 X11 转发不兼容导致的。

## 快速修复方法

### 方法 1: 使用环境变量（推荐）

在运行程序前设置环境变量：

```bash
export QT_QPA_PLATFORM=offscreen
export OPENCV_VIDEOIO_PRIORITY_MSMF=0
python phase3_demo.py --simulation
```

或者一行命令：
```bash
QT_QPA_PLATFORM=offscreen OPENCV_VIDEOIO_PRIORITY_MSMF=0 python phase3_demo.py --simulation
```

### 方法 2: 使用修复脚本

```bash
chmod +x fix_opencv_display.sh
./fix_opencv_display.sh python phase3_demo.py --simulation
```

### 方法 3: 添加到 ~/.bashrc（永久解决）

```bash
echo 'export QT_QPA_PLATFORM=offscreen' >> ~/.bashrc
echo 'export OPENCV_VIDEOIO_PRIORITY_MSMF=0' >> ~/.bashrc
source ~/.bashrc
```

### 方法 4: 无GUI模式运行

如果不需要显示窗口，程序仍然可以正常运行（控制命令会打印到终端）：

```bash
# 程序会自动检测GUI是否可用，如果不可用会继续运行但不显示窗口
python phase3_demo.py --simulation
```

## 检查 X11 转发

1. **确认 XQuartz 正在运行**（在 Mac 上）
2. **检查 DISPLAY 变量**：
   ```bash
   echo $DISPLAY
   # 应该显示类似：localhost:10.0
   ```
3. **重新连接 SSH**：
   ```bash
   # 断开当前连接，然后重新连接
   exit
   ssh -Y pi@raspberrypi.local
   ```

## 验证修复

运行测试：
```bash
python -c "import cv2; print('OpenCV version:', cv2.__version__); cv2.namedWindow('test')"
```

如果成功，说明修复生效。如果还有错误，错误会被捕获，程序会继续运行。

## 注意事项

- 程序会自动捕获 Qt 错误并继续运行
- 即使显示失败，所有控制逻辑仍然正常工作
- 控制命令会打印到终端（`[SIM] Car Command: ...`）
- 可以通过终端输出来监控程序状态

## 如果问题仍然存在

1. 检查 XQuartz 是否运行：在 Mac 上打开 XQuartz 应用
2. 重启 XQuartz：完全退出并重新打开
3. 检查 XQuartz 设置：Preferences > Security > "Allow connections from network clients"
4. 尝试不同的 SSH 选项：
   ```bash
   ssh -X pi@raspberrypi.local  # 不信任模式（可能更兼容）
   ```

## 临时解决方案：忽略显示错误

程序已经配置为即使显示失败也会继续运行。你可以：
- 忽略 Qt 错误消息
- 通过终端输出监控程序状态
- 使用 `--simulation` 模式看到所有控制命令

显示错误不会影响：
- 相机采集
- 人员检测
- 障碍检测
- 车辆控制命令

