# Dashboarder


Status:
[![Docker Image CI](https://github.com/javiermarasco/dashboarder/actions/workflows/docker-image.yml/badge.svg)](https://github.com/javiermarasco/dashboarder/actions/workflows/docker-image.yml)

Docker hub image: https://hub.docker.com/r/javilabs/dashboarder

## What it is and what is not

Dashboarder is a kubernetes operator that monitors your whole cluster for two specific CRDs (metrics and query), if a manifest
is found that matches those CRDs a dashboard in Azure is created with the configuration in them.

For the operator to work you need to provide a service principal with at least `PERMISSION` in your subscriptions (those where you
want the dashboards to be created)

The operator uses the Azure `DefaultAzureCredential` which will use the environment variables setup in the operator.

## Configuration

### Azure service principal required

In azure create a service principal and grant it access to create dashboards in the resource groups that you deploy your dashboards.

Then specify in the deployment of the operator the following environment variables with their corresponding values for your service principal.

- AZURE_TENANT_ID
```
This is the id of your azure active directory
```

- AZURE_CLIENT_ID
```
This is the client id of your service principal, also called 'application id'. This is NOT the object id of the service principal.
```

- AZURE_CLIENT_SECRET
```
This is the secret of your service principal, note those secret do expire and you set up the expiration by specifying a duration for the secret, keep in mind that if this secret expires the operator will not be able to modify/create/delete any dashboard.

On expiration, simply create a new one, update the deployment of the operator and delete any old pod for the operator.
```


### Install the CRDs

In the `manifests` folder there are two CRDs that needs to be installed in the kubernetes cluster: 
    - metric_dashboard_crd.yaml
    - query_dashboard_crd.yaml

Each one of those manifest will allow the operator to build a different type of dashboard.

### Deploy the operator

The operator can be deployed with a deployment manifest as the one following:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboarder-deployment
  labels:
    app: dashboarder
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dashboarder
  template:
    metadata:
      labels:
        app: dashboarder
    spec:
      containers:
      - name: dashboarder
        image: javilabs/dashboarder:latest
        imagePullPolicy: Always
        env:
        - name: AZURE_CLIENT_ID
          value: YOUR_SERVICE_PRINCIPAL_ID
        - name: AZURE_TENANT_ID
          value: YOUR_AZURE_TENANT_ID
        - name: AZURE_CLIENT_SECRET
          value: YOUR_SERVICE_PRINCIPAL_SECRET
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
```

This will create a single pod that will monitor the complete cluster for the correct CRDs.

### Create a dashboard

Now you can use one of the demo deployments in the `manifests` folder:

Adjust them following the details in `USAGE.md` and then deploy them with:

`kubectl apply -f dashboard_metric.yaml` or `kubectl apply -f dashboard_query.yaml`

You can check the status with:
    - kubectl get qazd (to check for query dashboards)
    - kubectl get mazd (to check for metric dashboards)

## More resources

You can find information on available metrics [here](https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-supported#microsoftcontainerservicemanagedclusters)

---

### If you find this project interesting please let me know by reaching to me with feedback, it is much appreaciated.
---
