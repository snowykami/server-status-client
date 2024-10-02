import platform
import socket

from arclet.alconna import Alconna, Subcommand, Option, Args, MultiVar

server_status_alc = Alconna(
    "server_status",
    Args["server", str]["token", str]["id", str],
    Subcommand(
        "run",
        Option("-n|--name", Args["name", str, socket.gethostname()], help_text="Host name/主机名称"),
        Option("--location", Args["location", str, "Unknown"], help_text="Host location/主机地理位置"),
        Option("--labels", Args["labels", MultiVar(str), [platform.system()]], help_text="Host labels/主机标签"),
        Option("--link", Args["link", str, None], help_text="Server address/服务器地址"),
        Option("--interval", Args["interval", int, 5], help_text="Interval to send data: 5/发送数据的间隔: 5"),
        help_text="Run the client/运行客户端",
    ),
    Subcommand(
        "rm",
        help_text="Remove the host/移除主机",
    ),
)
