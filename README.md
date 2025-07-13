# poc-dashboard

## Local Development Cheatsheet

This guide provides the commands needed to connect your local development environment to the services running in the Kubernetes cluster.

### 1. Start Port Forwarding

You need to create secure tunnels from your local machine to the PostgreSQL and MinIO services in the cluster. Run each of these commands in a **separate, dedicated terminal window** and keep them running.

**Terminal 1: Forward PostgreSQL (DuckLake Catalog)**
```bash
kubectl port-forward -n ducklake svc/postgres 5432:5432
```

**Terminal 2: Forward MinIO (S3 Data Storage)**
```bash
kubectl port-forward -n ducklake svc/minio-svc 9000:9000
```

### 2. Set Up Environment Variables

In a new terminal where you will run your dashboard app, export the database and S3 credentials from Kubernetes secrets.

```bash
# This command creates a .env file in your current directory
(
  echo "POSTGRES_USER=$(kubectl get secret postgres-secret -n ducklake -o jsonpath='{.data.username}' | base64 --decode)"
  echo "POSTGRES_PASSWORD=$(kubectl get secret postgres-secret -n ducklake -o jsonpath='{.data.password}' | base64 --decode)"
  echo "POSTGRES_DB=$(kubectl get secret postgres-secret -n ducklake -o jsonpath='{.data.database}' | base64 --decode)"
  echo "MINIO_ROOT_USER=$(kubectl get secret minio-secret -n ducklake -o jsonpath='{.data.MINIO_ROOT_USER}' | base64 --decode)"
  echo "MINIO_ROOT_PASSWORD=$(kubectl get secret minio-secret -n ducklake -o jsonpath='{.data.MINIO_ROOT_PASSWORD}' | base64 --decode)"
) > .env

echo ".env file created successfully."
```

### 3. Run the Local Dashboard App

With the port-forwards running and environment variables set, you can now run the Plotly Dash application.

```bash
# Navigate to your dashboard project directory
cd /path/to/your/poc-dashboard

# Run the application
python app.py
```
Your dashboard will be available at `http://localhost:8050` and will be connected to the live data in your cluster.

### 4. Accessing the Jupyter UI

To access the Jupyter notebook environment for data exploration:

**Step A: Port-forward the Jupyter Service**
Run this in a new terminal.
```bash
kubectl port-forward -n ducklake svc/jupyter-ui-svc 8888:80
```

**Step B: Get the Login Token**
```bash
# Get the pod name
POD_NAME=$(kubectl get pods -n ducklake -l app=jupyter-ui -o jsonpath='{.items[0].metadata.name}')

# Get the logs and find the token URL
kubectl logs -n ducklake $POD_NAME
```
Look for a URL in the logs like `http://127.0.0.1:8888/lab?token=...` which contains the required auth token.
