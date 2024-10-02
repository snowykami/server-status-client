
<div align="center">

# server-status-client

_✨ 服务器状态 - 客户端 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/snowykami/server-status-client.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/server-status">
    <img src="https://img.shields.io/pypi/v/server-status.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

服务器状态的客户端命令行工具

## 💿 安装

<details open>
<summary>使用 pip 安装(确保包路径在环境变量下)</summary>

    pip install server-status

</details>

Debian系请使用pipx安装

```bash
sudo apt install pipx
pipx install server-status
```

## 🎉 使用

### 命令

- `server_status <server> <token> <id> run` - 运行客户端
- `server_status <server> <token> <id> rm` - 从服务端移除主机

#### 可选项
- `-n|--name` - 设置主机名称
- `--labels` - 设置主机标签
- `--interval` - 设置上报间隔
- `--location` - 设置主机地域
- `--link` - 设置前端点击跳转链接

#### 示例
```shell
server_status https://status.liteyuki.icu 114514 myhost run -n "MyHost" --labels "标签1,标签2" --interval 5 --location "Chongqing" --link "https://example.com"
```

## 📝 其他

### 开机启动
执行以下命令
```shell
sudo touch /etc/systemd/system/server-status-client.service

sudo bash -c 'cat <<EOF > /etc/systemd/system/server-status-client.service
[Unit]
Description=Server Status Client
After=network-online.target

[Service]
Type=simple
ExecStart=sudo server_status <server> <token> <id> run  # 请替换为实际参数
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl enable server-status-client
sudo systemctl start server-status-client
```

### 服务端

请在中心服务器上部署 [server-status-server](https://github.com/snowykami/server-status-server)