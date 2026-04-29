<div align="center">
  <img src="https://raw.githubusercontent.com/JettaXP/python-things/main/logo.ans" alt="Logo" width="200" style="border-radius: 50%;">
  
  <h1>🐍 python-things</h1>
  <p><i>Крутые пайтон преколы для терминала</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
    <img src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen?style=for-the-badge" alt="Maintained">
  </p>
</div>

---

## 🎵 Lyrics Player (`lyrics_player.py`)

Продвинутый скрипт для прослушивания музыки прямо в терминале с синхронизированными субтитрами (караоке-стайл).

### ✨ Особенности
- **🔍 Умный поиск:** Ищет треки через `yt-dlp` и подтягивает текст через API (lrclib, netease).
- **⏳ Синхронизация:** Текст отображается ровно в тот момент, когда он звучит в песне.
- **🎨 Эффекты:** Анимация "печатающегося текста" и индикатор ожидания.
- **🔊 Фоновое воспроизведение:** Использует `ffplay` для вывода звука.

### 🛠 Зависимости
Для работы скрипта должны быть установлены следующие инструменты:
- [Python 3](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — для поиска аудио.
- [FFmpeg](https://ffmpeg.org/) (включая `ffplay`) — для проигрывания.
- Библиотека `requests`:
  ```bash
  pip install requests
  ```

### 🚀 Запуск
```bash
python lyrics_player.py
```
Просто введи название песни, и наслаждайся вайбом!

---

<div align="center">
  <p>Made with ❤️ by <a href="https://github.com/JettaXP">JettaXP</a></p>
  <img src="https://img.shields.io/badge/Material--You-Inspired-purple?style=flat-square" alt="Material You">
</div>
