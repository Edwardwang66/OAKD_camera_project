# 快速修复指南

## 🚨 立即解决方案（推荐）

**使用 `--no-gui` 选项避免所有显示问题**：

```bash
cd phase2
python phase3_demo.py --simulation --no-gui
```

这样程序会：
- ✅ 正常运行所有功能
- ✅ 所有输出显示在终端
- ✅ 控制命令会打印出来（`[SIM] Car Command: ...`）
- ✅ 不会因为Qt错误崩溃
- ❌ 不显示 OpenCV 窗口（但所有功能都正常）

---

## 问题 1: Qt 显示错误导致程序崩溃

如果你看到：
```
qt.qpa.plugin: Could not find the Qt platform plugin "offscreen"
Aborted
```

### 解决方案：禁用 GUI（最简单）

使用 `--no-gui` 参数运行程序，完全跳过显示：

```bash
python phase3_demo.py --simulation --no-gui
```

这样程序会：
- ✅ 正常运行所有功能（人员检测、障碍检测、车辆控制）
- ✅ 所有输出显示在终端
- ✅ 控制命令会打印出来（`[SIM] Car Command: ...`）
- ❌ 不显示 OpenCV 窗口（但所有功能都正常）

### 或者使用脚本

```bash
chmod +x run_phase3_no_gui.sh
./run_phase3_no_gui.sh --simulation
```

## 问题 2: 缺少 blobconverter（深度图不可用）

如果你看到：
```
Warning: blobconverter not available
[OAKDCamera] Depth support: DISABLED
```

### 解决方案：安装 blobconverter

```bash
pip install blobconverter
```

或者如果在虚拟环境中：
```bash
source env/bin/activate
pip install blobconverter
```

安装后重新运行程序，你应该看到深度支持已启用。

## 快速启动命令

### 无GUI模式（推荐，避免所有显示问题）

```bash
cd phase2
python phase3_demo.py --simulation --no-gui
```

### 有GUI模式（如果显示正常工作）

```bash
cd phase2
python phase3_demo.py --simulation
```

## 程序输出说明

即使没有GUI，程序仍然会：

1. **检测人员** - 终端会显示状态
2. **检测障碍** - 终端会显示深度信息
3. **控制车辆** - 控制命令会打印到终端：
   ```
   [SIM] Car Command: LEFT TURN | Linear: 0.00 m/s, Angular: 0.30 rad/s
   [SIM] Car Command: FORWARD | Linear: 0.50 m/s, Angular: 0.00 rad/s
   ```

4. **状态更新** - 每2秒打印一次状态信息

## 查看详细文档

- 安装 blobconverter: `cat INSTALL_BLOBCONVERTER.md`
- 显示问题修复: `cat FIX_DISPLAY_ISSUE.md`
- Phase 3 使用说明: `cat README_PHASE3.md`

