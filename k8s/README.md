# Kubernetes Manifests for CSV Processor

This directory contains all Kubernetes manifests required to deploy the CSV Processor application to an EKS cluster.

## 📁 Files Overview

### `namespace.yaml`
- **Purpose**: Creates dedicated namespace `k8s-raghadafghani`
- **Features**: Proper labels and annotations for organization
- **Usage**: Isolates application resources

### `configmap.yaml`
- **Purpose**: Non-sensitive configuration data
- **Contains**: 
  - Application environment settings
  - Server configuration
  - CORS settings
  - Performance tuning parameters
- **Usage**: Mounted as environment variables

### `secret.yaml`
- **Purpose**: Sensitive configuration data (base64 encoded)
- **Contains**: 
  - API keys (placeholder)
  - Database credentials (placeholder)
  - Application secret key
- **Security**: Never commit real secrets to Git!

### `deployment.yaml`
- **Purpose**: Main application deployment
- **Features**:
  - 3 replicas for high availability
  - Rolling update strategy
  - Resource requests/limits
  - Health check probes (liveness, readiness, startup)
  - Security context (non-root user)
  - ConfigMap and Secret integration

### `service.yaml`
- **Purpose**: Network access to the application
- **Features**:
  - LoadBalancer type for external access
  - Internal ClusterIP service for pod-to-pod communication
  - Port mapping (80/443 → 8000)
  - AWS Load Balancer annotations

## 🚀 Deployment Order

The manifests should be applied in this order:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 🔧 Configuration

### Resource Requirements
- **CPU**: 100m request, 500m limit
- **Memory**: 128Mi request, 512Mi limit
- **Storage**: 1Gi temporary cache volume

### Health Checks
- **Startup Probe**: 10s delay, 5s interval, 10 failures max
- **Liveness Probe**: 30s delay, 10s interval, 3 failures max
- **Readiness Probe**: 5s delay, 5s interval, 3 failures max

### Security Features
- Non-root user (UID 1001)
- Read-only root filesystem capability
- Dropped ALL capabilities
- Security context applied

## 🌐 Access

After deployment, the application will be available at:
- **HTTP**: `http://<LoadBalancer-IP>`
- **HTTPS**: `https://<LoadBalancer-IP>` (if SSL configured)

Check LoadBalancer IP:
```bash
kubectl get service csv-processor-service -n k8s-raghadafghani
```

## 📊 Monitoring

The deployment includes annotations for Prometheus monitoring:
- Scrape endpoint: `/health`
- Port: `8000`
- Enabled by default

## 🔍 Troubleshooting

### Check deployment status:
```bash
kubectl get deployment csv-processor -n k8s-raghadafghani
```

### View pod logs:
```bash
kubectl logs -l app.kubernetes.io/name=csv-processor -n k8s-raghadafghani
```

### Check pod status:
```bash
kubectl get pods -l app.kubernetes.io/name=csv-processor -n k8s-raghadafghani
```

### Describe deployment:
```bash
kubectl describe deployment csv-processor -n k8s-raghadafghani
```

## 🔄 Updates

To update the application:
1. Push new image to registry
2. Update image tag in `deployment.yaml`
3. Apply the deployment: `kubectl apply -f deployment.yaml`
4. Monitor rollout: `kubectl rollout status deployment/csv-processor -n k8s-raghadafghani`