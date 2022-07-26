# Usage

init: 

```python
import derive
derive.init(derive.DefaultConfig())
```

## logging

```python
from derive import logging
logging.info("test")
```

## trace

```python
import derive
from derive.trace import trace

@trace("test")
def test():
    pass

@trace("async_test")
async def async_test():
    pass

with trace('my_trace'):
    # do something
    pass
```

## metrics

```python
from derive.metrics import Counter, Summary, Gauge, Histogram
from derive.metrics.exporter import PrometheusExporter

c = Counter("my_failures_total", "Description of counter")
c.inc()  # Increment by 1
c.inc(1.6)  # Increment by given value
g = Gauge("my_inprogress_requests", "Description of gauge")
g.inc()  # Increment by 1
g.dec(10)  # Decrement by given value
g.set(4.2)  # Set to a given value
s = Summary("request_size_bytes", "Request size (bytes)")
s.observe(512)  # Observe 512 (bytes)
h = Histogram("request_size_bytes_histogram", "Request size (bytes)")
h.observe(512)  # Observe 512 (bytes)

print(PrometheusExporter.generate_latest())
```

# Integrations

## FluentBit TCP Input

### Code Example

```python
from configalchemy import BaseConfig

import derive
from derive import logging
from derive.config import DefaultConfig
from derive.integrations import fluentbit

class FluentBitConfig(fluentbit.DefaultConfig):
    ENABLE = False

class DeriveConfig(DefaultConfig):
    FLUENT_BIT_INTEGRATION_CONFIG = FluentBitConfig()


class Config(BaseConfig):
    DERIVE_CONFIG = DeriveConfig()


config = Config()
derive.init(
    config.DERIVE_CONFIG,
    [
        fluentbit.Integration(config.DERIVE_CONFIG.FLUENT_BIT_INTEGRATION_CONFIG),
    ],
)
logging.info("Hello World") # will be sent to FluentBit with TCP
```

### FluentBit Config Example

run command: `fluent-bit -c fb.conf`

- fb.conf:
```text
[INPUT]
    Name tcp
    Format json

[FILTER]
    Name lua
    Match *
    script filters.lua
    call set_time

[OUTPUT]
    Name stdout
    Match *
```
- filters.lua:
```lua
function set_time(tag, timestamp, record)
    local timestamp = record["Timestamp"]
    record["Timestamp"] = nil
    return 1, timestamp, record
end
```

## AWS X-Ray

### Usage

```python
from configalchemy import BaseConfig

import derive
from derive.config import DefaultConfig
from derive.integrations import aws_xray


class AWSXRayConfig(aws_xray.DefaultConfig):
    ENABLE = True


class DeriveConfig(DefaultConfig):
    AWS_XRAY_INTEGRATION_CONFIG = AWSXRayConfig()


class Config(BaseConfig):
    DERIVE_CONFIG = DeriveConfig()


config = Config()
derive.init(
    config.DERIVE_CONFIG,
    [
        aws_xray.Integration(config.DERIVE_CONFIG.AWS_XRAY_INTEGRATION_CONFIG),
    ],
)
```
### OLTP Config

reference: https://aws-otel.github.io/docs/setup/eks

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  memory_limiter:
    limit_mib: 100
    check_interval: 5s

exporters:
  awsxray:
    region: ap-northeast-1

extensions:
  awsproxy:

service:
  extensions: [awsproxy]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter]
      exporters: [awsxray]
```


## Kubernetes

Kubernetes Resources integration.

### Manifest

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test
spec:
  containers:
  - name: app
    env:
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
```


# Best Practices

### Support aws x-ray and fluent bit in kubernetes

#### Code Example

```python
from configalchemy import BaseConfig

import derive
from derive.config import DefaultConfig
from derive.integrations import aws_xray, kubernetes, fluentbit

class FluentBitConfig(fluentbit.DefaultConfig):
    ENABLE = False

class AWSXRayConfig(aws_xray.DefaultConfig):
    ENABLE = False


class DeriveConfig(DefaultConfig):
    AWS_XRAY_INTEGRATION_CONFIG = AWSXRayConfig()
    FLUENT_BIT_INTEGRATION_CONFIG = FluentBitConfig()


class Config(BaseConfig):
    CONFIGALCHEMY_ENV_PREFIX = "TEST_"

    DERIVE_CONFIG = DeriveConfig()


config = Config()
derive.init(
    config.DERIVE_CONFIG,
    [
        kubernetes.Integration(),
        aws_xray.Integration(config.DERIVE_CONFIG.AWS_XRAY_INTEGRATION_CONFIG),
        fluentbit.Integration(config.DERIVE_CONFIG.FLUENT_BIT_INTEGRATION_CONFIG),
    ],
)
```

#### Kubernetes Manifest Example

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
        value: /config/config.json
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
    volumeMounts:
      - mountPath: /config
        name: config
  volumes:
    - name: config
      configMap:
        name: derive-test-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: derive-test-config
data:
  config.json: |-
    {
      "DERIVE_CONFIG": {
        "AWS_XRAY_INTEGRATION_CONFIG": {
          "ENABLE": true,
          "OTLP_ENDPOINT": "<your otlp endpoint>"
        },
        "FLUENT_BIT_INTEGRATION_CONFIG": {
          "ENABLE": true,
          "TCP_HOST": "<your fluent bit host>",
          "TCP_PORT": "<your fluent bit port>"
        }
      }
    }
```