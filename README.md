# Serving vLLM Models on Kubernetes Cluster with ROCm-Enabled AMD GPUs using KServe for Linux

## Introdution

## Setup


1.   **Install [ROCm][rocm] (TODO: ensure X packages)**
2.   **Install [docker-engine][https://docs.docker.com/engine/install/ubuntu/] (for Ubuntu) **
3.   **Install [cri-dockerd] [https://github.com/Mirantis/cri-dockerd/releases]**
    - Ensure it is the right version for the system
4.   **Install kubeadm + kubelet + kubectl with package manager**
      - set up [kubectl cli autocompletion] [completion] (optional)
5. **Set up Control Plane Node**
    -   kubeadm init
      - 
6. **Add worker nodes [optional]**
7. **Install ROCm support**
8. **Install [KServe][kserve]**
9. **Install [vLLM in Docker container] [vllm]**
10. **Start InferenceService with OpenAI compatible Server**
11. **Enjoy!**


#### Setting Up Master Node (with control-plane)

#### Adding Worker Nodes

### Install k8s-device-plugin to enable GPU support for cluster

[rocm]: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html

[completion]: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#enable-shell-autocompletion
