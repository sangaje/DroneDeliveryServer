from pathlib import Path
import re

src = "response.txt"  # 첨부 파일 경로
out_dir = Path("extracted_images")
out_dir.mkdir(exist_ok=True)

with open(src, "rb") as f:
    data = f.read()

# boundary 추출: 본문에 나타난 첫 경계 라인을 찾아 사용
m = re.search(rb"\r?\n--([!-~]{1,70})\r?\n", data)  # RFC 2046: 1~70 chars, 7bit
if not m:
    # 파일 시작이 곧바로 경계일 수 있어 선행 개행 없이도 탐색
    m = re.search(rb"^--([!-~]{1,70})\r?\n", data)
if not m:
    raise RuntimeError("boundary를 찾지 못했습니다.")

boundary = b"--" + m.group(1)
final_boundary = boundary + b"--"

# 바디를 경계로 split (선행 프롤로그 제거)
parts_blob = data.split(boundary)
images = []

for part in parts_blob:
    part = part.lstrip(b"\r\n")
    if not part or part.startswith(b"--"):
        continue  # 에필로그 또는 빈 파트

    # 헤더/바디 분리
    if b"\r\n\r\n" in part:
        header_blob, body = part.split(b"\r\n\r\n", 1)
    elif b"\n\n" in part:
        header_blob, body = part.split(b"\n\n", 1)
    else:
        continue

    headers = header_blob.decode("utf-8", "ignore").splitlines()
    ctype = ""
    filename = None

    for h in headers:
        h_low = h.lower()
        if h_low.startswith("content-type"):
            # 예: Content-Type: image/png
            if ":" in h:
                ctype = h.split(":", 1)[1].strip().lower()
        if h_low.startswith("content-disposition"):
            # 예: Content-Disposition: inline; name=image; filename=capture.png
            mfn = re.search(r'filename="?([^";]+)"?', h, flags=re.IGNORECASE)
            if mfn:
                filename = mfn.group(1)

    if (
        ctype.startswith("image/png")
        or ctype.startswith("image/jpeg")
        or ctype.startswith("image/jpg")
    ):
        if not filename:
            filename = "image.bin"
        # 트레일링 CRLF 제거 가능성 고려
        body = body.rstrip(b"\r\n")
        out_path = out_dir / filename
        with open(out_path, "wb") as wf:
            wf.write(body)

        # 간단한 매직 넘버 검증
        ok = False
        if body.startswith(b"\x89PNG\r\n\x1a\n"):
            ok = True
        elif body.startswith(b"\xff\xd8\xff"):
            ok = True
        images.append((str(out_path), ctype, ok))

print("Extracted:", images)
