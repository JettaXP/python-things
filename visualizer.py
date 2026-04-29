import sys
import os
import numpy as np
import sounddevice as sd
import pygame
import signal
import math
import json
import subprocess
from scipy.interpolate import make_interp_spline

# === ПАРАМЕТРЫ ПЛАВНОСТИ ===
WIDTH, HEIGHT = 800, 300
FPS = 60
NUM_BANDS = 22
SMOOTH_UP = 0.12       # Медленный взлет
SMOOTH_DOWN = 0.03     # Очень плавное оседание
AMPLIFICATION = 2.5    # Умеренное усиление
NOISE_GATE = 0.005     # Отсечение шума
# ==========================

def get_matugen_color():
    """Получает текущий первичный цвет из matugen напрямую."""
    try:
        # Запрашиваем у matugen текущую схему в формате JSON
        res = subprocess.run(['matugen', 'color', 'hex', '#ffffff', '--dry-run', '-j', 'hex'], 
                             capture_output=True, text=True, timeout=1)
        data = json.loads(res.stdout)
        # Путь в JSON matugen: colors -> dark -> primary
        hex_color = data['colors']['dark']['primary'].lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception as e:
        print(f"Matugen error: {e}")
        return (120, 160, 255) # Приятный дефолт

def find_monitor_device():
    """Ищет точное устройство мониторинга системного звука."""
    try:
        # 1. Получаем имя текущего выхода
        sink = subprocess.check_output(['pactl', 'get-default-sink'], text=True).strip()
        # 2. Ищем монитор этого выхода
        sources = subprocess.check_output(['pactl', 'list', 'sources', 'short'], text=True)
        monitor_name = None
        for line in sources.splitlines():
            if sink in line and 'monitor' in line:
                monitor_name = line.split()[1]
                break
        
        if monitor_name:
            devices = sd.query_devices()
            for i, d in enumerate(devices):
                if monitor_name in d['name']:
                    return i
    except: pass
    return None

def get_bands(fft_data, num_bands):
    if len(fft_data) < 20: return np.zeros(num_bands)
    limit = int(len(fft_data) * 0.3)
    indices = np.linspace(2, limit, num_bands + 1).astype(int)
    return np.array([np.mean(fft_data[indices[i]:indices[i+1]]) if indices[i] < indices[i+1] else 0 for i in range(num_bands)])

def main():
    pygame.init()
    # Обычное окно, чтобы WM мог его затайлить
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Liquid Visualizer")
    clock = pygame.time.Clock()

    audio_buffer = np.zeros(4096)
    def callback(indata, frames, time, status):
        nonlocal audio_buffer
        audio_buffer = indata[:, 0]

    dev_id = find_monitor_device()
    
    try:
        sr = 44100
        if dev_id is not None:
            sr = int(sd.query_devices(dev_id)['default_samplerate'])
        stream = sd.InputStream(callback=callback, channels=1, samplerate=sr, device=dev_id)
        stream.start()
        print(f"Слушаю устройство: {sd.query_devices(dev_id)['name'] if dev_id is not None else 'Default'}")
    except Exception as e:
        print(f"Ошибка аудио: {e}")
        return

    current_bands = np.zeros(NUM_BANDS)
    theme_color = get_matugen_color()
    
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        # 1. Обработка звука
        fft = np.abs(np.fft.rfft(audio_buffer * np.hanning(len(audio_buffer))))
        
        if np.max(fft) < NOISE_GATE:
            raw = np.zeros(NUM_BANDS)
        else:
            raw = get_bands(fft, NUM_BANDS) * AMPLIFICATION

        # 2. Сглаживание (Экспоненциальное)
        for i in range(NUM_BANDS):
            if raw[i] > current_bands[i]:
                current_bands[i] = current_bands[i] * (1 - SMOOTH_UP) + raw[i] * SMOOTH_UP
            else:
                current_bands[i] = current_bands[i] * (1 - SMOOTH_DOWN) + raw[i] * SMOOTH_DOWN

        # 3. Отрисовка
        w, h = screen.get_size()
        screen.fill((15, 15, 20)) # Глубокий темный фон

        x_pts = np.linspace(0, w, NUM_BANDS + 2)
        y_pts = np.concatenate(([0], current_bands * h * 0.8, [0]))
        
        x_smooth = np.linspace(0, w, 200)
        try:
            spline = make_interp_spline(x_pts, y_pts, k=3)
            y_smooth = np.clip(spline(x_smooth), 0, h - 5)
        except:
            y_smooth = np.zeros_like(x_smooth)

        # Рисуем волну
        points = [(0, h)]
        for x, y in zip(x_smooth, y_smooth):
            points.append((x, h - y))
        points.append((w, h))

        # Тело волны (цвет из matugen)
        pygame.draw.polygon(screen, theme_color, points)
        
        # Контур (белый блик)
        line_pts = [(x, h - y) for x, y in zip(x_smooth, y_smooth)]
        if len(line_pts) > 1:
            pygame.draw.lines(screen, (255, 255, 255), False, line_pts, 2)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
