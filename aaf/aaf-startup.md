## Standalone Installation

#### Cudf랑 충돌 있음

- Proceed with cudf uninstallation if you're unlikely use the library 

```console
AIRFLOW_VERSION=2.10.4
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

echo "Python: $PYTHON_VERSION"
echo "Airflow to install: $AIRFLOW_VERSION"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERS>

echo "Repository URL: $CONSTRAINT_URL"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

#### First Run

```console
airflow info && airflow version
```

```console
airflow standalone
```

#### Manage Users

```console
airflow users create -e <email> -p <pwd> -r Admin -u <username>
airflow users list
```

#### Watch Connections

```console
airflow connections list
```


## Container-based usage

#### Docker Installtion

```console
sudo groupadd docker
sudo usermod -aG docker $USER
sudo systemctl enable docker.service && sudo systemctl enable containerd.service
docker version && docker ps && docker run hello-world
```

#### Kubernetes (minikube) Installation

```console
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

#### kubectl installation

```console
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubelctl version
```

#### Helm (k8s용 yaml manager) Installtion

```console
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 777 get_helm.sh && ./get_hlem.sh
```

```console
# To upgrade the chart, run
helm repo update
```

#### Airflow Installation

```console
helm repo add apache-airflow https://airflow.apache.org
# For upgrade, remove --install prefix and set --namespace airflow
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace
```
