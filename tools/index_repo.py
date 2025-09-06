# index_repo.py - Low-memory indexer (4MB 파일 제한)
import os, re, json, math, argparse, sys

EXTS = {'.java', '.xml', '.properties', '.yml', '.yaml', '.jsp', '.md'}
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[\uAC00-\uD7A3]+")

MAX_CHARS = 800    # 청크 크기 (기본 800자)
OVERLAP = 120      # 겹침 (기본 120자)
MAX_FILE_MB = 4.0  # 이 크기(MB)보다 큰 파일은 스킵

def tokenize(s):
    return TOKEN.findall(s.lower())

def stream_chunks(path, max_chars=MAX_CHARS, overlap=OVERLAP):
    buf, buf_len = [], 0
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            buf.append(line)
            buf_len += len(line)
            if buf_len >= max_chars:
                chunk = ''.join(buf)
                yield chunk
                if overlap > 0 and len(chunk) > overlap:
                    tail = chunk[-overlap:]
                    buf, buf_len = [tail], len(tail)
                else:
                    buf, buf_len = [], 0
        if buf_len > 0:
            yield ''.join(buf)

def build_index(root):
    docs, df = [], {}
    N, sum_dl = 0, 0.0
    skipped_big, scanned = 0, 0

    for base, _, files in os.walk(root):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if not (ext in EXTS or fn in ('pom.xml','build.gradle','settings.gradle','web.xml')):
                continue

            path = os.path.join(base, fn)
            try:
                size_mb = os.path.getsize(path)/(1024*1024)
            except OSError:
                continue

            scanned += 1
            if size_mb > MAX_FILE_MB:
                skipped_big += 1
                continue

            print("SCAN:", path)

            part = 0
            for ch in stream_chunks(path):
                if not ch.strip(): 
                    continue
                docs.append({
                    "id": len(docs),
                    "path": path,
                    "part": part,
                    "text": ch
                })
                toks = tokenize(ch)
                sum_dl += len(toks)
                for t in set(toks):
                    df[t] = df.get(t, 0) + 1
                N += 1
                part += 1

    avgdl = (sum_dl/N) if N else 0
    idf = {t: math.log(1 + (N - v + 0.5)/(v + 0.5)) for t,v in df.items()} if N else {}

    index = {"docs": docs, "avgdl": avgdl, "idf": idf}
    with open("code_index.json","w",encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)
    print(f"Indexed {N} chunks from {scanned} files (skipped big: {skipped_big}) -> code_index.json")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,help="소스 루트 폴더")
    args=ap.parse_args()
    try:
        build_index(args.root)
    except MemoryError:
        print("[FATAL] 메모리 부족, MAX_FILE_MB/청크 크기를 줄이세요.", file=sys.stderr)
        sys.exit(1)
