# 如何避免 Qt 错误导致程序崩溃

## 问题

Qt 错误会导致程序立即崩溃（Aborted），无法通过简单的错误捕获来解决。

## 最佳解决方案：使用 --no-gui 选项

最简单可靠的方法是使用 `--no-gui` 选项，完全跳过 GUI 相关代码：

```bash
python phase3_demo.py --simulation --no-gui
```

这样：
- ✅ 程序不会崩溃
- ✅ 所有功能都正常工作
- ✅ 控制命令输出到终端
- ✅ 没有显示窗口（但所有逻辑都正常）

## 快速启动命令

```bash
cd phase2

# 无GUI模式（推荐，避免所有Qt问题）
python phase3_demo.py --simulation --no-gui
```

## 安装 blobconverter（启用深度支持）

如果你还想启用深度图支持，需要安装：

```bash
pip install blobconverter
```

然后重新运行程序。

## 程序输出示例

使用 `--no-gui` 时，你会看到类似这样的输出：

```
[SIM] Car Command: LEFT TURN | Linear: 0.00 m/s, Angular: 0.30 rad/s

--- Status (State: SEARCH) ---
Person detected: False
Obstacle ahead: False
Car: linear=0.00 m/s, angular=0.30 rad/s
Mode: SIMULATION
----------------------------------------
```

所有功能都在运行，只是没有图形窗口而已。

## 如果必须使用 GUI

如果确实需要 GUI 显示，可以尝试：

1. **使用无头模式的环境变量**（但可能不工作）：
   ```bash
   unset QT_QPA_PLATFORM
   export OPENCV_VIDEOIO_PRIORITY_MSMF=0
   python phase3_demo.py --simulation
   ```

2. **检查 X11 连接**：
   ```bash
   echo $DISPLAY
   # 应该显示类似：localhost:10.0
   ```

3. **重新连接 SSH**：
   ```bash
   exit
   ssh -Y pi@raspberrypi.local
   ```

4. **确认 XQuartz 正在运行**（在 Mac 上）

但最可靠的方法仍然是使用 `--no-gui`。

