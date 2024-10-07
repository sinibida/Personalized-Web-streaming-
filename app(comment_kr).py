from flask import Flask, Response, send_file, render_template
import subprocess
import threading
import time
import os
import random
import copy
from mutagen import File
from PIL import Image
import io

app = Flask(__name__)

# 청크 크기 설정
CHUNK_SIZE = 1024  # 1KB

# 최대 실행 가능한 프로세스 수와 프로세스 목록 설정
max_processes = 80
process_list = []
process_list_lock = threading.Lock()
stop_event = threading.Event()

# 오디오 파일 목록을 추출하는 함수
def extract_audio_files(file_list_path):
    audio_files = []
    with open(file_list_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if "*file*" in line:
                file_path = line.split("*file*")[1]
                absolute_file_path = os.path.abspath(file_path)
                audio_files.append({"path": absolute_file_path, "name": os.path.basename(absolute_file_path)})
    return audio_files

# 프로세스 목록 관리 함수
def manage_process_list():
    global process_list
    with process_list_lock:
        process_list = [(proc, last_access) for proc, last_access in process_list if proc.poll() is None]
    print(f"현재 실행 중인 프로세스 수: {len(process_list)}")

# 비활성 프로세스 종료 스레드 함수
def terminate_inactive_processes():
    global process_list
    while not stop_event.is_set():
        current_time = time.time()
        with process_list_lock:
            for proc, last_access in process_list[:]:
                if current_time - last_access > 300 and proc.poll() is None:
                    proc.terminate()
                    proc.wait()
                    print(f"비활성 프로세스 종료됨. 종료된 프로세스의 종료 코드: {proc.returncode}")
                    process_list.remove((proc, last_access))
        time.sleep(30)

# 비활성 프로세스 종료 스레드 시작
cleanup_thread = threading.Thread(target=terminate_inactive_processes, daemon=True)
cleanup_thread.start()

file_list_path = r"C:\vscode\개인 프로젝트3\audio_file_list.txt"
audio_files = extract_audio_files(file_list_path)
shuffled_audio_files = copy.deepcopy(audio_files)
random.shuffle(shuffled_audio_files)

# 홈 페이지 경로 설정 - audio_files 전달
@app.route("/")
def index():
    return render_template("index.html", audio_files=shuffled_audio_files)

# 오디오 스트리밍 경로
@app.route("/audio/<filename>")
def stream_audio(filename):
    manage_process_list()
    if len(process_list) >= max_processes:
        return "Maximum number of processes running. Try again later.", 429

    file_info = next((f for f in shuffled_audio_files if os.path.basename(f["path"]) == filename), None)
    if file_info and os.path.exists(file_info["path"]):
        print(f"Streaming file: {file_info['path']}")

        def generate():
            file_path = os.path.abspath(file_info["path"])
            command = ['ffmpeg', '-i', file_path, '-map', '0:a', '-f', 'flac', '-c:a', 'flac', '-threads', '4', '-']
            current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_list.append((current_process, time.time()))

            try:
                while True:
                    chunk = current_process.stdout.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk

                    for i, (proc, last_access) in enumerate(process_list):
                        if proc == current_process:
                            process_list[i] = (proc, time.time())

            except Exception as e:
                print(f"Error while streaming: {e}")

            finally:
                current_process.stdout.close()
                current_process.wait()
                error = current_process.stderr.read().decode(errors="ignore")
                if current_process.returncode != 0:
                    print(f"FFmpeg error (Exit Code {current_process.returncode}): {error}")
                manage_process_list()

        return Response(generate(), mimetype="audio/flac")

    return "File not found", 404

# 앨범 커버 추출
def extract_album_cover(file_path):
    audio = File(file_path)
    if "APIC:" in audio.tags:
        cover_data = audio.tags["APIC:"].data
        return Image.open(io.BytesIO(cover_data))
    return None

# 앨범 커버 제공 경로
@app.route("/cover/<filename>")
def get_album_cover(filename):
    file_info = next((f for f in shuffled_audio_files if os.path.basename(f["path"]) == filename), None)
    if file_info:
        cover_image = extract_album_cover(file_info["path"])
        if cover_image:
            img_io = io.BytesIO()
            cover_image.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype="image/png")
    return "No cover available", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, threaded=True, port=8000)
