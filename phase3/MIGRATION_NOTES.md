# Phase 3 迁移说明

Phase 3 的文件已经从 `phase2/` 目录移动到 `phase3/` 目录。

## 文件结构

Phase 3 的文件现在位于：
```
phase3/
├── phase3_demo.py          # 主演示程序
├── obstacle_detector.py    # 障碍物检测模块
├── obstacle_avoider.py     # 避障控制模块
├── README.md               # Phase 3 概述
├── README_PHASE3.md        # 详细文档
├── QUICK_FIX.md            # 快速修复指南
├── RUN_WITHOUT_CRASHING.md # 避免崩溃说明
├── INSTALL_BLOBCONVERTER.md # 安装指南
├── FIX_DISPLAY_ISSUE.md    # 显示问题修复
├── requirements.txt        # 依赖列表
├── start_phase3.sh         # 启动脚本
├── run_phase3_no_gui.sh    # 无GUI启动脚本
└── fix_opencv_display.sh   # 显示修复脚本
```

## 依赖关系

Phase 3 依赖于 Phase 2 中的共享模块：
- `oakd_camera.py` - OAKD相机接口
- `car_controller.py` - 车辆控制接口
- `person_follower.py` - 人员跟踪控制逻辑

这些模块仍然位于 `phase2/` 目录中，Phase 3 会自动从那里导入。

## 使用方法

运行 Phase 3：

```bash
cd phase3
python phase3_demo.py --simulation --no-gui
```

程序会自动从 `../phase2/` 导入共享模块。

## 导入路径

`phase3_demo.py` 中的导入路径已经更新为：
1. 首先添加父目录（项目根目录）到路径（用于 `utils.py`）
2. 然后添加 `phase2/` 目录到路径（用于共享模块）

这样 Phase 3 可以：
- 从项目根目录导入 `utils`
- 从 `phase2/` 导入共享模块（`oakd_camera`, `car_controller`, `person_follower`）
- 从 `phase3/` 导入自己的模块（`obstacle_detector`, `obstacle_avoider`）

## 注意事项

- Phase 2 的文件保持不变，仍然在 `phase2/` 目录中
- Phase 3 依赖于 Phase 2 的共享模块，所以两个目录都需要存在
- 如果修改了 Phase 2 的共享模块，Phase 3 会自动使用更新后的版本

