FROM mcr.microsoft.com/devcontainers/javascript-node:0-20

# Install Python and docker-compose
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        docker-compose \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
