# Service pour publier sonde d'humidité dans OpenShift User Workload Monitoring


Déployer l'application en utilisant la fonctionnalité Source To Image. 
Peut être fait en 2 clics via la console Developer de OpenShift. Add from Git. 

Créer les configmap et secret pour la sonde. Ils sont également partagé avec le service jardin-ai. Seul 

ConfigMap
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: jardin-ai-config
data:
  SONDE_IP: "1.1.1.1"
  VALEUR_SEC: "835"
  VALEUR_HUMIDE: "420"
  SEUIL_ARROSAGE: "30"
  LAT: "latitude"
  LON: "longitude"
  PORT: "8080"
```

Secret
```
apiVersion: v1
kind: Secret
metadata:
  name: jardin-ai-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: YourKey
  WEATHER_API_KEY: YourKey
```

Attach Config and Secret to the deployment
```
template:
    spec:
      containers:
        - name: jardin-ai-metrics-git
          envFrom:
            - configMapRef:
                name: jardin-ai-config
            - secretRef:
                name: jardin-ai-secrets
```

Activer User Workload Monitoring

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
```

Annoter le déploiement
```
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

Créer un objet ServiceMonitor 

```
kind: ServiceMonitor
metadata:
  name: jardin-ai-metrics
  namespace: jardin-ai
spec:
  endpoints:
  - interval: 30s
    port: 8080-tcp
    scheme: http
  selector: 
    matchLabels:
      app: jardin-ai-metrics-git
```
