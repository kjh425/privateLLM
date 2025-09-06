로컬 LLM + 코드 RAG 세팅 README (Windows/폐쇄망)

이직한 회사가 내부망을 쓰는데 chatGPT 다른컴퓨터에서 쓰고 복붙하는게 너무 귀찮아서 내가 걍 만듬.

USB에서 폐쇄망 PC로 복사 후 아래 구조로 정리:

------------------------------------------------------------------- 프로젝트 구조 -------------------------------------------------------------------

모델이랑 설치파일은 아마 사이즈가 커서 깃에 못올릴듯. https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF?utm_source=chatgpt.com 에 들어가서 내 컴퓨터 스펙에 여유있는 모델로 다운

파이썬 다운경로도 https://www.python.org/downloads/release/python-3137/

ollama 다운경로 https://ollama.com/download

py나 확장자 없는 파일들은 수정할수있도록 txt파일로 샘플 넣어둿는데 수정사항생기면 메모장에서 .* 확장자로 선택해두고 확장자 붙혀서 .py나 "파일이름" 으로 확장자 없이 저장해서 tools/ 경로에 넣으면됨.

C:\llm
models
Meta-Llama-3.1-8B-Instruct-Q3_K_S.gguf (개인PC용) Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf (회사PC용) Meta-Llama-3.1-8B-Instruct-Q6_K_L.gguf (사양높은거(위에모델잘되면쓰려고 넣어둠)) Modelfile-q3.txt Modelfile-q5.txt Modelfile-q3 Modelfile-q5 tools
index_repo.py ask.py agent_apply.py (선택: diff 자동 적용기)

------------------------------------------------------------------- 세팅 -------------------------------------------------------------------

C:\llm\models\Modelfile-q3.txt 파일내용

FROM C:\llm\models\Meta-Llama-3.1-8B-Instruct-Q3_K_S.gguf PARAMETER temperature 0.2 PARAMETER num_ctx 2048 PARAMETER num_gpu_layers 0

이후 확장자 떼고 저장

C:\llm\models\Modelfile-q5.txt 파일내용

FROM C:\llm\models\Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf PARAMETER temperature 0.2 PARAMETER num_ctx 4096 PARAMETER num_gpu_layers 0

이후 확장자 떼고 저장

설치(exe파일 넣어둠.)

Ollama 설치

OllamaSetup.exe 실행 → 기본값으로 설치

Python 설치

python-3.13.x-amd64.exe 실행

꼭!!!! “Add python.exe to PATH” 체크 후 설치

설치 확인: ollama -v python --version

모델 등록 (로컬 이름 만들기)

ollama create <설정할 이름> -f <사용할 모델>

개인PC(램 7~8GB): ollama create my-llama31 -f C:\llm\models\Modelfile-q3

회사PC(램 16~32GB): ollama create my-llama31-q5 -f C:\llm\models\Modelfile-q5

------------------------------------------------------------------- 모델 삭제 ------------------------------------------------------------------- ollama list

출력 예: NAME ID SIZE MODIFIED my-llama31 3d82f19f… 3.4 GB 2025-09-06 11:20:00 my-llama31-q5 b91a01c2… 5.7 GB 2025-09-06 09:45:00

특정 모델 삭제 ollama rm my-llama31

등록 확인: ollama list

------------------------------------------------------------------- 실행 방법 (그냥 LLM 엄청빠름) ------------------------------------------------------------------- 마지막으로 실행방법은 2가지 방법이있는데. 첫번째는, 그냥 실행만 하는방법이다. ollama run <설정한 로컬 llm이름> 예시// ollama run my-llama31

------------------------------------------------------------------- 실행 방법 (프로젝트 기반 LLM) ------------------------------------------------------------------- 두번째는, 내 프로젝트기반으로 답변받기 (엄청느림) 터미널(cmd와 powershell)을 각각 키고 하나(cmd)는 명령어 : ollama serve 또 하나(powershell)는 tools/ 폴더로 가서

(프로젝트 기반 분석) python index_repo.py --root "<플젝경로>" 하게되면 tools/ 하위에 code_index.json 즉 내 프로젝트를 분석한 json파일이 생성된다 (예시) cd /d C:\llm\tools python index_repo.py --root "C:\Users\Admin\Documents\workspace-sts-3.9.17.RELEASE\jhproject"

(질문법) python ask.py --q '<질문할말>' --api "http://127.0.0.1:11434/v1/chat/completions" --model "my-llama31" (예시) python ask.py --q '안녕? 내프로젝트에서 @@@ 에 대해 알려줘' --api "http://127.0.0.1:11434/v1/chat/completions" --model "my-llama31"

------------------------------------------------------------------- 트러블 슈팅 ------------------------------------------------------------------- (오류 해결) Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket address (protocol/network address/port) is normally permitted. 이런식으로 뜰 경우 (이미 ollama가 올라가있는거기때문에 프로세스 종료시킨후 ollama serve로 다시시작)

------------------------------------------------------------------- 기록사항 ------------------------------------------------------------------- (+) 추가사항으로 뭔가 모델의 특성을 바꾸고싶으면 ask.txt 파일이나 index_repo.txt 파일 한번 보고 바꿀거 바꾸고 py파일로 변환해서 tools/ 에 넣고 다시해보자

2025/09/06 - 일단 지금 내 컴퓨터에서 돌려봤는데 03모델인데도 메모리 90퍼 차지함..ㅠㅠ 근데 뭔가 내 코드읽고 말하는거 지리긴함 ㅋㅋ ㅅㄱ
