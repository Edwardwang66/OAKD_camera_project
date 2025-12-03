# Phase 1: OAK-D 桌面 Demo

Phase 1 实现了在桌面环境（电脑/树莓派）上使用 OAK-D 相机进行人体检测、距离估计和石头剪刀布游戏的功能。

## 功能特性

### 1. 人体检测
- **输入**: OAK-D 彩色图像
- **输出**:
  - `person_found`: True/False
  - `person_bbox`: (x_min, y_min, x_max, y_max)
- **实现**: 使用 MediaPipe Pose 进行人体检测（可扩展为 OAK-D 的 mobilenet-ssd 模型）

### 2. 距离估计
- **输入**: OAK-D 深度图
- **输出**: `distance_to_person` (单位: 米)
- **实现**: 在人体 bbox 中心区域提取深度 patch，计算平均深度值

### 3. 游戏模块
- **输入**: 手部图像/关键点
- **输出**: rock / paper / scissors
- **接口**: `result = rps_game.play_round(frame)`

## 文件结构

```
phase1_person_detector.py  # 人体检测模块
phase1_oakd_camera.py      # 支持深度的 OAK-D 相机接口
phase1_rps_game.py         # RPS 游戏包装类
phase1_demo.py             # Phase 1 主演示程序
```

## 安装依赖

```bash
# 基础依赖
pip install opencv-python numpy mediapipe

# OAK-D 相机支持
pip install depthai

# RPS 模型（可选，用于更准确的手势识别）
# 模型文件应放在 project-1/ 目录下
# rps_model_improved.pth 或 rps_model.pth
```

## 使用方法

### 基本运行

```bash
# 在项目根目录运行
python phase1_demo.py
```

### 功能说明

程序启动后会显示两个模式：

1. **检测模式 (Detection Mode)**
   - 显示人体检测框
   - 显示距离信息
   - 按 `'d'` 切换到检测模式

2. **互动模式 (Interaction Mode)**
   - 在检测到人体后，可以进行石头剪刀布游戏
   - 显示手势识别结果
   - 显示游戏得分
   - 按 `'i'` 切换到互动模式

### 键盘控制

- `'q'` - 退出程序
- `'i'` - 切换到互动模式（RPS 游戏）
- `'d'` - 切换到检测模式（人体+距离）
- `'r'` - 重置 RPS 游戏

## 完成标准

✅ **Phase 1 完成标准**:

1. ✅ 在桌面上运行程序
2. ✅ 能看到画面里检测出人（框框）+ 距离
3. ✅ 能在"互动模式"里玩石头剪刀布，结果稳定

## 技术实现

### 人体检测

当前使用 MediaPipe Pose 进行人体检测。未来可以集成 OAK-D 的 mobilenet-ssd 模型以获得更好的性能：

```python
# 使用 mobilenet-ssd（需要集成到相机 pipeline）
from phase1_person_detector import PersonDetector
detector = PersonDetector(use_separate_pipeline=True)
```

### 距离估计

使用 OAK-D 的深度相机计算距离：

```python
# 获取深度图
depth_frame = camera.get_depth_frame()

# 从 bbox 中心计算距离
distance = camera.get_distance_from_bbox(person_bbox, depth_frame)
```

### RPS 游戏

游戏模块已包装为简单的接口：

```python
from phase1_rps_game import Phase1RPSGame

# 初始化游戏
rps_game = Phase1RPSGame()

# 玩一局
result = rps_game.play_round(frame)
# result 包含: result, player_gesture, ai_gesture, player_score, ai_score
```

## 故障排除

### OAK-D 相机未检测到

- 确保 OAK-D 相机已正确连接
- 检查 DepthAI 是否正确安装: `python -c "import depthai; print('OK')"`
- 如果没有 OAK-D，程序会自动回退到普通摄像头（但无深度支持）

### 人体检测不工作

- 确保 MediaPipe 已安装: `pip install mediapipe`
- 检查光照条件是否充足
- 尝试调整相机角度

### RPS 游戏识别不准确

- 确保手部在画面中清晰可见
- 尝试使用模型文件（`rps_model_improved.pth`）以获得更好的识别
- 保持手势稳定至少 1 秒

## 下一步 (Phase 2+)

- 集成 mobilenet-ssd 到主相机 pipeline
- 添加更多游戏模式
- 优化距离估计精度
- 添加多人检测支持

