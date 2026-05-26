# Outline

## Docker

어디서든 일정한 환경을 구축하기 위한<br>
container로 이루어진 환경<br>

## Composition

### install

[Docker Desktop](https://www.docker.com/)

### Dockerfile

```Dockerfile
# ============================================================
# CH3~5 실습 통합 Docker 이미지
# Base : PyTorch 2.7 + CUDA 12.8 (RTX 50xx / Blackwell 대응)
# Python : 3.10
# ============================================================

# 0. 베이스 이미지 설정
# PyTorch 2.7과 CUDA 12.8이 미리 설치된 공식 이미지를 사용합니다. 
# 모델 학습에 필수적인 cuDNN(9버전)도 포함되어 있어 별도의 CUDA 설치 과정이 생략됩니다. [cite: 1]
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

# ── 1. 환경 변수 (ENV) ────────────────────────────────────────────
# 이미지 빌드 및 실행 중에 사용할 기본 환경 변수들을 묶어서 설정합니다.
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JUPYTER_TOKEN=lab \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    UNSLOTH_ENABLE_CCE=0 \
    TORCHDYNAMO_DISABLE=1
# [참고] 
# DEBIAN_FRONTEND=noninteractive: 패키지 설치 시 사용자 입력 창(예: y/n)이 뜨는 것을 막아 자동화를 돕습니다. [cite: 1]
# PIP_NO_CACHE_DIR=1: pip로 패키지를 설치할 때 캐시를 남기지 않아 도커 이미지 용량을 줄여줍니다. [cite: 1]

# ── 2. 시스템 패키지 설치 (RUN) ────────────────────────────────
# 리눅스(우분투) 환경에 필요한 최소한의 필수 유틸리티를 설치합니다.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git curl wget tzdata libgl1 libglib2.0-0 gcc g++ && \
    ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# [참고]
# --no-install-recommends: 해당 패키지 실행에 꼭 필요하지 않은 추천 패키지들은 빼고 설치하여 용량을 아낍니다. [cite: 2]
# apt-get clean && rm -rf ... : 설치 완료 후 불필요한 임시 파일들을 삭제하여 최종 도커 이미지 크기를 최적화합니다. [cite: 2]

# ── 3. 작업 디렉터리 (WORKDIR) ────────────────────────────────────────
# 이후 실행될 모든 명령어(RUN, CMD, COPY 등)가 실행될 기본 폴더를 /workspace로 지정합니다. [cite: 2]
WORKDIR /workspace

# ── 4. Python 패키지 설치 (COPY & RUN) ───────────────────────────────────
# 호스트(내 PC)에 있는 requirements.txt 파일을 컨테이너 안으로 복사한 뒤, pip를 업데이트하고 패키지를 설치합니다. [cite: 2, 3]
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ── 4b. LangChain 생태계 패키지 설치 ─────────────────────────
# RAG(검색 증강 생성)나 AI 에이전트 구축에 필요한 LangChain 관련 패키지들을 특정 버전 범위 내에서 안전하게 설치합니다. [cite: 4]
RUN pip install \
    "langchain>=0.3.0,<1" \
    "langchain-core>=0.3.0,<1" \
    "langchain-community>=0.3.0,<1" \
    "langchain-openai>=0.2.0,<1" \
    "langchain-upstage>=0.3.0,<1" \
    "langchain-text-splitters>=0.3.0,<1" \
    "langgraph>=0.2.0,<1"

# ── 4c. Unsloth 설치 ─────────────────────────
# LLM 파인튜닝(미세조정) 속도를 높이고 메모리를 절약해 주는 Unsloth 라이브러리를 설치합니다. [cite: 5]
# 현재 컨테이너의 CUDA(12.8) 및 PyTorch(2.7) 버전에 정확히 맞는 전용 패키지를 지정하여 설치합니다. [cite: 5]
RUN pip install "unsloth[cu128-torch270]"

# ── 4d. CUDA 라이브러리 경로(ldconfig) 수동 등록 ─────────────────
# 도커 환경에서 bitsandbytes나 unsloth가 CUDA 동적 라이브러리(.so)를 찾지 못하는 버그를 해결하기 위한 핵심 트러블슈팅 구문입니다. [cite: 6]
# 파이썬 코드로 cublas 및 cuda_runtime의 설치 경로를 찾아낸 뒤, 시스템의 라이브러리 경로(/etc/ld.so.conf.d/)에 강제로 추가하고 반영(ldconfig)합니다. [cite: 6]
RUN NVIDIA_LIB=$(python -c "import nvidia.cublas; print(nvidia.cublas.__path__[0] + '/lib')") && \
    echo "$NVIDIA_LIB" > /etc/ld.so.conf.d/nvidia-python.conf && \
    CUDA_RT_LIB=$(python -c "import nvidia.cuda_runtime; print(nvidia.cuda_runtime.__path__[0] + '/lib')") && \
    echo "$CUDA_RT_LIB" >> /etc/ld.so.conf.d/nvidia-python.conf && \
    ldconfig

# ── 5. 환경 검증 스크립트 복사 ───────────────────────────────────
# 컨테이너 내부에 환경이 제대로 구축되었는지 테스트하는 스크립트를 시스템 경로(/usr/local/bin)로 복사하고, 실행 권한(chmod +x)을 부여합니다. [cite: 6]
COPY scripts/verify_env.sh /usr/local/bin/verify_env.sh
RUN chmod +x /usr/local/bin/verify_env.sh

# ── 6. 포트 노출 및 기본 실행 명령어 (EXPOSE & CMD) ───────────────
# 8888 포트를 외부에 개방함을 명시합니다. [cite: 6]
EXPOSE 8888

# 컨테이너가 켜질 때 최종적으로 실행할 명령어입니다. [cite: 6]
# Jupyter Lab 서버를 8888 포트에서 실행하며, 외부 접속 허용(--ip=0.0.0.0), 루트 권한 실행 허용(--allow-root) 등의 옵션을 줍니다. [cite: 6]
# 접속 토큰은 아까 1번 항목에서 설정한 ENV 변수(JUPYTER_TOKEN) 값을 불러와 사용합니다. [cite: 6]
CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token=${JUPYTER_TOKEN:-lab} --ServerApp.allow_origin='*'"]
```

### docker-compose.yml

```yml
# 컨테이너 빌드 및 실행 명령어: docker compose up --build

services:
  lab:
    # 1. 빌드 설정: 현재 폴더(.)에 있는 Dockerfile을 바탕으로 이미지를 빌드합니다.
    build:
      context: .
      dockerfile: Dockerfile
    
    # 2. 이미지 및 컨테이너 이름 지정
    image: ch3-5-lab:latest       # 생성될 도커 이미지의 이름과 태그
    container_name: Ai-project    # 실행될 도커 컨테이너의 고유 이름
    
    # 3. 포트 포워딩: 호스트(내 PC)의 8888 포트를 컨테이너의 8888 포트와 연결 (Jupyter Lab 접속용)
    ports:
      - "8888:8888"
    
    # 4. 볼륨 마운트: 호스트의 현재 폴더(.)를 컨테이너 내부의 /workspace와 동기화 (파일 실시간 공유)
    volumes:
      - .:/workspace
    
    # 5. 작업 경로: 컨테이너 터미널 진입 시 기본으로 위치할 폴더 지정
    working_dir: /workspace
    
    # 6. 상호작용 설정: 터미널 입력을 열어두고(stdin_open) 가상 터미널을 할당(tty)하여 컨테이너가 꺼지지 않게 유지
    stdin_open: true
    tty: true
    
    # 7. 공유 메모리 크기: 딥러닝 학습 시 데이터 로더 병목을 막기 위해 넉넉하게 4GB 할당
    shm_size: "4g"
    
    # 8. 컨테이너 내부 환경 변수 설정
    environment:
      PYTHONUNBUFFERED: "1"                         # 파이썬 출력 버퍼링 끄기 (터미널 로그가 지연 없이 즉시 출력됨)
      TZ: Asia/Seoul                                # 시스템 시간대를 한국 시간(KST)으로 설정
      JUPYTER_TOKEN: Ghkdtnscjf!1                   # 주피터 랩 접속 시 사용할 비밀번호 설정
      NVIDIA_VISIBLE_DEVICES: all                   # 컨테이너에서 시스템의 모든 NVIDIA GPU 인식 허용
      NVIDIA_DRIVER_CAPABILITIES: compute,utility   # GPU의 연산(compute) 및 모니터링(utility) 기능 활성화
      UNSLOTH_ENABLE_CCE: "0"                       # Unsloth 라이브러리의 커스텀 C++ 컴파일러(CCE) 비활성화 (호환성 에러 방지용)
      TORCHDYNAMO_DISABLE: "1"                      # PyTorch 2.x의 동적 컴파일(torch.compile) 비활성화 (충돌 방지 및 안정성 확보)
      HF_HOME: /workspace/.cache/huggingface        # 허깅페이스 모델 저장 경로를 마운트된 볼륨 내부로 지정 (컨테이너 재생성 시에도 모델 유지)
    
    # 9. GPU 리소스 할당
    # 시스템에 모든 GPU 자원을 컨테이너에 예약합니다. GPU가 없는 환경이어도 에러 없이 CPU 모드로 우회 실행되도록 돕는 최신 설정 방식입니다.
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia        # NVIDIA 드라이버 사용
              count: all            # 가능한 모든 GPU 개수 할당
              capabilities: [gpu]   # GPU 기능 활성화
```

### scripts (환경변수 세팅 검사 도구)