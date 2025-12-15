#!/bin/bash

# CSV Processor Kubernetes Deployment Script
# Usage: ./deploy.sh [IMAGE_TAG]

set -e

# Configuration
NAMESPACE="k8s-raghadafghani"
IMAGE_TAG=${1:-"main"}
IMAGE_REPO="ghcr.io/raghadafghani/csv-processor"

echo "🚀 Deploying CSV Processor to Kubernetes..."
echo "📦 Image: ${IMAGE_REPO}:${IMAGE_TAG}"
echo "🏷️  Namespace: ${NAMESPACE}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "💡 Make sure your kubeconfig is set up correctly"
    exit 1
fi

# Update image tag in deployment
echo "📝 Updating image tag in deployment.yaml..."
sed -i.bak "s|ghcr.io/raghadafghani/csv-processor:main|${IMAGE_REPO}:${IMAGE_TAG}|g" deployment.yaml

# Apply manifests in order
echo "📋 Applying Kubernetes manifests..."

echo "  → Creating namespace..."
kubectl apply -f namespace.yaml

echo "  → Applying ConfigMap..."
kubectl apply -f configmap.yaml

echo "  → Applying Secrets..."
kubectl apply -f secret.yaml

echo "  → Deploying application..."
kubectl apply -f deployment.yaml

echo "  → Creating services..."
kubectl apply -f service.yaml

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/csv-processor -n ${NAMESPACE} --timeout=300s

# Show deployment status
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Deployment Status:"
kubectl get deployment csv-processor -n ${NAMESPACE}

echo ""
echo "🏃 Running Pods:"
kubectl get pods -l app.kubernetes.io/name=csv-processor -n ${NAMESPACE}

echo ""
echo "🌐 Services:"
kubectl get services -n ${NAMESPACE}

echo ""
echo "🔗 LoadBalancer Status:"
EXTERNAL_IP=$(kubectl get service csv-processor-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")

if [ "$EXTERNAL_IP" != "pending" ] && [ "$EXTERNAL_IP" != "" ]; then
    echo "🎉 Application is available at:"
    echo "   HTTP:  http://${EXTERNAL_IP}"
    echo "   HTTPS: https://${EXTERNAL_IP}"
else
    echo "⏳ LoadBalancer IP is still pending..."
    echo "💡 Run this command to check status:"
    echo "   kubectl get service csv-processor-service -n ${NAMESPACE}"
fi

# Restore original deployment.yaml
mv deployment.yaml.bak deployment.yaml

echo ""
echo "🎯 Deployment Summary:"
echo "   Namespace: ${NAMESPACE}"
echo "   Image: ${IMAGE_REPO}:${IMAGE_TAG}"
echo "   Replicas: 3"
echo "   Service Type: LoadBalancer"
echo ""
echo "📚 Useful Commands:"
echo "   View logs: kubectl logs -l app.kubernetes.io/name=csv-processor -n ${NAMESPACE}"
echo "   Scale app: kubectl scale deployment csv-processor --replicas=5 -n ${NAMESPACE}"
echo "   Delete app: kubectl delete namespace ${NAMESPACE}"