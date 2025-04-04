FROM python:3.9-slim

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    libgtk2.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the Streamlit app
CMD ["streamlit", "run", "web.py", "--server.port=8080", "--server.address=0.0.0.0"]
