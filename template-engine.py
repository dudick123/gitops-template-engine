import os
import yaml
from jinja2 import Environment, FileSystemLoader
from kubernetes import client, config

# Load Kubernetes config
config.load_kube_config()

# Initialize the Kubernetes API client
api = client.CustomObjectsApi()
core_api = client.CoreV1Api()

# Load templates
template_dir = "./templates"
env = Environment(loader=FileSystemLoader(template_dir))

def render_template(template_name, context):
    template = env.get_template(template_name)
    return template.render(context)

def apply_manifest(manifest):
    manifest_data = yaml.safe_load(manifest)
    kind = manifest_data["kind"]
    
    if kind == "Namespace":
        core_api.create_namespace(manifest_data)
    elif kind == "AppProject":
        api.create_namespaced_custom_object(
            group="argoproj.io", version="v1alpha1", namespace="argocd", 
            plural="appprojects", body=manifest_data
        )
    elif kind == "ApplicationSet":
        api.create_namespaced_custom_object(
            group="argoproj.io", version="v1alpha1", namespace="argocd", 
            plural="applicationsets", body=manifest_data
        )

def create_namespace(context):
    manifest = render_template("namespace.yaml.j2", context)
    print(f"Applying Namespace:\n{manifest}")
    apply_manifest(manifest)

def create_project(context):
    manifest = render_template("appproject.yaml.j2", context)
    print(f"Applying AppProject:\n{manifest}")
    apply_manifest(manifest)

def create_applicationset(context):
    manifest = render_template("applicationset.yaml.j2", context)
    print(f"Applying ApplicationSet:\n{manifest}")
    apply_manifest(manifest)

def main(manifest_file):
    # Load YAML manifest file
    with open(manifest_file, "r") as file:
        data = yaml.safe_load(file)
    
    # Extract contexts
    namespace_context = data.get("namespace", {})
    appproject_context = data.get("appproject", {})
    applicationset_context = data.get("applicationset", {})

    # Render and apply resources
    if namespace_context:
        print("Creating Namespace...")
        create_namespace(namespace_context)
    if appproject_context:
        print("Creating AppProject...")
        create_project(appproject_context)
    if applicationset_context:
        print("Creating ApplicationSet...")
        create_applicationset(applicationset_context)

if __name__ == "__main__":
    manifest_file = "resources.yaml"
    main(manifest_file)
