import subprocess
import json
from typing import Dict, List, Optional, Any

from utils.logger import logger


class KubectlWrapper:
    """Generic kubectl wrapper (не EKS-специфічний)"""

    def __init__(self, kubeconfig: Optional[str] = None) -> None:
        self.kubeconfig = kubeconfig

    def _build_command(self, command: List[str]) -> List[str]:
        """Build kubectl command with kubeconfig"""
        cmd: List[str] = ["kubectl"]

        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])

        cmd.extend(command)
        return cmd

    def run(
        self,
        command: List[str],
        namespace: Optional[str] = None,
        output_format: Optional[str] = "json",
    ) -> Dict[str, Any]:
        """
        Execute kubectl command

        Args:
            command: kubectl args (without 'kubectl')
            namespace: k8s namespace
            output_format: json, yaml, or wide

        Returns:
            Result dict
        """
        full_cmd = self._build_command(command)

        if namespace:
            full_cmd.extend(["-n", namespace])

        if output_format and output_format in ["json", "yaml"]:
            full_cmd.extend(["-o", output_format])

        try:
            logger.debug(f"Виконання: {' '.join(full_cmd)}")

            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(full_cmd),
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Kubectl timeout: {' '.join(full_cmd)}")
            return {
                "success": False,
                "error": "Command timeout",
                "command": " ".join(full_cmd),
            }

        except Exception as e:  # pragma: no cover - захист від неочікуваних помилок
            logger.error(f"Kubectl error: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(full_cmd),
            }

    def get(
        self,
        resource: str,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """kubectl get"""
        cmd: List[str] = ["get", resource]

        if name:
            cmd.append(name)

        if label_selector:
            cmd.extend(["-l", label_selector])

        result = self.run(cmd, namespace=namespace, output_format="json")

        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except Exception:
                return {}

        return {}

    def describe(
        self,
        resource: str,
        name: str,
        namespace: Optional[str] = None,
    ) -> str:
        """kubectl describe"""
        cmd = ["describe", resource, name]
        result = self.run(cmd, namespace=namespace, output_format=None)
        return result.get("stdout", "")

    def logs(
        self,
        pod_name: str,
        namespace: Optional[str] = None,
        container: Optional[str] = None,
        previous: bool = False,
        tail: int = 100,
    ) -> str:
        """kubectl logs"""
        cmd: List[str] = ["logs", pod_name, f"--tail={tail}"]

        if container:
            cmd.extend(["-c", container])

        if previous:
            cmd.append("--previous")

        result = self.run(cmd, namespace=namespace, output_format=None)
        return result.get("stdout", "")

    def exec(
        self,
        pod_name: str,
        command: List[str],
        namespace: Optional[str] = None,
        container: Optional[str] = None,
    ) -> str:
        """kubectl exec"""
        cmd: List[str] = ["exec", pod_name]

        if container:
            cmd.extend(["-c", container])

        cmd.extend(["--", *command])

        result = self.run(cmd, namespace=namespace, output_format=None)
        return result.get("stdout", "")


# Global instance
kubectl = KubectlWrapper()

