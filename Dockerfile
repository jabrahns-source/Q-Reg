# Q-Reg Deterministic CI - Robust Docker env for Idris2 + Rust
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Base deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential libgmp-dev pkg-config git \
    && rm -rf /var/lib/apt/lists/*

# Chez Scheme (Idris2 backend)
RUN apt-get update && apt-get install -y chezscheme && rm -rf /var/lib/apt/lists/*

# Install Idris2 v0.7.0 (layered for reliability)
RUN curl -sSL https://github.com/idris-lang/Idris2/archive/refs/tags/v0.7.0.tar.gz | tar -xz -C /tmp && \
    cd /tmp/Idris2-0.7.0 && \
    make bootstrap SCHEME=chez && \
    make install PREFIX=/usr/local && \
    rm -rf /tmp/Idris2-0.7.0

ENV PATH="/usr/local/bin:${PATH}"

# Rust (stable)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable && \
    rm -rf /root/.cargo/registry /root/.cargo/git
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app
COPY . .

# Verification command - fails fast on errors
CMD ["sh", "-c", "set -e; echo '=== Rust check ==='; cd runtime && cargo check; echo '=== Idris2 formal check ==='; cd ../formal && idris2 --check *.idr; echo '✅ All checks passed'"]