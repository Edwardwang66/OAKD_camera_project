# 清理 Python 缓存文件（解决 git pull 冲突）

## 问题

如果看到 git pull 错误：
```
error: The following untracked working tree files would be overwritten by checkout:
        phase1/__pycache__/...
Please move or remove them before you switch branches.
```

## ✅ 快速解决方案

在 Raspberry Pi 上运行：

```bash
cd ~/projects/OAKD_camera_project

# 删除所有 __pycache__ 目录
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 删除所有 .pyc 文件
find . -type f -name "*.pyc" -delete

# 删除所有 .pyo 文件  
find . -type f -name "*.pyo" -delete
```

或者使用提供的脚本：

```bash
cd ~/projects/OAKD_camera_project/display_test
chmod +x clean_cache.sh
./clean_cache.sh
```

## 一行命令（最简单）

```bash
cd ~/projects/OAKD_camera_project && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && find . -type f -name "*.pyc" -delete && echo "Cache cleaned!"
```

## 然后重新 pull

```bash
cd ~/projects/OAKD_camera_project
git pull
```

## 注意

这些缓存文件可以安全删除，Python 会在需要时自动重新生成。

