# Bounding Box 使用说明

## 功能概述

Project-1 现在支持使用 bounding box 进行手势识别：

1. **Hand Detection**: 使用 MediaPipe 检测手部位置
2. **Bounding Box**: 返回手部的边界框坐标 (x, y, w, h)
3. **模型推理**: 根据 bounding box 裁剪手部区域，输入模型进行分类

## 工作流程

```
相机帧
  ↓
MediaPipe 手部检测
  ↓
获取 Bounding Box (x, y, w, h)
  ↓
根据 BBox 裁剪手部区域
  ↓
调整大小到模型输入尺寸 (64x64)
  ↓
模型分类 (Rock/Paper/Scissors)
  ↓
显示结果和 Bounding Box
```

## 代码示例

### 基本使用

```python
from oakd_hand_detector import OAKDHandDetector
from hand_gesture_detector_model import HandGestureDetectorModel

# 初始化检测器
hand_detector = OAKDHandDetector()
gesture_detector = HandGestureDetectorModel()

# 检测手部和手势
frame = camera.get_frame()
bbox, landmarks, annotated = hand_detector.detect_hand_bbox(frame)

if bbox:
    x, y, w, h = bbox
    print(f"Hand detected at: ({x}, {y}), size: {w}x{h}")
    
    # 模型会自动使用 bbox 进行识别
    gesture, result_frame, _ = gesture_detector.detect_gesture(frame)
    print(f"Gesture: {gesture.value}")
```

### 手动裁剪区域

```python
# 获取 bounding box
bbox, _, _ = hand_detector.detect_hand_bbox(frame)

if bbox:
    # 裁剪手部区域
    hand_region = hand_detector.crop_hand_region(frame, bbox)
    
    # 可以保存或进一步处理
    cv2.imwrite("hand_region.jpg", hand_region)
```

## Bounding Box 格式

Bounding box 返回格式：`(x, y, width, height)`

- `x`: 左上角 X 坐标
- `y`: 左上角 Y 坐标  
- `width`: 边界框宽度
- `height`: 边界框高度

包含 padding（默认 20-30 像素）以确保完整的手部区域。

## 可视化

Bounding box 会自动绘制在图像上：
- **绿色框**: MediaPipe 手部检测的 bounding box
- **蓝色框**: 模型输入区域（如果有）
- **手部关键点**: MediaPipe landmarks

## 优势

使用 bounding box 的优势：

1. **提高准确率**: 只对相关区域进行分类
2. **减少干扰**: 排除背景和其他物体
3. **性能优化**: 处理更小的图像区域
4. **可视化**: 清楚显示检测区域

## 在 OAKD Edge AI 上使用

如果要使用 OAKD 内置算力：

1. 转换模型为 Blob 格式
2. 使用 `OAKDEdgeAICamera` 类
3. Bounding box 检测可以在相机上运行（需要手部检测模型）

详见 `README_OAKD_EDGE_AI.md`

