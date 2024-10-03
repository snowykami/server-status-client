import platform
import threading
import time
from typing import Any

import psutil
import requests

excluded_partition_prefix = ("/var", "/boot", "/run", "/proc", "/sys", "/dev", "/tmp", "/snap")


def log(*args):
    # 在输出前加上时间
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args)


def get_network_speed(interval) -> tuple[int, int]:
    """
    获取网络速度，会阻塞interval秒
    Returns:
        tuple[int, int]: 上行速度, 下行速度
    """
    net1 = psutil.net_io_counters()
    time.sleep(interval)
    net2 = psutil.net_io_counters()
    return net2.bytes_sent - net1.bytes_sent, net2.bytes_recv - net1.bytes_recv


class Hardware:
    mem_total: int = psutil.virtual_memory().total
    mem_used: int = psutil.virtual_memory().used

    swap_total: int = psutil.swap_memory().total
    swap_used: int = psutil.swap_memory().used

    cpu_cores: int = psutil.cpu_count()
    cpu_logics: int = psutil.cpu_count(logical=True)
    cpu_percent: float = psutil.cpu_percent()

    disks: dict[str, dict[str, int]] = {}

    net_up: int = 0
    net_down: int = 0
    net_type: str = "ethernet"


class Api:
    def __init__(self, api_root: str, variables: dict[str, str] = None):
        """
        初始化一个API组
        Args:
            api_root: API根路径，不要用/结尾，且所有类方法参数中的path都前置/但不后置
            variables: 变量，使用{}填充
        """
        self.variables = variables if variables else {}
        self.api_root = api_root.format(self.variables)
        self.headers = {}

    def get(self, path: str, *args, **kwargs) -> requests.Response:
        """
        发送一个GET请求, path中的变量会被替换, 其他参数请使用format
        Args:
            path:
            *args:
            **kwargs:

        Returns:

        """
        path = path.format(self.variables)
        args = self.format(args)
        kwargs = self.format(kwargs)
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
        return requests.get(self.api_root + "/" + path, *args, **kwargs)

    def post(self, path: str, *args, **kwargs) -> requests.Response:
        path = path.format(self.variables)
        args = self.format(args)
        kwargs = self.format(kwargs)
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
        return requests.post(self.api_root + "/" + path, *args, **kwargs)

    def delete(self, path: str, *args, **kwargs) -> requests.Response:
        path = path.format(self.variables)
        args = self.format(args)
        kwargs = self.format(kwargs)
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
        return requests.delete(self.api_root + "/" + path, *args, **kwargs)

    def group(self, path: str) -> "Api":
        """
        获取一个子API
        Args:
            path: 子API路径例如"/user"
        Returns:
            子API对象
        """
        return type(self)(self.api_root + path, self.variables)

    def add_headers(self, **headers):
        """
        添加请求头
        Args:
            **headers: 请求头
        """
        self.headers.update(self.format(headers))

    def format(self, obj: str | list[str] | dict[str, Any]) -> str | list[str] | dict[str, Any]:
        if isinstance(obj, str):
            obj = obj.format(**self.variables)
        elif isinstance(obj, dict):
            for key in obj:
                obj[key] = self.format(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.format(obj[i])
        return obj


class Client:
    def __init__(self, addr: str, token: str, client_id: str, name: str = "", location: str = "", labels: list[str] = [], link: str = "",
                 interval: int = 2):
        self.api = Api(addr, {"token": token, "id": client_id})
        self.api = self.api.group("/client")
        self.api.add_headers(Authorization="{token}")

        self.addr = addr
        self.start_time = None
        self.client_id = client_id
        self.name = name
        self.location = location
        self.labels = labels
        self.link = link
        self.interval = interval

        self.hardware = Hardware()

        log("Client initialized",
            f"Name: {self.name}({self.client_id}), Location: {self.location}, Labels: {self.labels}")

    def start(self):
        self.start_time = time.time()
        self.observe()

        while True:
            try:
                resp = self.get_ping()
                if resp.status_code == 200:
                    log(f"Connected to server {self.addr}")
                    break
                else:
                    log(f"Failed to connect to server {self.addr}, retrying in 5 seconds: {resp.text}")
            except Exception as e:
                log(f"Failed to connect to server {self.addr}, retrying in 5 seconds: {e}")
            time.sleep(5)

        while True:
            try:
                resp = self.post_status()
                if resp.status_code == 200:
                    log("Status updated successfully")
                else:
                    log(f"Failed to post status: {resp.text}")
            except Exception as e:
                log(f"Failed to post status: {e}")
            time.sleep(self.interval)

    def get_ping(self):
        return self.api.get("/ping")

    def post_status(self):
        status = self.get_device_status()
        return self.api.post("/status", json=status)

    def get_device_status(self) -> dict[str, Any]:
        return {
            "meta": {
                "id": self.client_id,
                "name": self.name,
                "os": {
                    "name": platform.system(),
                    "version": platform.version(),
                },
                "labels": self.labels,
                "location": self.location,
                "uptime": int(time.time() - self.start_time),
                "link": self.link,
                "observed_at": int(time.time()),
            },
            "hardware": {
                "mem": {
                    "total": self.hardware.mem_total,
                    "used": self.hardware.mem_used,
                },
                "swap": {
                    "total": self.hardware.swap_total,
                    "used": self.hardware.swap_used,
                },
                "cpu": {
                    "cores": self.hardware.cpu_cores,
                    "logics": self.hardware.cpu_logics,
                    "percent": self.hardware.cpu_percent,
                },
                "disks": self.hardware.disks,
                "net": {
                    "up": self.hardware.net_up,
                    "down": self.hardware.net_down,
                    "type": "ethernet",
                },
            },
        }

    def observe(self):
        """
        观察硬件状态并更新
        Returns:

        """

        def _observe():
            while True:
                self.hardware.mem_total = psutil.virtual_memory().total
                self.hardware.mem_used = psutil.virtual_memory().used
                self.hardware.swap_total = psutil.swap_memory().total
                self.hardware.swap_used = psutil.swap_memory().used
                self.hardware.cpu_cores = psutil.cpu_count(logical=False)
                self.hardware.cpu_logics = psutil.cpu_count(logical=True)
                for part in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(part.mountpoint)

                        if part.mountpoint.startswith(excluded_partition_prefix) or usage.total == 0:
                            continue

                        self.hardware.disks[part.device] = {
                            "total": usage.total,
                            "used": usage.used,
                        }
                    except:
                        pass
                self.hardware.cpu_percent = psutil.cpu_percent(1)
                self.hardware.net_up, self.hardware.net_down = get_network_speed(1)
                log("Observed")

        threading.Thread(target=_observe, daemon=True).start()

    def remove(self, client_id) -> requests.Response:
        return self.api.delete("/host", data={"id": client_id})
