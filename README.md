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

- Linux 可使用脚本安装，带自动部署和自启动

```shell
curl -sSL https://raw.githubusercontent.com/snowykami/server-status-client/refs/heads/main/deploy.sh | sudo bash
```

- 或手动部署

```shell
# 克隆仓库
git clone https://github.com/snowykami/server-status-client
cd server-status-client

# 配置环境
python3 -m venv venv
source venv/bin/activate
# 安装依赖
pip install pdm
pdm install

# 如需自启动请自行添加到系统服务
```

## 🎉 使用

### 命令

- `server-status <server> <token> <id> run` - 运行客户端
- `server-status <server> <token> <id> rm` - 从服务端移除主机

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
sudo pipx ensurepath  # 确保pipx路径在环境变量下

sudo touch /etc/systemd/system/server-status-client.service

sudo bash -c 'cat <<EOF > /etc/systemd/system/server-status-client.service
[Unit]
Description=Server Status Client
After=network-online.target

[Service]
Type=simple
ExecStart=server-status <server> <token> <id> run  # 请替换为实际参数
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl enable server-status-client
sudo systemctl start server-status-client
```

### 更新

```shell
git pull
sudo systemctl restart server-status-client
#
git pull
systemctl restart server-status-client
```

### 服务端

请在中心服务器上部署 [server-status-server](https://github.com/snowykami/server-status-server)