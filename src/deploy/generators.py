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

RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface

EXPOSE {port}

CMD ["python", "-m", "{pkg}.main"]
"""


def generate_docker_compose(
    name: str,
    pkg: str,
    port: int = 8000,
    *,
    include_qdrant: bool = False,
) -> str:
    """Compose file for local runs. Optionally add a Qdrant sidecar for vector storage."""
    qdrant_block = ""
    vols = "  hf-cache:\n"
    extra_dep = ""
    extra_env = ""
    if include_qdrant:
        qdrant_block = f"""\
  {name}-qdrant:
    image: qdrant/qdrant:v1.12.0
    ports:
      - "6333:6333"
    volumes:
      - {name}-qdrant-data:/qdrant/storage
    restart: unless-stopped

"""
        vols += f"  {name}-qdrant-data:\n"
        extra_dep = f"""\
    depends_on:
      - {name}-qdrant
"""
        extra_env = f"""\
    environment:
      QDRANT_URL: http://{name}-qdrant:6333
      VECTOR_PROVIDER: qdrant
"""

    return f"""\
services:
{qdrant_block}  {name}:
    build: .
    ports:
      - "{port}:{port}"
    env_file: .env
{extra_dep}{extra_env}    volumes:
      - ./data:/app/data
      - hf-cache:/root/.cache/huggingface
    restart: unless-stopped

volumes:
{vols}"""


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


def generate_k8s_namespace(name: str) -> str:
    """Logical namespace for RAG microservice manifests."""
    return f"""\
apiVersion: v1
kind: Namespace
metadata:
  name: {name}
"""


def generate_k8s_pvc_rag_staging(name: str) -> str:
    """Shared staging PVC for extract → chunk → embed Jobs (sequential use)."""
    return f"""\
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {name}-rag-staging
  namespace: {name}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
"""


def generate_k8s_pvc_qdrant(name: str) -> str:
    return f"""\
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {name}-qdrant-data
  namespace: {name}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
"""


def generate_k8s_qdrant_deployment(name: str) -> str:
    return f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-qdrant
  namespace: {name}
  labels:
    app.kubernetes.io/name: {name}-qdrant
    component: vector-database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}-qdrant
  template:
    metadata:
      labels:
        app: {name}-qdrant
        component: vector-database
    spec:
      containers:
        - name: qdrant
          image: qdrant/qdrant:v1.12.0
          ports:
            - containerPort: 6333
              name: http
          volumeMounts:
            - name: qdrant-storage
              mountPath: /qdrant/storage
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
      volumes:
        - name: qdrant-storage
          persistentVolumeClaim:
            claimName: {name}-qdrant-data
"""


def generate_k8s_qdrant_service(name: str) -> str:
    return f"""\
apiVersion: v1
kind: Service
metadata:
  name: {name}-qdrant
  namespace: {name}
  labels:
    component: vector-database
spec:
  selector:
    app: {name}-qdrant
  ports:
    - name: http
      port: 6333
      targetPort: 6333
  type: ClusterIP
"""


def generate_k8s_configmap_rag(name: str, pkg: str) -> str:
    """Env shared by RAG Jobs (non-secret defaults). Secrets belong in a Secret resource."""
    return f"""\
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}-rag-config
  namespace: {name}
data:
  LOG_LEVEL: "INFO"
  RAG_SOURCE_DIR: "/app/data/raw"
  QDRANT_URL: "http://{name}-qdrant:6333"
  VECTOR_PROVIDER: "qdrant"
  LANGFUSE_HOST: "https://cloud.langfuse.com"
  LANGFUSE_ENABLED: "true"
  # Langfuse keys: use kubectl create secret or external secrets — not plain ConfigMap in production.
"""


def generate_k8s_job_rag_stage(name: str, pkg: str, stage: str) -> str:
    """Batch Job for one RAG stage (extract | chunk | embed)."""
    stage_labels = {"extract": "data-extraction", "chunk": "chunking", "embed": "embedding"}
    component = stage_labels.get(stage, stage)
    return f"""\
apiVersion: batch/v1
kind: Job
metadata:
  name: {name}-rag-{stage}
  namespace: {name}
  labels:
    app.kubernetes.io/name: {name}
    rag-stage: {stage}
    component: {component}
spec:
  backoffLimit: 2
  ttlSecondsAfterFinished: 86400
  template:
    metadata:
      labels:
        rag-stage: {stage}
        component: {component}
    spec:
      restartPolicy: Never
      containers:
        - name: rag-{stage}
          image: {name}:latest
          imagePullPolicy: IfNotPresent
          command: ["python", "-m", "{pkg}.workers.stage_runner"]
          envFrom:
            - configMapRef:
                name: {name}-rag-config
          env:
            - name: RAG_STAGE
              value: "{stage}"
          volumeMounts:
            - name: rag-data
              mountPath: /app/data
            - name: hf-cache
              mountPath: /root/.cache/huggingface
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "8Gi"
              cpu: "2000m"
      volumes:
        - name: rag-data
          persistentVolumeClaim:
            claimName: {name}-rag-staging
        - name: hf-cache
          emptyDir: {{}}
"""


def generate_k8s_rag_readme(name: str, pkg: str) -> str:
    return f"""\
# Kubernetes layout — RAG services

This scaffold separates **concerns** used in production RAG systems:

| Resource | Role |
|----------|------|
| Jobs `{name}-rag-extract`, `{name}-rag-chunk`, `{name}-rag-embed` | **Data extraction** (load documents), **chunking**, **embedding + vector upsert** — each runs `python -m {pkg}.workers.stage_runner` with `RAG_STAGE` set. |
| Deployment `{name}-qdrant` + Service | **Vector database** (Qdrant) — holds embeddings; embed Job writes via `QDRANT_URL`. |
| PVC `{name}-rag-staging` | Shared **checkpoint files** (`data/staging/documents.json`, `chunks.json`) between Jobs. |

## Order of execution

Jobs must run **in sequence** on the same PVC (ReadWriteOnce): **extract → chunk → embed**.
Use CI (GitHub Actions), Argo Workflows, or manual `kubectl` between steps. For multi-node clusters you need ReadWriteMany storage or object storage instead of shared PVC.

Build and load your image:

```bash
docker build -t {name}:latest .
kind load docker-image {name}:latest   # or push to your registry and set imagePullSecrets
```

Apply manifests:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pvc-rag-staging.yaml
kubectl apply -f k8s/pvc-qdrant.yaml
kubectl apply -f k8s/configmap-rag.yaml
kubectl apply -f k8s/qdrant-deployment.yaml
kubectl apply -f k8s/qdrant-service.yaml
kubectl apply -f k8s/job-rag-extract.yaml
kubectl wait --for=condition=complete job/{name}-rag-extract -n {name} --timeout=600s
kubectl apply -f k8s/job-rag-chunk.yaml
kubectl wait --for=condition=complete job/{name}-rag-chunk -n {name} --timeout=600s
kubectl apply -f k8s/job-rag-embed.yaml
kubectl wait --for=condition=complete job/{name}-rag-embed -n {name} --timeout=1800s
```

## Langfuse

Set keys via **Secret** (recommended) or extend the ConfigMap for non-production only:

```bash
kubectl create secret generic {name}-langfuse -n {name} \\\\
  --from-literal=LANGFUSE_PUBLIC_KEY=pk-... \\\\
  --from-literal=LANGFUSE_SECRET_KEY=sk-...
```

Mount or reference them in the Job spec as needed; locally use `.env` from `.env.example`.

## Optional monolith

For a single-process demo, run **`docker compose up`** at the project root or **`python -m {pkg}`** locally — see the project README.
"""
