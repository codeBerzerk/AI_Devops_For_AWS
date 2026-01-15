# k8s/eks_wrapper.py
"""
AWS EKS інтеграція
Обгортка для kubectl + AWS CLI для діагностики EKS кластерів
"""

import subprocess
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from utils.logger import logger


@dataclass
class EKSClusterInfo:
    """Інформація про EKS кластер"""
    name: str
    region: str
    version: str
    endpoint: str
    arn: str
    vpc_id: Optional[str] = None
    security_groups: Optional[List[str]] = None
    status: str = "UNKNOWN"


@dataclass
class EKSNodeGroup:
    """Node Group інформація"""
    name: str
    cluster_name: str
    instance_types: List[str]
    desired_size: int
    min_size: int
    max_size: int
    ami_type: str
    disk_size: int
    node_role_arn: str
    status: str


class EKSManager:
    """Управління AWS EKS кластером"""
    
    def __init__(
        self,
        cluster_name: str,
        region: str = "eu-west-1",
        aws_profile: Optional[str] = None
    ):
        self.cluster_name = cluster_name
        self.region = region
        self.aws_profile = aws_profile
        
        # AWS CLI base command
        self.aws_cmd_base = ["aws", "eks"]
        if aws_profile:
            self.aws_cmd_base.extend(["--profile", aws_profile])
        self.aws_cmd_base.extend(["--region", region])
    
    def _run_aws_command(
        self,
        command: List[str],
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        Виконання AWS CLI команди
        
        Args:
            command: Команда для виконання
            capture_output: Чи захоплювати вивід
        
        Returns:
            Result dict з stdout, stderr, returncode
        """
        full_command = self.aws_cmd_base + command
        
        try:
            logger.info(f"Виконання AWS команди: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=capture_output,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": ' '.join(full_command)
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"AWS команда timeout: {' '.join(full_command)}")
            return {
                "success": False,
                "error": "Command timeout",
                "command": ' '.join(full_command)
            }
        
        except Exception as e:
            logger.error(f"Помилка виконання AWS команди: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(full_command)
            }
    
    def _run_kubectl_command(
        self,
        command: List[str],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Виконання kubectl команди
        
        Args:
            command: kubectl команда (без 'kubectl')
            namespace: K8s namespace
        
        Returns:
            Result dict
        """
        full_command = ["kubectl"] + command
        
        if namespace:
            full_command.extend(["-n", namespace])
        
        try:
            logger.info(f"Виконання kubectl: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": ' '.join(full_command)
            }
        
        except Exception as e:
            logger.error(f"Помилка kubectl: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(full_command)
            }
    
    def get_cluster_info(self) -> Optional[EKSClusterInfo]:
        """Отримати інформацію про EKS кластер"""
        
        command = [
            "describe-cluster",
            "--name", self.cluster_name,
            "--output", "json"
        ]
        
        result = self._run_aws_command(command)
        
        if not result["success"]:
            logger.error(f"Не вдалося отримати інформацію про кластер: {result.get('stderr')}")
            return None
        
        try:
            data = json.loads(result["stdout"])
            cluster = data["cluster"]
            
            return EKSClusterInfo(
                name=cluster["name"],
                region=self.region,
                version=cluster["version"],
                endpoint=cluster["endpoint"],
                arn=cluster["arn"],
                vpc_id=cluster.get("resourcesVpcConfig", {}).get("vpcId"),
                security_groups=cluster.get("resourcesVpcConfig", {}).get("securityGroupIds", []),
                status=cluster["status"]
            )
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Помилка парсингу cluster info: {e}")
            return None
    
    def list_node_groups(self) -> List[str]:
        """Список node groups в кластері"""
        
        command = [
            "list-nodegroups",
            "--cluster-name", self.cluster_name,
            "--output", "json"
        ]
        
        result = self._run_aws_command(command)
        
        if not result["success"]:
            return []
        
        try:
            data = json.loads(result["stdout"])
            return data.get("nodegroups", [])
        except:
            return []
    
    def get_nodegroup_info(self, nodegroup_name: str) -> Optional[EKSNodeGroup]:
        """Детальна інформація про node group"""
        
        command = [
            "describe-nodegroup",
            "--cluster-name", self.cluster_name,
            "--nodegroup-name", nodegroup_name,
            "--output", "json"
        ]
        
        result = self._run_aws_command(command)
        
        if not result["success"]:
            return None
        
        try:
            data = json.loads(result["stdout"])
            ng = data["nodegroup"]
            
            return EKSNodeGroup(
                name=ng["nodegroupName"],
                cluster_name=self.cluster_name,
                instance_types=ng.get("instanceTypes", []),
                desired_size=ng.get("scalingConfig", {}).get("desiredSize", 0),
                min_size=ng.get("scalingConfig", {}).get("minSize", 0),
                max_size=ng.get("scalingConfig", {}).get("maxSize", 0),
                ami_type=ng.get("amiType", "UNKNOWN"),
                disk_size=ng.get("diskSize", 0),
                node_role_arn=ng.get("nodeRole", ""),
                status=ng.get("status", "UNKNOWN")
            )
        
        except Exception as e:
            logger.error(f"Помилка парсингу nodegroup info: {e}")
            return None
    
    def update_kubeconfig(self) -> bool:
        """Оновити kubeconfig для доступу до EKS кластеру"""
        
        command = [
            "update-kubeconfig",
            "--name", self.cluster_name
        ]
        
        result = self._run_aws_command(command)
        
        if result["success"]:
            logger.info(f"Kubeconfig оновлено для кластеру {self.cluster_name}")
            return True
        else:
            logger.error(f"Не вдалося оновити kubeconfig: {result.get('stderr')}")
            return False
    
    def get_cloudwatch_logs(
        self,
        log_group: Optional[str] = None,
        minutes_back: int = 60
    ) -> str:
        """
        Отримати CloudWatch логи кластеру
        
        Args:
            log_group: Log group name (default: /aws/eks/{cluster}/cluster)
            minutes_back: Скільки хвилин назад шукати
        
        Returns:
            Логи як string
        """
        if not log_group:
            log_group = f"/aws/eks/{self.cluster_name}/cluster"
        
        # AWS CloudWatch logs через boto3 or AWS CLI
        # TODO: Implement CloudWatch logs retrieval
        
        logger.warning("CloudWatch logs integration - TODO")
        return ""
    
    # ========================================================================
    # KUBECTL WRAPPERS для зручності
    # ========================================================================
    
    def get_pods(
        self,
        namespace: str = "default",
        label_selector: Optional[str] = None
    ) -> List[Dict]:
        """Отримати список pods"""
        
        command = ["get", "pods", "-o", "json"]
        
        if label_selector:
            command.extend(["-l", label_selector])
        
        result = self._run_kubectl_command(command, namespace)
        
        if not result["success"]:
            return []
        
        try:
            data = json.loads(result["stdout"])
            return data.get("items", [])
        except:
            return []
    
    def describe_pod(self, pod_name: str, namespace: str = "default") -> str:
        """Детальний опис pod"""
        
        command = ["describe", "pod", pod_name]
        result = self._run_kubectl_command(command, namespace)
        
        return result.get("stdout", "")
    
    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        container: Optional[str] = None,
        previous: bool = False,
        tail: int = 100
    ) -> str:
        """Отримати логи pod"""
        
        command = ["logs", pod_name, f"--tail={tail}"]
        
        if container:
            command.extend(["-c", container])
        
        if previous:
            command.append("--previous")
        
        result = self._run_kubectl_command(command, namespace)
        
        return result.get("stdout", "")
    
    def get_events(
        self,
        namespace: str = "default",
        field_selector: Optional[str] = None
    ) -> str:
        """Отримати Kubernetes events"""
        
        command = ["get", "events", "--sort-by=.lastTimestamp"]
        
        if field_selector:
            command.extend(["--field-selector", field_selector])
        
        result = self._run_kubectl_command(command, namespace)
        
        return result.get("stdout", "")
    
    # ========================================================================
    # EKS-SPECIFIC ДІАГНОСТИКА
    # ========================================================================
    
    def diagnose_image_pull_issue(
        self,
        pod_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Діагностика ImagePullBackOff для ECR
        
        Returns:
            Diagnostic report
        """
        report = {
            "issue": "ImagePullBackOff",
            "pod": pod_name,
            "namespace": namespace,
            "checks": []
        }
        
        # 1. Pod details
        pod_desc = self.describe_pod(pod_name, namespace)
        report["pod_description"] = pod_desc
        
        # 2. Check if image is from ECR
        if ".dkr.ecr." in pod_desc and ".amazonaws.com" in pod_desc:
            report["checks"].append({
                "name": "Image from ECR",
                "status": "detected",
                "recommendation": "Перевірити IAM permissions для ECR"
            })
            
            # 3. Check node IAM role
            # TODO: Get node IAM role from nodegroup and check ECR policy
        
        # 4. Check events
        events = self.get_events(
            namespace=namespace,
            field_selector=f"involvedObject.name={pod_name}"
        )
        report["events"] = events
        
        return report
    
    def diagnose_loadbalancer_pending(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """Діагностика Service LoadBalancer Pending"""
        
        report = {
            "issue": "LoadBalancer Pending",
            "service": service_name,
            "namespace": namespace,
            "checks": []
        }
        
        # 1. Check AWS Load Balancer Controller
        lb_controller_check = self._run_kubectl_command([
            "get", "deployment",
            "aws-load-balancer-controller",
            "-n", "kube-system"
        ])
        
        if lb_controller_check["success"]:
            report["checks"].append({
                "name": "AWS LB Controller",
                "status": "installed",
                "message": "Controller знайдено"
            })
        else:
            report["checks"].append({
                "name": "AWS LB Controller",
                "status": "missing",
                "message": "Controller НЕ встановлений!",
                "recommendation": "Встановити: helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system"
            })
        
        # 2. Service details
        svc_result = self._run_kubectl_command([
            "get", "svc", service_name, "-o", "yaml"
        ], namespace)
        
        report["service_yaml"] = svc_result.get("stdout", "")
        
        # 3. Events
        events = self.get_events(
            namespace=namespace,
            field_selector=f"involvedObject.name={service_name}"
        )
        report["events"] = events
        
        return report
    
    def get_eks_diagnostic_bundle(self) -> Dict[str, Any]:
        """
        Повний diagnostic bundle для EKS кластеру
        Для troubleshooting
        """
        bundle = {
            "timestamp": datetime.now().isoformat(),
            "cluster": {}
        }
        
        # 1. Cluster info
        cluster_info = self.get_cluster_info()
        if cluster_info:
            bundle["cluster"] = {
                "name": cluster_info.name,
                "version": cluster_info.version,
                "status": cluster_info.status,
                "vpc_id": cluster_info.vpc_id,
                "region": self.region
            }
        
        # 2. Node groups
        nodegroups = self.list_node_groups()
        bundle["nodegroups"] = []
        
        for ng_name in nodegroups:
            ng_info = self.get_nodegroup_info(ng_name)
            if ng_info:
                bundle["nodegroups"].append({
                    "name": ng_info.name,
                    "instance_types": ng_info.instance_types,
                    "desired_size": ng_info.desired_size,
                    "status": ng_info.status
                })
        
        # 3. Kubernetes resources summary
        bundle["k8s"] = {}
        
        # Nodes
        nodes_result = self._run_kubectl_command(["get", "nodes", "-o", "json"])
        if nodes_result["success"]:
            try:
                nodes_data = json.loads(nodes_result["stdout"])
                bundle["k8s"]["nodes_count"] = len(nodes_data.get("items", []))
            except:
                pass
        
        # Pods (all namespaces)
        pods_result = self._run_kubectl_command([
            "get", "pods", "--all-namespaces", "-o", "json"
        ])
        if pods_result["success"]:
            try:
                pods_data = json.loads(pods_result["stdout"])
                pods = pods_data.get("items", [])
                
                # Count by status
                status_count = {}
                for pod in pods:
                    status = pod.get("status", {}).get("phase", "Unknown")
                    status_count[status] = status_count.get(status, 0) + 1
                
                bundle["k8s"]["pods"] = {
                    "total": len(pods),
                    "by_status": status_count
                }
            except:
                pass
        
        return bundle


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def setup_eks_access(cluster_name: str, region: str) -> bool:
    """
    Швидке налаштування доступу до EKS кластеру
    
    Args:
        cluster_name: Назва EKS кластеру
        region: AWS region
    
    Returns:
        Success status
    """
    manager = EKSManager(cluster_name, region)
    
    # Update kubeconfig
    if not manager.update_kubeconfig():
        logger.error("Не вдалося налаштувати kubeconfig")
        return False
    
    # Verify access
    test_cmd = manager._run_kubectl_command(["get", "nodes"])
    
    if test_cmd["success"]:
        logger.info("✅ Доступ до EKS кластеру налаштовано")
        return True
    else:
        logger.error("❌ Не вдалося підключитись до кластеру")
        return False