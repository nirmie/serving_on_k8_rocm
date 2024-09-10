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
- If you already have Docker engine, it could work without an installation. However, you may be able to avoid unseen errors by reinstalling Docker Engine on a clean slate by following the instructions in the linked document.
- 
### 3. Install [cri-dockerd][dockerd]
- Ensure it is the right version for the system (in the following example I use the Jammy 22.04 version as it still works on Noble 24.04)
- The prebuilt binaries should be the easiest to install, and can be done so with running:
```
wget https://github.com/Mirantis/cri-dockerd/releases/download/v0.3.15/cri-dockerd_0.3.15.3-0.ubuntu-jammy_amd64.deb
sudo apt-get install ./cri-dockerd_0.3.15.3-0.ubuntu-jammy_amd64.deb
```
If installing another version, make sure to update the file names with the proper ones.

start the service with `sudo systemctl daemon-reload`

### 4. Install [kubeadm + kubelet + kubectl][kubeadm]
- set up [kubectl cli autocompletion][completion] (optional)

### 5.  Set up Control Plane Node
-   Set hostname (this name will be used for pod names). You can replace `master-node` with a name of your choice, just remember which node is the control point node.
```
hostnamectl set-hostname master-node
```
-   Set necessary environmental variables (IPADDR is currently set to local IP, for public IP use `IPADDR=$(curl ifconfig.me && echo "")` instead.
```
IPADDR=$(hostname -I)
NODENAME=$(hostname -s)
POD_CIDR="192.168.0.0/16"
```
-   Command for initialization:
```
sudo kubeadm init --control-plane-endpoint=$IPADDR  --apiserver-cert-extra-sans=$IPADDR  --pod-network-cidr=$POD_CIDR --node-name $NODENAME --cri-socket unix:///var/run/cri-dockerd.sock
```
-   After initialization, make sure to copy the join command and save it somewhere as it will be used later for the worker nodes. You can also regenerate this command with `kubeadm token create --print-join-command` later if needed.
- Create `kubeconfig` so kubectl can function properly:
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
-   Run `kubectl cluster-info` to verify kubectl works. CoreDNS will function properly after setting up a network plugin.
-   If you are not planning on adding worker nodes, or you would like the control plane node to run pods too, you can remove taints on the node:
```
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

### 6. Set up container networking with [Canal][canal]
-    We will be using Canal, which includes flannel for pod networking across hosts with VXLAN and calico for network policies and pod to pod networking
-    install Canal using the recommended method with Kubernetes API datastore
-    You can use other CNIs as well, but ensure they are compatible with kubeadm and MetalLB if you decide to use the loadbalancer

### 7.  Add worker nodes [optional]
-   Use the join command saved from before on the worker nodes after installing all requirements. You can reprint it by running `kubeadm token create --print-join-command` on the control plane node. Make sure to use `sudo` if running as a normal user.
-   Run `kubectl get nodes` on the master node to ensure the worker node appears and is detected by the master node.
-   You can add roles for nodes by labelling the node with the following command (reokace /<node_name/> with the proper node name listed with `kubectl get nodes`:
```
kubectl label node <node_name>  node-role.kubernetes.io/worker=worker
```
- You can repeat these 3 steps on as many worker nodes as you would like, as long as the prequisites and necessary isntallation steps have already been met for each node.

### 8. Install ROCm support
-   install [k8s ROCm plugin][rocm_plugin]
-   make to use the labeller also specifed in the github to enable `amd.com/gpu` 

### 9. Install [MetalLB LoadBalancer][metallb] (optional, but I recommend)
Do so if you would like an external IP to send inference requests to instead of only operating within tbe cluster using Cluster IPs.
- Install by manifest and configure to set up [layer 2 networking][layer2]

### 10. Install [KServe][kserve]
- Ensure to follow all of its directions, including the Istio installation as it will be how we can route requests to our inference service.

### 11. Optional: Install [vLLM in Docker container] [vllm]
-   One can also choose to use the container I have already created that works with MI series GPUs. However, you may have specific requirements in which it would be pr eferable to build your own container.
-   Follow Option 1, building within a container
-   After building it, make sure to push it to a valid repository so it can be called by the inference service. Make sure to update the image argument in the inference service to point to your container.

### 12. Start InferenceService with OpenAI compatible Server
-   create namespace to launch inference service. Here we will use `model`, but you can use any valid namespace name.
```
kubectl create namespace model
```
Referring to the inference file linked in the repo named `llama3.1-openai-chat.yaml`:
-   Add your huggingface token in `spec.predictor.containers.env` (environmental variable), replacing `$HF_TOKEN` with your key. You can also simply update the `HF_TOKEN` bash variable to be your token with `export HF_TOKEN=<your_token>` by replacing `\<your_token\>` everytime before you wish to launch the inference service.
-   If running on 7900s or other gpus that do not support NCCL P2P, make sure to uncomment the following lines in the llama3.1-openai-chat.yaml file:
```
#        - name: NCCL_P2P_DISABLE
#          value: "1"
```
This sets an environmental variable that tells vllm to not use the unsupported feature.
- Finally, launch the inference service with
```
kubectl apply -f llama3.1-openai-chat.yaml -n model
```

### 13. Send Inference Requests to model
- running `kubectl get isvc -n model` should lead to the following:
```
kubectl get inferenceservices sklearn-iris -n kserve-test
NAME           URL                                                 READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION      AGE
llama3         http://llama3.model.example.com                     True           100                              llama3-predictor-00001   20m
```
Here we can see the DNS is not set yet, as it is .example.com. For testing purposes, we can use a magic domain `sslip.io` to get a usable domain.
First find the IP address to use. Run the following command below in your terminal:
```
kubectl get svc istio-ingressgateway --namespace istio-system
```
If the output has a value sets under `EXTERNAL-IP`, use that IP address. If there is no usable IP, then you the `CLUSTER-IP`, however you will be limited to working within the cluster. (I personally tested with EXTERNAL_IP)
Set up the domain with this command:
```
kubectl edit cm config-domain --namespace knative-serving
```
In the editor change example.com to {{external-ip}}.sslip.io (make sure to replace {{external-ip}} with the IP, either the `EXTERNAL-IP` or `CLUSTER-IP` that you found earlier).

Save the file. (You may need to restart the inference service to update the address by deleting the inference service with `kubectl delete isvc -n model llama3` and redo step the launch with `kubectl apply -f llama3.1-openai-chat.yaml -n model`. 

With the change applied you can find the URL with `kubectl get isvc -n model`.
Now, you can directly curl the URL or use `streaming.py` to run inference, replacing `http://llama3.model.192.168.2.100.sslip.io` with the URL you found. Make sure to keep the `/v1` at the end of the URL.

To Curl:
```
curl http://llama3.model.192.168.2.100.sslip.io/v1/chat/completions   -H "Content-Type: application/json"   -H "Authorization: Bearer token-abc123"   -d '{
     "model": "llama3",
     "messages": [{"role": "user", "content": "What are some of the best movies ever produced?"}],
     "temperature": 0.1,
     "stop": ["\n", "<|endoftext|>"],
     "max_tokens": 100
   }'
```

To use streaming.py, edit the base_url variable in the client line, replacing the URL with your URL. Make sure to include the `/v1` at the end of the URL.
```
from openai import OpenAI

client = OpenAI(
        #base_url = "http://10.244.1.8:8080/v1",
        base_url = "http://llama3.model.192.168.2.100.sslip.io/v1",
        api_key="token-abc123",
    )

stream = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Who is the greatest of all time in basketball and why?"}],
    stream=True,
    max_tokens = 100,
    stop=["\n", "<|endoftext|>"],
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```
Then, run `python3 streaming.py`.

### 14. Enjoy!
With the URL you have, you can send any open AI compliant requests as long as the proper chat template is specified in the inference service yaml file. If you wish to work with completions instead of chat, change the '--chat-template` argument value to point to an accepted template currently in the vllm container.


[rocm]: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html
[docker-engine]: https://docs.docker.com/engine/install/ubuntu/
[dockerd]: https://github.com/Mirantis/cri-dockerd/releases
[kubeadm]: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#installing-kubeadm-kubelet-and-kubectl
[canal]: https://docs.tigera.io/calico/latest/getting-started/kubernetes/flannel/install-for-flannel
[completion]: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#enable-shell-autocompletion
[rocm_plugin]: https://github.com/ROCm/k8s-device-plugin?tab=readme-ov-file#deployment
[metallb]: https://metallb.universe.tf/installation/
[layer2]: https://metallb.universe.tf/configuration/#layer-2-configuration
[kserve]: https://kserve.github.io/website/master/admin/serverless/serverless/#5-install-kserve-built-in-clusterservingruntimes
[vllm]: https://docs.vllm.ai/en/latest/getting_started/amd-installation.html
