import requests
import time
import re
import sys
import os
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter_print(text, duration, start_timestamp, song_start_time):
    if not text: return
    n = len(text)
    target_duration = duration * 0.8
    for i, char in enumerate(text):
        char_target_time = start_timestamp + (i / n) * target_duration
        current_elapsed = time.time() - song_start_time
        wait_time = char_target_time - current_elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        sys.stdout.write(char)
        sys.stdout.flush()
    print()

def animate_dots(duration, song_start_time, target_timestamp):
    frames = [". . .", ". .  ", ".    ", ". .  "]
    idx = 0
    while True:
        current_elapsed = time.time() - song_start_time
        remaining = target_timestamp - current_elapsed
        if remaining <= 0.1: break
        sys.stdout.write(f"\r {frames[idx % len(frames)]} ")
        sys.stdout.flush()
        time.sleep(0.3)
        idx += 1
    sys.stdout.write("\r       \r")
    sys.stdout.flush()

def parse_lrc(lrc_content):
    if not lrc_content: return []
    lines = []
    pattern = re.compile(r'\[(\d+):(\d+[\.:]\d+)\](.*)')
    for line in lrc_content.splitlines():
        match = pattern.match(line)
        if match:
            minutes = int(match.group(1))
            sec_part = match.group(2).replace(':', '.')
            seconds = float(sec_part)
            text = match.group(3).strip()
            if text and not any(text.lower().startswith(tag) for tag in ['by:', 'al:', 'ar:', 'ti:', 're:', 've:']):
                lines.append((minutes * 60 + seconds, text))
    lines.sort(key=lambda x: x[0])
    return lines

def get_lyrics(query):
    try:
        r = requests.get("https://lrclib.net/api/search", params={"q": query}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                for t in data:
                    if t.get("syncedLyrics"):
                        return t["syncedLyrics"], f"{t['artistName']} - {t['trackName']}"
    except: pass
    try:
        r = requests.get("https://music.163.com/api/search/get/web", params={"s": query, "type": 1, "limit": 1}, timeout=10)
        res = r.json().get("result", {})
        if "songs" in res:
            song = res["songs"][0]
            lr = requests.get("https://music.163.com/api/song/lyric", params={"id": song["id"], "lv": 1}, timeout=10)
            lrc = lr.json().get("lrc", {}).get("lyric")
            if lrc: return lrc, f"{song['artists'][0]['name']} - {song['name']}"
    except: pass
    return None, None

def get_audio_url(query):
    try:
        cmd = ["yt-dlp", f"ytsearch1:{query}", "--get-url", "--format", "bestaudio", "--quiet", "--no-warnings"]
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
    except: return None

def main():
    try:
        song_input = input("󰠃 Введите название песни: ").strip()
        if not song_input: return
        print("󰩊 Ищу песню и текст...")
        lyrics_data, info = get_lyrics(song_input)
        if not lyrics_data:
            print("󰅚 Текст не найден.")
            return
        audio_url = get_audio_url(song_input + " official audio")
        print(f"󰎈 Песня найдена - {info}")
        time.sleep(1.5)
        parsed_lines = parse_lrc(lyrics_data)
        player_proc = None
        if audio_url:
            player_proc = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        clear_screen()
        song_start_time = time.time()
        for i in range(len(parsed_lines)):
            timestamp, text = parsed_lines[i]
            while True:
                current_elapsed = time.time() - song_start_time
                wait = timestamp - current_elapsed
                if wait <= 0: break
                if wait > 1.5:
                    animate_dots(wait, song_start_time, timestamp)
                else:
                    time.sleep(0.01)
            if i < len(parsed_lines) - 1:
                duration = parsed_lines[i+1][0] - timestamp
            else:
                duration = 5.0
            typewriter_print(text, duration, timestamp, song_start_time)
        if player_proc:
            player_proc.wait()
    except (KeyboardInterrupt, EOFError):
        print("\r󰝚 Остановлено. ")
    finally:
        if 'player_proc' in locals() and player_proc:
            player_proc.terminate()

if __name__ == "__main__":
    main()
