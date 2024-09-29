import os
from flask import Flask, render_template, send_file

app = Flask(__name__)

# Function to extract audio file paths and song information from a text file
# 텍스트 파일에서 오디오 파일 경로와 곡명 정보를 추출하는 함수
def extract_audio_files(file_list_path):
    audio_files = []
    # 파일 목록이 적힌 파일 열기 (utf-8!)
    with open(file_list_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:       # 앞뒤 공백 제거
            line = line.strip()  # Remove leading and trailing whitespace
            if '*file*' in line:  # Identify path with '*file*'
                                  # '*file*' 이후의 경로만 추출
                file_path = line.split('*file*')[1]  # Extract the path after '*file*'
                                                     # 절대 경로로 변환
                # 파일명만 추출 (.확장자 제거)
                absolute_file_path = os.path.abspath(file_path)  # Convert to absolute path
                # 노래명 표시(경로를 제거하고 표시할 수 있음.)
                # Extract only the file name (remove the extension)
                file_name = os.path.splitext(os.path.basename(absolute_file_path))[0]
                
                # Display the song name (remove unnecessary path information)
                cleaned_file_name = file_name.split('. ', 1)[-1] if '. ' in file_name else file_name
 
                audio_files.append({'path': absolute_file_path, 'name': cleaned_file_name})  # Save the absolute path and cleaned song name
    return audio_files
# 오디오 파일이 포함된 텍스트 파일 경로
# Path to the text file containing audio files
                                        # 실제 경로로 변경하세요 대부분 여기만 손을 봐서 사용할겁니다.
file_list_path = 'audio_file_list.txt'  # Change to the actual path
audio_files = extract_audio_files(file_list_path)
# HTML 렌더링
# Render HTML
@app.route('/')
def index():
    return render_template('index.html', audio_files=audio_files)
# 오디오 파일 전송
# Serve audio files
@app.route('/audio/<filename>')
def get_audio(filename):
    # filename에서 경로 탐색 방지를 위한 보안 처리
    # Security check to prevent path traversal attacks with the filename
    # (filename의 값이 audio_files의 각 path 내에 존재한다면)
    file_info = next((f for f in audio_files if os.path.basename(f['path']) == filename), None)
    if file_info and os.path.exists(file_info['path']):
        return send_file(file_info['path'], as_attachment=False)
    return "File not found", 404

if 0:
    print(0);

if __name__ == '__main__':
    app.run(debug=True)