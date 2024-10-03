import sys

from server_status.api import *
from server_status.cmd_parser import server_status_alc


def main():
    raw_msg = "server_status " + " ".join(sys.argv[1:])
    print(raw_msg)
    arp = server_status_alc.parse(raw_msg)

    if arp.query("run"):
        sub_opts = arp.subcommands["run"].options
        client = Client(
            addr=arp["server"],
            token=arp["token"],
            client_id=arp["id"],
            name=sub_opts["name"].args["name"],
            location=sub_opts["location"].args["location"],
            labels=sub_opts["labels"].args["labels"],
            interval=sub_opts["interval"].args["interval"],
        )
        client.start()

    elif arp.query("rm"):
        client = Client(
            addr=arp["server"],
            token=arp["token"],
            client_id=arp["id"],
        )
        resp = client.remove(arp["id"])
        if resp.status_code == 200:
            log("Host removed successfully")
        else:
            log(f"Failed to remove host: {resp.text}")

    else:
        log("Unknown command, use 'server_status --help' for help/未知命令或参数错误，请使用 'server_status --help' 获取帮助")


if __name__ == "__main__":
    main()
