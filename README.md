# CSV Processor

A production-ready CSV processing web application with enterprise-grade CI/CD pipeline and Kubernetes deployment.

## 🚀 Live Application

**The CSV Processor is automatically deployed and accessible via LoadBalancer URL shown in GitHub Actions.**

## ✨ Features

### **CSV Processing Operations**

- **📊 View**: Display all rows and columns from uploaded CSV files with clean table formatting
- **🔍 Filter**: Filter rows based on specific column values (e.g., show only records where "Status" = "Active")
- **🔄 Transform**: Modify column data with operations:
  - **Uppercase**: Convert text to UPPERCASE
  - **Lowercase**: Convert text to lowercase
  - **Trim**: Remove leading/trailing whitespace
- **📈 Aggregate**: Count occurrences and group data by column values (e.g., count how many records per category)
- **🔢 Sort**: Sort entire dataset by any column in ascending order

### **User Experience**
- **📁 Drag & Drop**: Intuitive file upload interface
- **💾 Download**: Export processed results as CSV files
- **🎨 Clean UI**: Apple-inspired minimalist design
- **⚡ Fast Processing**: Efficient server-side CSV handling

### **Enterprise Features**
- **🚀 Production Ready**: Enterprise-grade deployment pipeline
- **🔒 Secure**: Non-root containers with security scanning
- **📊 Scalable**: Kubernetes orchestration with auto-scaling
- **🔄 Zero Downtime**: Rolling updates with health checks

## 🏗️ Architecture

### **Application Stack**
- **Backend**: Python FastAPI
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Container**: Docker with Alpine Linux
- **Orchestration**: Kubernetes on AWS EKS

### **CI/CD Pipeline**
```
git push → GitHub Actions → Docker Build → Security Scan → Deploy to EKS
```

## 📦 Docker

### **Dockerfile Requirements Met:**
- ✅ Multi-stage build for smaller image (<200MB)
- ✅ Alpine Linux base for security
- ✅ Non-root user (UID 1001)
- ✅ Health checks on `/health` endpoint
- ✅ Optimized layer caching
- ✅ Build context minimization


## ☸️ Kubernetes

### **Deployment Requirements Met:**
- ✅ 2+ replicas for high availability
- ✅ Resource requests/limits (CPU & memory)
- ✅ ConfigMap for environment variables
- ✅ Health probes (liveness & readiness)
- ✅ Rolling update strategy
- ✅ LoadBalancer service for external access

### **Manifests:**
```
k8s/
├── namespace.yaml     # Isolated namespace
├── configmap.yaml     # App configuration
├── deployment.yaml    # Main application
└── service.yaml       # LoadBalancer access
```

## 🔄 Automated Deployment

**Zero-touch deployment:** Push code → Automatic deployment to production

### **Pipeline Stages:**
1. **Test**: Unit tests with coverage
2. **Build**: Docker image creation
3. **Security**: Vulnerability scanning (Trivy + pip-audit)
4. **Push**: Image to GitHub Container Registry
5. **Deploy**: Rolling update to EKS cluster


## 🛠️ Development

### **Local Development:**
```bash
pip install -r requirements.txt
python main.py
# Open http://localhost:8000
```

### **Testing:**
```bash
pytest -v --cov=.
```

## 📊 Monitoring

### **Health Check:**
```bash
curl http://your-loadbalancer-url/health
```

### **Kubernetes Status:**
```bash
kubectl get all -n k8s-raghadafghani
```

## 🔧 Configuration

Application configured via ConfigMap:
- `APP_ENV=production`
- `LOG_LEVEL=info`
- `HOST=0.0.0.0`
- `PORT=8000`

