# ============================================================
# CH3~5 실습 통합 Docker 이미지
# Base : PyTorch 2.7 + CUDA 12.8 (RTX 50xx / Blackwell 대응)
# Python : 3.10
# ============================================================
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

# ── 1. 환경 변수 ────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JUPYTER_TOKEN=lab \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    UNSLOTH_ENABLE_CCE=0 \
    TORCHDYNAMO_DISABLE=1

# ── 2. 시스템 패키지 (최소한) ────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git curl wget tzdata libgl1 libglib2.0-0 gcc g++ && \
    ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ── 3. 작업 디렉터리 ────────────────────────────────────────
WORKDIR /workspace

# ── 4. Python 패키지 설치 ───────────────────────────────────
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ── 4b. LangChain 생태계 (의존성 복잡하므로 별도 설치) ──────
RUN pip install \
    "langchain>=0.3.0,<1" \
    "langchain-core>=0.3.0,<1" \
    "langchain-community>=0.3.0,<1" \
    "langchain-openai>=0.2.0,<1" \
    "langchain-upstage>=0.3.0,<1" \
    "langchain-text-splitters>=0.3.0,<1" \
    "langgraph>=0.2.0,<1"

# ── 4c. Unsloth (CUDA 12.8 + torch 2.7 전용 extra) ─────────
RUN pip install "unsloth[cu128-torch270]"

# ── 4d. CUDA 라이브러리를 ldconfig에 등록 (bitsandbytes/unsloth 호환) ──
RUN NVIDIA_LIB=$(python -c "import nvidia.cublas; print(nvidia.cublas.__path__[0] + '/lib')") && \
    echo "$NVIDIA_LIB" > /etc/ld.so.conf.d/nvidia-python.conf && \
    CUDA_RT_LIB=$(python -c "import nvidia.cuda_runtime; print(nvidia.cuda_runtime.__path__[0] + '/lib')") && \
    echo "$CUDA_RT_LIB" >> /etc/ld.so.conf.d/nvidia-python.conf && \
    ldconfig

# ── 5. 검증 스크립트 복사 ───────────────────────────────────
COPY scripts/verify_env.sh /usr/local/bin/verify_env.sh
RUN chmod +x /usr/local/bin/verify_env.sh

# ── 6. 포트 & 실행 ─────────────────────────────────────────
EXPOSE 8888
CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token=${JUPYTER_TOKEN:-lab} --ServerApp.allow_origin='*'"]
