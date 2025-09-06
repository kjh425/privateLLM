@echo off
REM ==== 설정값 ====
set "TOOLS_DIR=C:\llm\tools"
REM 레거시 프로젝트 루트 폴더 경로를 아래에 지정하세요
set "PROJECT_DIR=D:\workspace\legacy-spring"

cd /d "%TOOLS_DIR%"
if not exist "%TOOLS_DIR%\index_repo.py" (
  echo [ERROR] index_repo.py 가 없습니다: %TOOLS_DIR%
  pause
  exit /b 1
)

if not exist "%PROJECT_DIR%" (
  echo [ERROR] 프로젝트 폴더가 없습니다: %PROJECT_DIR%
  echo 경로를 build_index.bat 상단에서 수정하세요.
  pause
  exit /b 1
)

echo == 코드 인덱싱 시작 ==
echo 대상: %PROJECT_DIR%
echo.

python "%TOOLS_DIR%\index_repo.py" --root "%PROJECT_DIR%"
if errorlevel 1 (
  echo [ERROR] 인덱싱 실패
  pause
  exit /b 1
)

if exist "%TOOLS_DIR%\code_index.json" (
  echo.
  echo [OK] 인덱싱 완료: %TOOLS_DIR%\code_index.json
) else (
  echo [WARN] code_index.json 이 생성되지 않았습니다. 오류 로그를 확인하세요.
)
pause
