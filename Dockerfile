# Q-Reg Idris2 + Rust CI Environment
FROM ubuntu:24.04

# Install system deps + Chez Scheme (Idris2 backend)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libgmp-dev \
    chezscheme \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Idris2 (latest stable via official method)
RUN curl -sSL https://github.com/idris-lang/Idris2/archive/refs/tags/v0.7.0.tar.gz | tar -xz && \
    cd Idris2-0.7.0 && \
    make bootstrap SCHEME=chez && \
    make install && \
    cd .. && rm -rf Idris2-0.7.0

ENV PATH="/root/.idris2/bin:${PATH}"

# Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Copy project
COPY . .

# Verify
CMD ["sh", "-c", "cd runtime && cargo check && cd ../formal && idris2 --check *.idr && echo '✅ Q-Reg CI: Rust + Idris2 verified'"]