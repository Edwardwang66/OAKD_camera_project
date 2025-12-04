# 快速清理 Python 缓存

## 在 Raspberry Pi 上运行（复制粘贴）

```bash
cd ~/projects/OAKD_camera_project
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

## 或者一行命令

```bash
cd ~/projects/OAKD_camera_project && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && find . -type f -name "*.pyc" -delete && echo "✓ Done!"
```

## 然后重新 pull

```bash
git pull
```

