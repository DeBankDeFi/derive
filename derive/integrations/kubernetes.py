import os

from opentelemetry.sdk import resources
from opentelemetry.sdk.resources import Resource

import derive
from derive import trace
from derive.integrations import BaseIntegration


class Integration(BaseIntegration):
    def __init__(self):
        attributes: resources.Attributes = {}
        if os.getenv("K8S_CLUSTER_NAME"):
            attributes[resources.KUBERNETES_CLUSTER_NAME] = os.getenv(
                "K8S_CLUSTER_NAME"
            )
        if os.getenv("K8S_NAMESPACE"):
            attributes[resources.KUBERNETES_NAMESPACE_NAME] = os.getenv(
                "K8S_POD_NAMESPACE"
            )
        if os.getenv("K8S_POD_NAME"):
            attributes[resources.KUBERNETES_POD_NAME] = os.getenv("K8S_POD_NAME")
        if os.getenv("K8S_POD_UID"):
            attributes[resources.KUBERNETES_POD_UID] = os.getenv("K8S_POD_UID")
        self.k8s_resource = Resource(attributes)
        derive.update_global_resources(self.k8s_resource)

    @property
    def identifier(self) -> str:
        return "kubernetes"

    def setup_trace(self):
        tracer = trace.get_tracer()
        resource: Resource = getattr(tracer, "resource", Resource.create())
        setattr(tracer, "resource", resource.merge(self.k8s_resource))
