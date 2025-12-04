# 快速删除命令 - 复制粘贴到 Raspberry Pi

## 一行命令（最简单）

```bash
cd ~/projects/OAKD_camera_project && rm -rf phase1/__pycache__ project-1/__pycache__ && find . -name "*.pyc" -delete && echo "✓ Cleaned!"
```

## 或者删除所有缓存（更彻底）

```bash
cd ~/projects/OAKD_camera_project && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && find . -type f -name "*.pyc" -delete && echo "✓ All cache cleaned!"
```

## 然后重新 pull

```bash
git pull
```

## 如果还有问题

使用 `-f` 强制删除：

```bash
cd ~/projects/OAKD_camera_project
rm -rf phase1/__pycache__ project-1/__pycache__
git pull
```

