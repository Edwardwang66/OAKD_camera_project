# Phase 3: Person Following with Obstacle Avoidance

Phase 3在Phase 2的基础上增加了基于深度图的避障功能，在寻找和接近人的过程中避免撞到障碍物。

**设计用于：Raspberry Pi 5 + OAKD Lite相机 + DonkeyCar/VESC**

## 功能概述

Phase 3实现了以下功能：
- ✅ 基于Phase 2的人体跟踪和接近
- ✅ 使用深度图进行前方障碍物检测
- ✅ 在检测到障碍物时自动进入避障模式
- ✅ 智能选择绕行方向（左转或右转）

## 状态机

Phase 3的状态机在Phase 2的基础上新增了`AVOID_OBSTACLE`状态：

1. **SEARCH**: 
   - 缓慢旋转寻找人
   - 检测前方障碍物
   - 检测到障碍物时切换到`AVOID_OBSTACLE`

2. **APPROACH**:
   - 向人移动（根据位置进行左转/右转/直行）
   - **在前进前检测前方障碍物**
   - 检测到障碍物时切换到`AVOID_OBSTACLE`
   - 检测到人就绪时切换到`INTERACT`

3. **AVOID_OBSTACLE** (新增):
   - 停止前进
   - 扫描左右两侧的深度信息
   - 选择深度更大的一侧转向
   - 转向一段时间后返回原状态（SEARCH或APPROACH）

4. **INTERACT**:
   - 在目标距离处停止
   - 保持与人交互

5. **STOP**:
   - 紧急停止

## 避障原理

### 深度检测区域

- **前方检测区域**: 画面中间30%的矩形区域（可配置）
- **深度值处理**: 
  - 过滤掉0值和无效值（< 100mm 或 > 6000mm）
  - 使用中位数或10%最小值作为代表深度

### 障碍物判断

```
if front_depth < depth_threshold (默认0.5m):
    obstacle_ahead = True
else:
    obstacle_ahead = False
```

### 避障策略

当检测到障碍物时：
1. **停止**: 先停止0.3秒
2. **扫描**: 停止0.5秒，扫描左右两侧深度
3. **转向**: 根据左右深度选择方向，转向1秒
4. **恢复**: 返回原状态继续任务

## 硬件要求

- **Raspberry Pi 5** (或 Raspberry Pi 4)
- **OAKD Lite Camera** (需要支持stereo depth，通过USB连接)
- **DonkeyCar** with VESC电机控制器
- **Mac** (用于X11转发显示，通过XQuartz)

## 安装

### 1. 安装依赖

```bash
cd phase2
pip install -r requirements.txt
```

### 2. OAKD相机深度支持

OAKD Lite使用双目立体视觉获取深度图。确保相机正确连接，Phase 3会自动检测深度支持。

**验证深度支持**:
```bash
python -c "from oakd_camera import OAKDCamera; cam = OAKDCamera(); print('Depth:', cam.has_depth)"
```

## 使用方法

### 基本运行（仿真模式）

测试避障功能，不控制实际车辆：

```bash
cd phase2
python phase3_demo.py --simulation
```

### 调整避障阈值

```bash
# 设置障碍物检测阈值为0.3米
python phase3_demo.py --simulation --depth-threshold 0.3

# 设置障碍物检测阈值为0.8米
python phase3_demo.py --simulation --depth-threshold 0.8
```

### 实际车辆控制

```bash
# 自动检测VESC端口
python phase3_demo.py

# 指定VESC端口
python phase3_demo.py --vesc-port /dev/ttyACM0

# 调整目标距离
python phase3_demo.py --target-distance 1.5 --depth-threshold 0.5
```

### 命令行参数

- `--target-distance`: 目标距离（米，默认: 1.0）
- `--vesc-port`: VESC串口（例如 /dev/ttyACM0），None表示自动检测
- `--simulation`: 仿真模式（不实际控制车辆）
- `--depth-threshold`: 障碍物检测阈值（米，默认: 0.5）

## 文件结构

```
phase2/
├── oakd_camera.py          # OAKD相机接口（已添加深度支持）
├── car_controller.py       # 车辆控制接口
├── person_follower.py      # 人体跟踪控制逻辑
├── obstacle_detector.py    # 障碍物检测模块（新增）
├── obstacle_avoider.py     # 避障控制模块（新增）
├── phase2_demo.py          # Phase 2演示（原始版本）
├── phase3_demo.py          # Phase 3演示（带避障）
└── README_PHASE3.md        # 本文档
```

## 配置参数

### 障碍物检测器 (`ObstacleDetector`)

在`phase3_demo.py`中初始化：

```python
self.obstacle_detector = ObstacleDetector(
    front_region_ratio=0.3,      # 前方检测区域比例（30%）
    depth_threshold=0.5,          # 障碍物阈值（米）
    min_depth_mm=100,             # 最小有效深度（毫米）
    max_depth_mm=6000,            # 最大有效深度（毫米）
    method='median'               # 'median' 或 'percentile_10'
)
```

### 避障控制器 (`ObstacleAvoider`)

在`phase3_demo.py`中初始化：

```python
self.obstacle_avoider = ObstacleAvoider(
    turn_duration=1.0,            # 转向持续时间（秒）
    turn_angular_speed=0.5,       # 转向角速度（rad/s）
    scan_duration=0.5             # 扫描持续时间（秒）
)
```

## 工作原理

### 深度图获取

OAKD Lite使用双目立体视觉：
- 左右两个单目相机（MonoCamera）
- 立体深度节点（StereoDepth）计算深度图
- 深度值以毫米为单位（16位）

### 障碍物检测流程

1. **获取深度图**: 从相机获取当前深度帧
2. **提取前方区域**: 提取画面中间30%区域
3. **过滤无效值**: 移除0值和超出范围的值
4. **计算代表深度**: 使用中位数或10%最小值
5. **判断障碍物**: 比较代表深度与阈值

### 避障决策流程

```
检测到障碍物
    ↓
进入AVOID_OBSTACLE状态
    ↓
停止0.3秒
    ↓
扫描左右深度0.5秒
    ↓
选择深度更大的一侧
    ↓
转向1秒
    ↓
返回原状态（SEARCH或APPROACH）
```

## 故障排除

### 深度图不可用

如果显示"Depth: DISABLED"：

1. **检查相机型号**: 确认是OAKD Lite（支持stereo depth）
2. **检查连接**: 确保相机正确连接
3. **查看日志**: 查看初始化时的错误信息

```
[OAKDCamera] Warning: Could not initialize depth cameras: ...
[OAKDCamera] Depth support disabled (camera may not have stereo)
```

### 障碍物检测不准确

- **调整阈值**: 尝试不同的`--depth-threshold`值
- **调整检测区域**: 修改`front_region_ratio`参数
- **检查光照**: 确保充足光照（双目视觉需要良好光照）
- **检查深度范围**: 调整`min_depth_mm`和`max_depth_mm`

### 避障行为异常

- **调整转向速度**: 修改`turn_angular_speed`
- **调整转向时间**: 修改`turn_duration`
- **检查深度质量**: 查看深度图可视化

## 安全注意事项

⚠️ **重要**：
- 始终先在仿真模式下测试：`--simulation`
- 准备紧急停止（按's'键）
- 在安全、开放的区域测试
- 从低速开始测试
- 密切监控车辆行为
- 确保可以手动停止车辆

## 未来改进

- [ ] 使用深度图计算到人的实际距离（替代bounding box大小）
- [ ] 改进避障策略（多步避障、路径规划）
- [ ] 添加LiDAR支持（替换深度图作为障碍检测源）
- [ ] 动态调整避障参数
- [ ] 记录和回放避障数据

## 与LiDAR集成（未来）

当前实现使用深度图进行障碍检测。如果将来要使用LiDAR，只需要替换障碍检测的输入源：

```python
# 当前：使用深度图
depth_frame = camera.get_depth_frame()
obstacle_result = obstacle_detector.detect_obstacle(depth_frame)

# 未来：使用LiDAR
lidar_data = lidar.get_scan()
obstacle_result = obstacle_detector.detect_obstacle_from_lidar(lidar_data)
```

避障逻辑和状态机保持不变。

## 参考

- Phase 2 README: `README.md`
- OAKD Lite深度支持: 参考 `phase1/phase1_oakd_camera.py`
- DepthAI文档: https://docs.luxonis.com/

