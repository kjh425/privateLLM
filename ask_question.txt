@echo off
REM ==== 설정값 ====
set "TOOLS_DIR=C:\llm\tools"
REM llama.cpp 기본 API
set "API_URL=http://127.0.0.1:8000/v1/chat/completions"
REM Ollama를 쓰는 경우(오프라인 수동 임포트 후):
REM set "API_URL=http://127.0.0.1:11434/v1/chat/completions"

cd /d "%TOOLS_DIR%"

if not exist "%TOOLS_DIR%\ask.py" (
  echo [ERROR] ask.py 가 없습니다: %TOOLS_DIR%
  pause
  exit /b 1
)

if not exist "%TOOLS_DIR%\code_index.json" (
  echo [WARN] code_index.json 이 없습니다. 먼저 build_index.bat 를 실행하세요.
  pause
  exit /b 1
)

echo == 질문 실행 ==
set /p USERQ=질문을 입력하세요(^>^): 
if "%USERQ%"=="" (
  echo [INFO] 질문이 비어 있습니다. 종료합니다.
  exit /b 0
)

echo.
echo [INFO] LLM 호출 중...
python "%TOOLS_DIR%\ask.py" --q "%USERQ%" --api "%API_URL%"
echo.
pause
