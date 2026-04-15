"""Generate deployment files for ai-builder projects."""

from __future__ import annotations


def generate_dockerfile(name: str, pkg: str, port: int = 8000) -> str:
    return f"""\
# syntax=docker/dockerfile:1
FROM python:3.13-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
RUN mkdir -p src/{pkg} && touch src/{pkg}/__init__.py
RUN --mount=type=cache,target=/root/.cache/pip \\
    pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface

EXPOSE {port}

CMD ["python", "-m", "{pkg}.main"]
"""


def generate_docker_compose(name: str, pkg: str, port: int = 8000) -> str:
    return f"""\
services:
  {name}:
    build: .
    ports:
      - "{port}:{port}"
    env_file: .env
    volumes:
      - ./data:/app/data
      - hf-cache:/root/.cache/huggingface
    restart: unless-stopped

volumes:
  hf-cache:
"""


def generate_k8s_deployment(name: str, port: int = 8000) -> str:
    return f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  labels:
    app: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
        - name: {name}
          image: {name}:latest
          ports:
            - containerPort: {port}
          envFrom:
            - configMapRef:
                name: {name}-config
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          readinessProbe:
            httpGet:
              path: /health
              port: {port}
            initialDelaySeconds: 10
            periodSeconds: 15
          volumeMounts:
            - name: data
              mountPath: /app/data
            - name: hf-cache
              mountPath: /root/.cache/huggingface
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: {name}-data
        - name: hf-cache
          persistentVolumeClaim:
            claimName: {name}-hf-cache
"""


def generate_k8s_service(name: str, port: int = 8000) -> str:
    return f"""\
apiVersion: v1
kind: Service
metadata:
  name: {name}
spec:
  selector:
    app: {name}
  ports:
    - protocol: TCP
      port: {port}
      targetPort: {port}
  type: ClusterIP
"""


def generate_k8s_configmap(name: str) -> str:
    return f"""\
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}-config
data:
  LOG_LEVEL: "INFO"
  EMBEDDING_MODEL: "sentence-transformers/all-MiniLM-L6-v2"
  # Add your configuration here.
  # Secrets should use a Secret resource, not ConfigMap.
"""


def generate_k8s_hpa(name: str) -> str:
    return f"""\
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {name}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {name}
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
"""
