@echo off
REM ==== 설정값 ====
set "LLM_DIR=C:\llm\llama.cpp"
set "MODEL_PATH=C:\llm\models\qwen2.5-coder-7b-instruct-q5_k_m.gguf"
set "PORT=8000"
set "HOST=127.0.0.1"
set "CTX=8192"

cd /d "%LLM_DIR%"
if not exist "%MODEL_PATH%" (
  echo [ERROR] 모델 파일이 없습니다: %MODEL_PATH%
  echo C:\llm\models\ 아래에 .gguf 모델을 넣고 경로를 수정하세요.
  pause
  exit /b 1
)

echo == LLM 서버 기동 ==
echo 모델: %MODEL_PATH%
echo 포트: %HOST%:%PORT%  컨텍스트: %CTX%  스레드: %NUMBER_OF_PROCESSORS%
echo.

server.exe -m "%MODEL_PATH%" -c %CTX% -t %NUMBER_OF_PROCESSORS% -p %PORT% --host %HOST%
