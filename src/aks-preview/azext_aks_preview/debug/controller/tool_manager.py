import os
import subprocess

from knack.log import get_logger

from ..common.consts import DEBUG_TOOL_DIR

logger = get_logger(__name__)


class ToolManager:
    def __init__(self) -> None:
        self.tool_dir = DEBUG_TOOL_DIR

    def get_tool_dir(self) -> str:
        return self.tool_dir

    def ensure_tool_dir(self) -> None:
        if not os.path.exists(self.tool_dir):
            os.makedirs(self.tool_dir)

    def get_kubectl_path(self) -> str:
        return os.path.join(self.tool_dir, "kubectl")

    def local_install_kubectl(self) -> None:
        if os.path.exists(self.get_kubectl_path()):
            logger.debug("[tool manager] kubectl already exists")
            return
        logger.info("[tool manager] kubectl not exists, will install it to %s", self.get_kubectl_path())
        self.ensure_tool_dir()
        subprocess.run(
            [
                "curl",
                "-LO",
                "https://dl.k8s.io/release/v1.29.9/bin/linux/amd64/kubectl",
            ],
            cwd=self.tool_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            [
                "chmod",
                "+x",
                "kubectl",
            ],
            cwd=self.tool_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("[tool manager] kubectl installed successfully")
        return

    def get_kubectl_inspektor_gadget_path(self) -> str:
        return os.path.join(self.tool_dir, "kubectl-gadget")

    def local_install_kubectl_inspektor_gadget(self) -> None:
        if os.path.exists(self.get_kubectl_inspektor_gadget_path()):
            logger.debug("[tool manager] kubectl-gadget already exists")
            return
        logger.info("[tool manager] kubectl-gadget not exists, will install it to %s", self.get_kubectl_inspektor_gadget_path())
        self.ensure_tool_dir()
        subprocess.run(
            [
                "curl",
                "-LO",
                "https://github.com/inspektor-gadget/inspektor-gadget/releases/download/v0.34.0/kubectl-gadget-linux-amd64-v0.34.0.tar.gz",
            ],
            cwd=self.tool_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            [
                "tar",
                "-xvf",
                "kubectl-gadget-linux-amd64-v0.34.0.tar.gz",
            ],
            cwd=self.tool_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            [
                "chmod",
                "+x",
                "kubectl-gadget",
            ],
            cwd=self.tool_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("[tool manager] kubectl-gadget installed successfully")
        return

    def remote_install_inspektor_gadget(self) -> str:
        self.local_install_kubectl_inspektor_gadget()
        p = subprocess.run(
            [
                "kubectl",
                "gadget",
                "version",
            ],
            cwd=self.tool_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if "Server version: not installed" in p.stdout.decode("utf-8"):
            logger.info("[tool manager] inspektor gadget not installed to cluster, will install it")
            subprocess.run(
                [
                    "kubectl",
                    "gadget",
                    "deploy",
                ],
                cwd=self.tool_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("[tool manager] inspektor gadget installed to cluster successfully")
        else:
            logger.debug("[tool manager] inspektor gadget already installed to cluster")
        return
