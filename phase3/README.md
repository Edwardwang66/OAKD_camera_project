# Phase 3: Person Following with Obstacle Avoidance

Phase 3在Phase 2的基础上增加了基于深度图的避障功能，在寻找和接近人的过程中避免撞到障碍物。

**设计用于：Raspberry Pi 5 + OAKD Lite相机 + DonkeyCar/VESC**

## 概述

Phase 3实现了以下功能：
- ✅ 基于Phase 2的人体跟踪和接近
- ✅ 使用深度图进行前方障碍物检测
- ✅ 在检测到障碍物时自动进入避障模式
- ✅ 智能选择绕行方向（左转或右转）

## 快速开始

### 安装依赖

```bash
cd phase3
pip install -r requirements.txt
```

### 运行程序（无GUI模式，推荐）

```bash
python phase3_demo.py --simulation --no-gui
```

### 安装 blobconverter（启用深度支持）

如果需要深度图支持，安装：

```bash
pip install blobconverter
```

详细说明请查看 `INSTALL_BLOBCONVERTER.md`

## 文件结构

```
phase3/
├── phase3_demo.py          # 主演示程序
├── obstacle_detector.py    # 障碍物检测模块
├── obstacle_avoider.py     # 避障控制模块
├── README.md               # 本文件
├── README_PHASE3.md        # 详细文档
├── QUICK_FIX.md            # 快速修复指南
├── requirements.txt        # 依赖列表
└── ...
```

## 状态机

Phase 3的状态机包括：

1. **SEARCH**: 缓慢旋转寻找人，检测前方障碍物
2. **APPROACH**: 向人移动，前进前检测障碍物
3. **AVOID_OBSTACLE**: 避障模式（停止、扫描、转向）
4. **INTERACT**: 在目标距离处停止
5. **STOP**: 紧急停止

## 避障原理

- **前方检测区域**: 画面中间30%的矩形区域
- **深度值处理**: 过滤无效值，使用中位数或10%最小值
- **障碍物判断**: 如果前方深度 < 阈值（默认0.5m），则检测到障碍物
- **避障策略**: 停止 → 扫描左右深度 → 选择方向 → 转向 → 恢复

## 使用方法

### 基本运行

```bash
# 仿真模式（无GUI）
python phase3_demo.py --simulation --no-gui

# 实际车辆控制
python phase3_demo.py --vesc-port /dev/ttyACM0
```

### 命令行参数

- `--target-distance`: 目标距离（米，默认: 1.0）
- `--vesc-port`: VESC串口（例如 /dev/ttyACM0）
- `--simulation`: 仿真模式（不实际控制车辆）
- `--depth-threshold`: 障碍物检测阈值（米，默认: 0.5）
- `--no-gui`: 禁用GUI显示（避免Qt错误）

## 依赖模块

Phase 3依赖于phase2中的共享模块：
- `oakd_camera.py` - OAKD相机接口（需要深度支持）
- `car_controller.py` - 车辆控制接口
- `person_follower.py` - 人员跟踪控制逻辑

这些模块位于 `../phase2/` 目录中。

## 故障排除

### Qt显示错误

如果遇到Qt/X11显示错误，使用 `--no-gui` 选项：

```bash
python phase3_demo.py --simulation --no-gui
```

详细说明请查看 `QUICK_FIX.md` 和 `RUN_WITHOUT_CRASHING.md`

### 深度支持不可用

如果没有深度支持，安装 `blobconverter`：

```bash
pip install blobconverter
```

详细说明请查看 `INSTALL_BLOBCONVERTER.md`

## 详细文档

- `README_PHASE3.md` - Phase 3详细文档
- `QUICK_FIX.md` - 快速修复指南
- `RUN_WITHOUT_CRASHING.md` - 避免崩溃的说明
- `INSTALL_BLOBCONVERTER.md` - 安装blobconverter指南
- `FIX_DISPLAY_ISSUE.md` - 显示问题修复

## 与Phase 2的关系

Phase 3基于Phase 2，添加了：
- 深度图获取和处理
- 障碍物检测模块
- 避障控制逻辑
- AVOID_OBSTACLE状态

Phase 2的文件位于 `../phase2/` 目录中，Phase 3会自动从那里导入共享模块。

## 下一步

- [ ] 使用深度图计算到人的实际距离（替代bounding box大小）
- [ ] 改进避障策略（多步避障、路径规划）
- [ ] 添加LiDAR支持（替换深度图作为障碍检测源）
- [ ] 动态调整避障参数

