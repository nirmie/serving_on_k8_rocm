# Serving Models on Kubernetes Cluster with ROCm-Enabled AMD GPUs

## Introdution

## Setup


1. Install [ROCm][rocm] (TODO: ensure X packages)
2. Install [docker-engine][https://docs.docker.com/engine/install/ubuntu/] (for Ubuntu) 
3. Install [cri-dockerd] [https://github.com/Mirantis/cri-dockerd/releases] by choosing the appropriate version for your system
4. Install kubeadm + kubelet + kubectl with package manager
5. Set up control-plane node
6. Add worker nodes
7. Install rocm support
8. Install Kserve


#### Setting Up Master Node (with control-plane)

#### Adding Worker Nodes

### Install k8s-device-plugin to enable GPU support for cluster

[rocm]: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html

completion: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#enable-shell-autocompletion
