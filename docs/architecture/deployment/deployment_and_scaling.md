# Deployment and Scaling Guidelines

This document provides comprehensive guidelines for deploying and scaling the Open WebUI backend.

## Deployment Options

### 1. Docker Deployment

#### Basic Setup
```bash
# Build the image
docker build -t open-webui-backend .

# Run the container
docker run -d \
  -p 3000:3000 \
  -v /path/to/data:/app/data \
  -e OPENAI_API_KEY=your-key \
  open-webui-backend
```

#### Production Configuration
```bash
docker run -d \
  -p 3000:3000 \
  -v /path/to/data:/app/data \
  -e OPENAI_API_KEY=your-key \
  -e RAG_EMBEDDING_ENGINE=openai \
  -e RAG_EMBEDDING_MODEL=text-embedding-ada-002 \
  -e ENABLE_RAG_HYBRID_SEARCH=true \
  -e VECTOR_DB=chroma \
  -e CHUNK_SIZE=1000 \
  -e CHUNK_OVERLAP=100 \
  open-webui-backend
```

### 2. Kubernetes Deployment

#### Basic Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: open-webui-backend
  template:
    metadata:
      labels:
        app: open-webui-backend
    spec:
      containers:
      - name: open-webui-backend
        image: open-webui-backend:latest
        ports:
        - containerPort: 3000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: open-webui-secrets
              key: openai-api-key
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: open-webui-pvc
```

#### Production Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: open-webui-backend
  template:
    metadata:
      labels:
        app: open-webui-backend
    spec:
      containers:
      - name: open-webui-backend
        image: open-webui-backend:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: open-webui-secrets
              key: openai-api-key
        - name: RAG_EMBEDDING_ENGINE
          value: "openai"
        - name: RAG_EMBEDDING_MODEL
          value: "text-embedding-ada-002"
        - name: ENABLE_RAG_HYBRID_SEARCH
          value: "true"
        - name: VECTOR_DB
          value: "chroma"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: config-volume
          mountPath: /app/config
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: open-webui-pvc
      - name: config-volume
        configMap:
          name: open-webui-config
```

## Scaling Strategies

### 1. Horizontal Scaling

#### Load Balancer Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: open-webui-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: open-webui-backend
```

#### Auto-scaling Configuration
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: open-webui-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: open-webui-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Vertical Scaling

#### Resource Optimization
```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"
```

## Performance Optimization

### 1. Caching Strategy

#### Redis Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-cache
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis-cache
  template:
    metadata:
      labels:
        app: redis-cache
    spec:
      containers:
      - name: redis
        image: redis:6-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
```

### 2. Database Optimization

#### Vector Database Scaling
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: vector-db
spec:
  serviceName: vector-db
  replicas: 3
  selector:
    matchLabels:
      app: vector-db
  template:
    metadata:
      labels:
        app: vector-db
    spec:
      containers:
      - name: vector-db
        image: vector-db:latest
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

## Monitoring and Logging

### 1. Prometheus Metrics

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: open-webui-monitor
spec:
  selector:
    matchLabels:
      app: open-webui-backend
  endpoints:
  - port: metrics
    interval: 15s
```

### 2. Logging Configuration

```yaml
apiVersion: logging.banzaicloud.io/v1beta1
kind: Flow
metadata:
  name: open-webui-logs
spec:
  filters:
  - parser:
      remove_key_name_field: true
      parse:
        type: json
  match:
  - select:
      labels:
        app: open-webui-backend
  localOutputRefs:
  - open-webui-logs-output
```

## Security Considerations

### 1. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: open-webui-network-policy
spec:
  podSelector:
    matchLabels:
      app: open-webui-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
```

### 2. Secret Management

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: open-webui-secrets
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  ollama-api-key: <base64-encoded-key>
```

## Backup and Recovery

### 1. Data Backup

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: open-webui-backup
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool:latest
            command: ["/backup.sh"]
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
```

### 2. Disaster Recovery

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: open-webui-backup-schedule
spec:
  schedule: "0 0 * * *"
  template:
    includedNamespaces:
    - open-webui
    storageLocation: default
    volumeSnapshotLocations:
    - default
```

## Best Practices

1. **Resource Management**
   - Monitor resource usage regularly
   - Set appropriate resource limits
   - Implement auto-scaling based on metrics

2. **Security**
   - Use secrets for sensitive data
   - Implement network policies
   - Regular security audits

3. **Monitoring**
   - Set up comprehensive monitoring
   - Configure alerts for critical metrics
   - Regular performance reviews

4. **Backup**
   - Regular data backups
   - Test recovery procedures
   - Document backup/restore procedures

5. **Scaling**
   - Start with conservative scaling
   - Monitor performance impact
   - Adjust based on metrics 