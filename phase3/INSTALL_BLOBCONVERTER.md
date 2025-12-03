# 安装 blobconverter 以启用人员检测和深度支持

## 问题

如果你看到以下错误：
```
Warning: blobconverter not available. Install with: pip install blobconverter
Person detection will be disabled.
[OAKDCamera] Error setting up DepthAI detection: blobconverter required for person detection
```

这意味着需要安装 `blobconverter` 来使用 OAKD 相机的边缘 AI 人员检测功能。

## 解决方案

### 安装 blobconverter

在 Raspberry Pi 上运行：

```bash
pip install blobconverter
```

如果在虚拟环境中：

```bash
# 激活虚拟环境
source env/bin/activate  # 或你的虚拟环境路径

# 安装 blobconverter
pip install blobconverter
```

### 验证安装

```bash
python -c "import blobconverter; print('blobconverter installed successfully')"
```

## 安装后

重新运行 phase3_demo.py，你应该看到：

```
[OAKDCamera] Camera initialized successfully with DepthAI person detection and depth support
```

而不是：

```
[OAKDCamera] Camera initialized with MediaPipe person detection fallback (no depth)
```

## 关于深度支持

OAKD Lite 使用双目立体视觉来获取深度图。安装 `blobconverter` 后，深度支持应该会自动启用（如果相机支持 stereo depth）。

如果仍然没有深度支持，可能是因为：
1. 相机型号不支持 stereo depth（某些型号只有 RGB）
2. 需要检查相机的实际硬件配置

## 临时解决方案

如果没有安装 blobconverter，程序会回退到 MediaPipe 人员检测（在 Raspberry Pi CPU 上运行），但会失去：
- 边缘 AI 性能优势（检测在相机 VPU 上运行）
- 深度图支持（需要 DepthAI pipeline）

程序仍然可以运行，只是性能会稍差。

