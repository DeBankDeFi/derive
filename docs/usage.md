# Usage


## logging

### logging to FluentBit with TCP

#### Code Example

```python
from configalchemy import BaseConfig

import derive
from derive import logging
from derive.config import DefaultConfig
from derive.integrations import fluentbit

class FluentBitConfig(fluentbit.DefaultConfig):
    ENABLE = False

class deriveConfig(DefaultConfig):
    AWS_XRAY_INTEGRATION_CONFIG = FluentBitConfig()


class Config(BaseConfig):
    CONFIGALCHEMY_ENV_PREFIX = "TEST_"

    derive_CONFIG = deriveConfig()


config = Config()
derive.init(
    config.derive_CONFIG,
    [
        fluentbit.Integration(config.derive_CONFIG.AWS_XRAY_INTEGRATION_CONFIG, config.derive_CONFIG),
    ],
)
logging.info("Hello World") # will be sent to FluentBit
```

#### FluentBif Config Example

`fluent-bit -c fb.conf`

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

## trace

### Simplest Usage

```python
import derive
from derive.trace import trace
derive.init(derive.DefaultConfig())

with trace('my_trace'):
    # do something
    pass
```
### AWS-X-Ray Support in Kubernetes

#### Code Example

```python
from configalchemy import BaseConfig

import derive
from derive.trace import trace
from derive.config import DefaultConfig
from derive.integrations import aws_xray, kubernetes


class AWSXRayConfig(aws_xray.DefaultConfig):
    ENABLE = False


class deriveConfig(DefaultConfig):
    AWS_XRAY_INTEGRATION_CONFIG = AWSXRayConfig()


class Config(BaseConfig):
    CONFIGALCHEMY_ENV_PREFIX = "TEST_"

    derive_CONFIG = deriveConfig()


config = Config()
derive.init(
    config.derive_CONFIG,
    [
        aws_xray.Integration(config.derive_CONFIG.AWS_XRAY_INTEGRATION_CONFIG, config.derive_CONFIG),
        kubernetes.Integration(),
    ],
)
with trace('my_trace'):
    # do something
    pass
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
  name: derive-test-config
data:
  config.json: |-
    {
      "derive_CONFIG": {
        "AWS_XRAY_INTEGRATION_CONFIG": {
          "ENABLE": true,
          "OTLP_ENDPOINT": "<your otlp endpoint>"
        }
      }
    }
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