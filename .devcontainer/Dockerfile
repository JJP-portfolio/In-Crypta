FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV SDL_VIDEODRIVER=x11
ENV SDL_AUDIODRIVER=pulse

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libsdl2-gfx-1.0-0 \
    libportaudio2 \
    libjack0 \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/In-Crypta

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6080 5900

CMD ["bash", "-c", "Xvfb :99 -screen 0 1280x720x24 & sleep 1 && DISPLAY=:99 x11vnc -display :99 -forever -shared -rfbport 5900 -bg -nopw -listen 0.0.0.0 & sleep 1 && websockify --web=/usr/share/novnc/ 6080 localhost:5900 --daemon & sleep 1 && DISPLAY=:99 python main.py"]
