# 🛩 Drone Delivery Server
> Drone Delivery Simulation Server with Cosys-Airsm

FastAPI 기반의 웹 서버를 통해 [Cosys-AirSim](https://pypi.org/project/cosysairsim/) 시뮬레이터를 제어하고,  
경로 설정, 설정 변경, 센서 스트리밍 등을 API 및 웹 UI를 통해 제공하는 시스템입니다.

---

## 📁 프로젝트 구조

```
app/
├── api/                # FastAPI 라우터 (v1 API 포함)
│   └── v1/
├── core/               # 설정, 보안, 예외 처리 등
├── models/             # Pydantic + SQLAlchemy 모델
├── services/           # 핵심 비즈니스 로직 (예: aircraft, settings)
├── static/             # JS, CSS, 이미지
├── templates/          # Jinja2 HTML 템플릿
├── utils/              # 헬퍼 함수 모음
├── main.py             # FastAPI 엔트리포인트
└── ...
```
```
test/                   # 테스트 코드
├── TODO
└── ...
```

---
## 📦 설치 및 실행 가이드

### 🧪 Conda 환경 설정

```bash
# 1. Conda 환경 생성
conda create -n drone-server python=3.12 -y
conda activate drone-server

# 2. 필수 패키지 설치
pip install -r requirements.txt
```

또는 수동으로 설치:

```bash
pip install "fastapi[standard]" "uvicorn[standard]" pydantic  rpc-msgpack cosysairsim jinja2 geopy
```

> `cosysairsim`은 Cosys-Lab에서 제공하는 AirSim 제어용 Python API입니다.

---

## 🚀 FastAPI 서버 실행

```bash
python Launch.py
```

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
- ReDoc 문서: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛠 이 아래부터는 미완성

## ⚙️ 환경 설정 파일 (`.env`)

```env
SIM_HOST=127.0.0.1
SIM_PORT=41451
API_KEY=dev-secret
```

> `.env` 파일은 `pydantic.BaseSettings`을 통해 자동 로드됩니다.

---

## 🧪 테스트 실행

```bash
pytest tests/
```

---

## 🛠 TODO

- [ ] Aircraft 경로 시각화 (Leaflet.js)
- [ ] 다중 에이전트 제어 및 상태 모니터링
- [ ] 설정 변경 로그 저장 기능
- [ ] Lidar / Depth 이미지 API 연동

---

## 🧾 라이선스

MIT License  
(c) 2025 YourName
