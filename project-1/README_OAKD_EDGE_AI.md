# OAKD Edge AI 使用指南

本指南说明如何在OAKD相机内置算力上运行手势识别模型，并使用bounding box进行检测。

## OAKD相机内置算力

OAKD Lite相机内置Myriad X VPU，可以在设备端运行深度学习模型，实现：
- **降低主机计算负担**
- **提高实时性能**
- **减少延迟**

## 功能特性

1. **Hand Detection with Bounding Box**
   - 使用MediaPipe检测手部
   - 返回bounding box坐标 (x, y, w, h)
   - 在图像上绘制bounding box

2. **模型推理基于Bounding Box**
   - 根据bounding box裁剪手部区域
   - 将裁剪区域输入模型进行分类
   - 提高识别准确率

3. **Edge AI支持（可选）**
   - 将PyTorch模型转换为Blob格式
   - 在OAKD相机上直接运行推理
   - 完全利用相机内置算力

## 使用方法

### 1. 基本使用（带Bounding Box）

```bash
cd project-1
python main.py
```

程序会自动：
- 检测手部并绘制bounding box
- 根据bounding box裁剪手部区域
- 使用模型对裁剪区域进行分类

### 2. 转换模型为Blob格式（Edge AI）

#### 步骤1: 安装依赖

```bash
pip install openvino blobconverter
```

#### 步骤2: 转换模型

```bash
# 方法1: 使用转换脚本
python convert_model_to_blob.py --model rps_model_improved.pth

# 方法2: 使用在线转换器
# 访问: https://blobconverter.luxonis.com/
# 上传ONNX文件进行转换
```

#### 步骤3: 使用Edge AI模式

```python
from oakd_edge_ai import OAKDEdgeAICamera

# 初始化Edge AI相机
camera = OAKDEdgeAICamera(
    model_blob_path="rps_model_improved.blob",
    use_hand_detection=True
)

# 获取带检测结果的帧
frame, bboxes, nn_results = camera.get_frame_with_detection()
```

## 代码结构

### 主要文件

1. **`oakd_hand_detector.py`**
   - Hand detection with bounding boxes
   - 返回 (x, y, w, h) 坐标

2. **`oakd_edge_ai.py`**
   - OAKD Edge AI相机接口
   - 支持在相机上运行神经网络

3. **`convert_model_to_blob.py`**
   - PyTorch模型转Blob格式工具
   - 支持ONNX和OpenVINO转换

4. **`hand_gesture_detector_model.py`**
   - 已更新支持bounding box
   - 根据bbox裁剪区域进行分类

## Bounding Box工作流程

```
1. 相机捕获帧
   ↓
2. Hand Detector检测手部
   ↓
3. 返回Bounding Box (x, y, w, h)
   ↓
4. 根据BBox裁剪手部区域
   ↓
5. 将裁剪区域输入模型
   ↓
6. 模型分类 (Rock/Paper/Scissors)
   ↓
7. 显示结果和Bounding Box
```

## Edge AI工作流程

```
1. PyTorch模型 (.pth)
   ↓
2. 转换为ONNX格式
   ↓
3. 转换为OpenVINO IR
   ↓
4. 转换为Blob格式 (.blob)
   ↓
5. 部署到OAKD相机
   ↓
6. 在Myriad X VPU上运行
```

## 模型转换示例

```python
# 转换PyTorch模型到Blob
python convert_model_to_blob.py \
    --model rps_model_improved.pth \
    --output rps_model.blob \
    --input-size 64 64
```

## 性能优势

使用OAKD Edge AI的优势：

- **延迟降低**: 模型在相机上运行，无需传输到主机
- **CPU释放**: 主机CPU可用于其他任务
- **实时性**: 更高的帧率和响应速度
- **功耗优化**: 专用VPU比CPU更高效

## 注意事项

1. **模型格式**: 需要将PyTorch模型转换为Blob格式
2. **输入尺寸**: 确保模型输入尺寸匹配 (默认64x64)
3. **兼容性**: 某些模型架构可能不支持Edge AI
4. **Fallback**: 如果Edge AI不可用，会自动回退到CPU推理

## 故障排除

### Bounding Box未显示
- 检查手部是否在画面中
- 确保光线充足
- 调整MediaPipe检测阈值

### Edge AI模型加载失败
- 检查Blob文件路径
- 验证模型格式是否正确
- 查看OAKD相机连接状态

### 转换失败
- 确保安装了OpenVINO
- 检查模型架构兼容性
- 尝试使用在线转换器

## 参考资源

- [DepthAI文档](https://docs.luxonis.com/)
- [Blob Converter](https://blobconverter.luxonis.com/)
- [OpenVINO工具包](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/overview.html)

