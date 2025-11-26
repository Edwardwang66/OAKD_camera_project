# OAKD Edge AI + Bounding Box 实现总结

## ✅ 已完成的功能

### 1. Bounding Box 检测
- ✅ **Hand Detection**: 使用 MediaPipe 检测手部
- ✅ **Bounding Box 返回**: 返回 (x, y, w, h) 坐标
- ✅ **可视化**: 在图像上绘制 bounding box
- ✅ **模型输入**: 根据 bounding box 裁剪手部区域进行分类

### 2. OAKD Edge AI 支持
- ✅ **Edge AI 接口**: 创建了 `OAKDEdgeAICamera` 类
- ✅ **模型转换工具**: `convert_model_to_blob.py` 用于转换模型
- ✅ **Blob 格式支持**: 支持在 OAKD 相机上运行模型

### 3. 代码更新
- ✅ **hand_gesture_detector_model.py**: 已更新支持 bounding box
- ✅ **main.py**: 集成 bounding box 检测和显示
- ✅ **oakd_hand_detector.py**: 专门的手部检测器，返回 bounding box

## 📁 新增文件

1. **`oakd_edge_ai.py`**
   - OAKD Edge AI 相机接口
   - 支持在相机内置 VPU 上运行模型

2. **`oakd_hand_detector.py`**
   - 手部检测器，返回 bounding box
   - 支持裁剪手部区域

3. **`convert_model_to_blob.py`**
   - PyTorch 模型转 Blob 格式工具
   - 支持 ONNX 和 OpenVINO 转换

4. **`README_OAKD_EDGE_AI.md`**
   - Edge AI 使用指南（中文）

5. **`USAGE_BBOX.md`**
   - Bounding Box 使用说明（中文）

## 🔄 工作流程

### 当前实现（CPU推理 + Bounding Box）

```
相机帧 (640x480)
  ↓
MediaPipe 手部检测
  ↓
获取 Bounding Box (x, y, w, h)
  ↓
根据 BBox 裁剪手部区域
  ↓
调整大小到 64x64
  ↓
PyTorch 模型分类 (CPU)
  ↓
返回结果和 Bounding Box
```

### Edge AI 实现（OAKD VPU推理）

```
相机帧 (OAKD)
  ↓
Hand Detection Model (OAKD VPU) - 可选
  ↓
获取 Bounding Box
  ↓
裁剪手部区域
  ↓
Gesture Classification Model (OAKD VPU)
  ↓
返回结果（无需传输到主机）
```

## 🚀 使用方法

### 基本使用（带 Bounding Box）

```bash
cd project-1
python main.py
```

程序会自动：
1. 检测手部并显示 bounding box（绿色框）
2. 根据 bounding box 裁剪区域
3. 使用模型对裁剪区域进行分类
4. 显示识别结果

### Edge AI 使用（需要转换模型）

```bash
# 1. 转换模型
python convert_model_to_blob.py --model rps_model_improved.pth

# 2. 使用 Edge AI 模式（需要修改代码使用 OAKDEdgeAICamera）
```

## 📊 Bounding Box 格式

返回格式：`(x, y, width, height)`

- **x, y**: 左上角坐标
- **width, height**: 边界框尺寸
- **包含 padding**: 默认 20-30 像素，确保完整手部区域

## 🎯 优势

### Bounding Box 的优势
1. ✅ **提高准确率**: 只对相关区域分类
2. ✅ **减少干扰**: 排除背景
3. ✅ **性能优化**: 处理更小区域
4. ✅ **可视化**: 清楚显示检测区域

### Edge AI 的优势
1. ✅ **低延迟**: 模型在相机上运行
2. ✅ **释放CPU**: 主机CPU用于其他任务
3. ✅ **实时性**: 更高帧率
4. ✅ **功耗优化**: VPU比CPU更高效

## 📝 下一步（可选）

如果要完全使用 OAKD Edge AI：

1. **转换模型为 Blob**
   ```bash
   python convert_model_to_blob.py --model rps_model_improved.pth
   ```

2. **使用在线转换器**
   - 访问: https://blobconverter.luxonis.com/
   - 上传 ONNX 文件
   - 下载 .blob 文件

3. **修改代码使用 Edge AI**
   ```python
   from oakd_edge_ai import OAKDEdgeAICamera
   
   camera = OAKDEdgeAICamera(
       model_blob_path="rps_model_improved.blob",
       use_hand_detection=True
   )
   ```

## ⚠️ 注意事项

1. **模型转换**: Blob 格式需要特定的模型架构支持
2. **输入尺寸**: 确保模型输入尺寸匹配（默认 64x64）
3. **Fallback**: 如果 Edge AI 不可用，自动回退到 CPU 推理
4. **兼容性**: 某些复杂模型可能不支持 Edge AI

## 📚 文档

- **README_OAKD_EDGE_AI.md**: Edge AI 详细指南
- **USAGE_BBOX.md**: Bounding Box 使用说明
- **README.md**: 项目主文档

