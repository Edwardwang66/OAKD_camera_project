# Dockerfile for Phase 2: Person Following Demo
# Avoids Qt/X11 display conflicts by running headless or with proper backend configuration

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libusb-1.0-0 \
    libgl1 \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY phase2/requirements.txt ./phase2/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir \
    opencv-python-headless>=4.8.0 \
    numpy>=1.24.0 \
    depthai>=2.23.0 \
    blobconverter>=1.0.0 \
    mediapipe>=0.10.0

# Copy project files
COPY phase2/ /app/phase2/
COPY utils.py /app/utils.py

# Set environment variables to avoid Qt conflicts
ENV QT_QPA_PLATFORM=offscreen
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0
ENV DISPLAY=""
ENV PYTHONUNBUFFERED=1

# Set Python path
ENV PYTHONPATH=/app:/app/phase2

# Create udev rules directory for OAKD camera
RUN mkdir -p /etc/udev/rules.d

# Default command (can be overridden)
CMD ["python", "phase2/phase2_demo.py", "--simulation"]

