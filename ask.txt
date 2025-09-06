# ask.py - 표준 라이브러리만 사용(HTTP도 urllib)
import json, argparse, math, urllib.request

K1, B = 1.5, 0.75
MAX_SNIPPETS = 3
SYSTEM_PROMPT = """너는 Spring/eGovFrame에 능숙한 시니어 자바 개발자다.
내가 주는 '프로젝트 스니펫들'을 근거로:
1) 문제 원인/맥락, 2) 수정 코드(diff 또는 코드블록), 3) 영향/테스트 포인트, 4) 대안을 제시하라.
한국어로, 근거 파일경로와 스니펫 번호를 표기하되, **스니펫 원문을 길게 복사하지 말고 필요한 부분만 짧게 인용**하라.
"""

def bm25_rank(index, query):
    q_toks = tokenize(query)
    idf = index["idf"]
    docs = index["docs"]
    with open("code_index_meta.tmp", "w") as _:
        pass
    # 문서 길이/토큰 캐시
    scores = [0.0]*len(docs)
    avgdl = index["avgdl"] or 1.0
    for doc_id, d in enumerate(docs):
        toks = tokenize(d["text"])
        dl = len(toks) or 1
        tf = {}
        for t in toks: tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for t in q_toks:
            if t not in tf: continue
            t_idf = idf.get(t, 0.0)
            numer = tf[t]*(K1+1)
            denom = tf[t] + K1*(1 - B + B*dl/avgdl)
            s += t_idf * (numer/denom)
        scores[doc_id] = s
    ranked = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)
    top = [(docs[i], scores[i]) for i in ranked[:MAX_SNIPPETS]]
    return top

import re
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[\uAC00-\uD7A3]+")
def tokenize(s):
    s = s.lower()
    return TOKEN.findall(s)

def call_llm_chat(url, model, messages, max_tokens=1200, temperature=0.2):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False   # ★ 추가
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True, help="질문")
    ap.add_argument("--model", default="llama.cpp", help="모델 이름 라벨 (표시용)")
    ap.add_argument("--index", default="code_index.json", help="인덱스 파일")
    ap.add_argument("--api", default="http://127.0.0.1:11434/v1/chat/completions", help="LLM API")
    args = ap.parse_args()

    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)

    top = bm25_rank(index, args.q)
    context_parts = []
    for i, (d, sc) in enumerate(top, 1):
        header = f"[SNIPPET {i}] path={d['path']} part={d['part']} score={round(sc,3)}"
        body = d["text"]
        context_parts.append(header + "\n" + body)

    context = "\n\n".join(context_parts)
    user_msg = f"""[질문]
{args.q}

[프로젝트 스니펫들]
{context}

[요구사항]
- 위 스니펫들만 근거로 답변.
- 수정안은 코드블록 또는 unified diff 형태로.
- 어떤 파일 어느 부분인지(파일경로/스니펫 번호) 근거 표기.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]
    out = call_llm_chat(args.api, args.model, messages)
    try:
        print(out["choices"][0]["message"]["content"])
    except:
        print(out)
