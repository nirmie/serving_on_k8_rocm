# Serving vLLM Models on Kubernetes Cluster with ROCm-Enabled AMD GPUs using KServe for Linux

## Introdution



## Prerequisites (for all nodes):
- ensure swap space is turned off:
```
sudo swapoff -a
```
- Compatible Linux Host (Most Debian/Red Hat Distros should work)
- Complete Network Connectivity between nodes
- Unique hostname, MAC address, and product_uuid for every node (most likely already true)
    - check mac addresses with `ip link` or `ifconfig -a`
    - check product_uiuds with `sudo cat /sys/class/dmi/id/product_uuid`
- Ensure the required ports for all components are open
    - [Kuberernetes Required Ports][k8_ports]
    - [Istio Required Ports][istio_ports]
    - may be easier to simply disable firewall with `sudo ufw disable` (if your deployment allows it)
        - If you plan on using huggingface or some other online storage for the model, it will be easier with firewall off
- Ensure the ports are not in use either with `nc 127.0.0.1 \<port-num\> -v` where <port-num> is the port to check
 

[k8_ports]: https://kubernetes.io/docs/reference/networking/ports-and-protocols/
[istio_ports]: https://istio.io/latest/docs/ops/deployment/application-requirements/#ports-used-by-istio
## Setup

### 1. Install [ROCm][rocm]
### 2. Install [Docker Engine][docker-engine] (for Ubuntu)
### 3. Install [cri-dockerd][dockerd]
- Ensure it is the right version for the system
### 4. Install [kubeadm + kubelet + kubectl][kubeadm]
- set up [kubectl cli autocompletion][completion] (optional)
### 5.  Set up Control Plane Node
-   kubeadm init
### 6. Set up container networking with Canal
- We will be using Canal, which includes flannel for pod networking across hosts with VXLAN and calico for network policies and pod to pod networking
- You can use other CNIs as well, but ensure they are compatible with kubeadm and MetalLB if you decide to use the loadbalancer
### 7.  Add worker nodes [optional]
-   kubeadm join
### 8. Install ROCm support
-   install [k8s ROCm plugin][rocm_plugin]
-   make to use the labeller also specifed in the github
### 9. Install [MetalLB LoadBalancer][metallb] (optional)
Do so if you would like an external IP to send inference requests to instead of only operating within tbe cluster using Cluster IPs.
- Install by manifest and configure to set up layer 2 networking 
### 10. Install [KServe][kserve]
### 11. Install [vLLM in Docker container] [vllm]
-   build in docker
### 12. Start InferenceService with OpenAI compatible Server
-   inference file linked in github (edit as needed)
-   Add your huggingface token in `spec.predictor.containers.env` (environmental variable), replacing `$HF_TOKEN` with your key. You can also simply update the `HF_TOKEN` bash variable to be your token with `export HF_TOKEN=<your_token>` by replacing `\<your_token\>` everytime before you wish to launch the inference service.
-   If running on MI series AMD GPUs, leave file as is. If running on 7900s or other AMD GPUs, make sure to uncomment the following lines in the llama3.1-openai-chat.yaml file:
```
#        - name: NCCL_P2P_DISABLE
#          value: "1"
```
- launch inference service with
```
kubectl apply -f llama3.1-openai-chat.yaml -n model
```
### 13. Send Inference Requests to model
- running 'kubectl get isvc -n model' should lead to the following:
### 13. Enjoy!


#### Setting Up Master Node (with control-plane)

#### Adding Worker Nodes

### Install k8s-device-plugin to enable GPU support for cluster

[rocm]: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html
[docker-engine]: https://docs.docker.com/engine/install/ubuntu/
[dockerd]: https://github.com/Mirantis/cri-dockerd/releases
[kubeadm]: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/
[completion]: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#enable-shell-autocompletion
[rocm_plugin]: https://github.com/ROCm/k8s-device-plugin?tab=readme-ov-file#deployment
[metallb]: https://metallb.universe.tf/installation/
