FROM python:3.11-slim-bookworm

WORKDIR /app

# --- Install dependencies + precompiled Node.js ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        procps && \
    rm -rf /var/lib/apt/lists/*

# --- Install Python dependencies ---
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m ipykernel install --user

# --- Download Traefik static binary (v2.10.1) ---
RUN curl -L -o /tmp/traefik.tar.gz https://github.com/traefik/traefik/releases/download/v2.10.1/traefik_v2.10.1_linux_amd64.tar.gz && \
    tar -xzf /tmp/traefik.tar.gz -C /usr/local/bin/ traefik && \
    chmod +x /usr/local/bin/traefik && rm /tmp/traefik.tar.gz

# --- Setup Voila config ---
RUN mkdir -p /etc/jupyter && \
    echo '{ \
      "VoilaConfiguration": { \
        "file_allowlist": [".*", "iframe_figures/.*"], \
        "show_tracebacks": true \
      }, \
      "ServerApp": { \
        "allow_origin": "*", \
        "allow_credentials": true, \
        "disable_check_xsrf": true, \
        "disable_check_trust": true \
      } \
    }' > /etc/jupyter/voila.json

# --- Copy application code ---
COPY . .

# --- Copy Traefik config + scripts ---
COPY count_kernels.sh /app/count_kernels.sh
COPY dynamic_conf.yml /etc/traefik/dynamic_conf.yml
COPY traefik.yml /etc/traefik/traefik.yml
COPY run_voila.py /app/run_voila.py

RUN chmod +x /app/count_kernels.sh

EXPOSE 8080

CMD ["sh", "-c", "\
    /app/count_kernels.sh & \
    python -m http.server 8867 --directory /tmp & \
    \
    # CRITICAL FIX: Redirects Voila's output and error streams (2>&1) \
    # to the main shell, ensuring the Traceback appears in Cloud Run logs.\
    { python /app/run_voila.py & } 2>&1 & \
    \
    # The echo line was removed as it was misleading and hardcoded.\
    traefik --configFile=/etc/traefik/traefik.yml" \
]
