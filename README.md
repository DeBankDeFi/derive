# Pillar: The Python Observability Toolkit Bsed on OpenTelemetry

# Simplest Usage

```python
import pillar
from pillar.trace import trace
pillar.init(pillar.DefaultConfig())

with trace('my_trace'):
    # do something
    pass
```

## AWS-X-Ray Support in Kubernetes

code: 

```python
from configalchemy import BaseConfig

import pillar
from pillar.trace import trace
from pillar.config import DefaultConfig
from pillar.integrations import aws_xray, kubernetes


class AWSXRayConfig(aws_xray.DefaultConfig):
    ENABLE = False


class PillarConfig(DefaultConfig):
    AWS_XRAY_INTEGRATION_CONFIG = AWSXRayConfig()


class Config(BaseConfig):
    CONFIGALCHEMY_ENV_PREFIX = "TEST_"

    PILLAR_CONFIG = PillarConfig()


config = Config()
pillar.init(
    config.PILLAR_CONFIG,
    [
        aws_xray.Integration(config.PILLAR_CONFIG.AWS_XRAY_INTEGRATION_CONFIG),
        kubernetes.Integration(),
    ],
)
with trace('my_trace'):
    # do something
    pass
```

Kubernetes:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test
spec:
  containers:
  - name: app
    env:
      - name: TEST_CONFIGALCHEMY_CONFIG_FILE
        value: <your json config file>
      - name: K8S_CLUSTER_NAME
        value: production
      - name: K8S_POD_NAMESPACE
        valueFrom:
          fieldRef:
            fieldPath: metadata.namespace
      - name: K8S_POD_NAME
        valueFrom:
          fieldRef:
            fieldPath: metadata.name
      - name: K8S_POD_UID
        valueFrom:
          fieldRef:
            fieldPath: metadata.uid
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: pillar-test-config
data:
  config.json: |-
    {
      "PILLAR_CONFIG": {
        "AWS_XRAY_INTEGRATION_CONFIG": {
          "ENABLE": true,
          "OTLP_ENDPOINT": "<your otlp endpoint>"
        }
      }
    }
```