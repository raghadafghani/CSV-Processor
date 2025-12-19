# Kubernetes Manifests for CSV Processor

This directory contains all Kubernetes manifests required to deploy the CSV Processor application to an EKS cluster.

## 📁 Files Overview

### `namespace.yaml`
- **Purpose**: Creates dedicated namespace `k8s-raghadafghani`
- **Features**: Esential labels for organizastion and management
- **Usage**: Isolates application resources

### `configmap.yaml`
- **Purpose**: Non-sensitive configuration data
- **Requirements Met**:
  - ✅ Configuration data (not secrets!)
  - ✅ APP_ENV=production
  - ✅ LOG_LEVEL=info
  - ✅ Custom config your app needs
- **Contains**: Server settings, CORS config, file processing limits

### `deployment.yaml`
- **Purpose**: Main application deployment
- **Requirements Met**:
  - ✅ Deployment with 2+ replicas
  - ✅ Container image from GHCR (the one you pushed)
  - ✅ Resource requests/limits (CPU & memory)
  - ✅ Environment variables from ConfigMap
  - ✅ Health check probes (livenessProbe, readinessProbe)
  - ✅ Rolling update strategy
  - ✅ Labels and selectors properly configured
- **Features**: Security context, non-root user, proper resource management

### `service.yaml`
- **Purpose**: Network access to the application
- **Requirements Met**:
  - ✅ Service type: LoadBalancer (for external access)
  - ✅ Port mapping (container port → service port)
  - ✅ Selector matches deployment labels
  - ✅ Session affinity: None (stateless app)
- **Features**: External LoadBalancer for internet access

## Automated Deployment

**No manual deployment needed!** Everything is handled by GitHub Actions:

```
git push → GitHub Actions → Automated Deployment to EKS
```

The CI/CD pipeline automatically:
1. Builds and tests the application
2. Creates Docker image and pushes to GHCR
3. Applies all Kubernetes manifests
4. Provides live URL for the application

## Configuration

### Resource Requirements
- **CPU**: 50m request, 250m limit per pod
- **Memory**: 64Mi request, 256Mi limit per pod
- **Replicas**: 2 pods for high availability


## Access

After deployment, the CSV Processor App is available at the LoadBalancer URL

## Monitoring

Check deployment status:
```bash
kubectl get all -n k8s-raghadafghani
```

View application logs:
```bash
kubectl logs -l app.kubernetes.io/name=csv-processor -n k8s-raghadafghani
```

## Troubleshooting

### Check deployment status:
```bash
kubectl get deployment csv-processor -n k8s-raghadafghani
```

### View pod logs:
```bash
kubectl logs -l app.kubernetes.io/name=csv-processor -n k8s-raghadafghani
```

### Check service status:
```bash
kubectl get service csv-processor-service -n k8s-raghadafghani
```

### Get LoadBalancer URL:
```bash
kubectl get service csv-processor-service -n k8s-raghadafghani -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Updates

Updates are handled automatically through GitHub Actions. When we push code changes:
1. New Docker image is built
2. Kubernetes performs rolling update
3. Zero downtime deployment
4. Health checks ensure smooth transition
