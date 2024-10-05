#!/bin/bash

# 部署脚本中国大陆可用版本

# check if sudo is used
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# check install dir
install_dir="/opt"
echo -n "安装目录? (默认: $install_dir/server-status-client): " && read -r install_dir_input
if [ -n "$install_dir_input" ]; then
    install_dir="$install_dir_input"
fi

# check server
echo -n "服务端地址? (必须): " && read -r server
if [ -z "$server" ]; then
    echo "服务端地址是必须的"
    exit 1
fi

# check token
echo -n "令牌? (必须或留空): " && read -r token

# check hostname
hostname=$(hostname)
echo -n "此主机名? (默认: $hostname): " && read -r hostname_input
if [ -n "$hostname_input" ]; then
    hostname="$hostname_input"
fi

# labels
echo -n "标签们? (空格分隔): " && read -r labels_input
if [ -n "$labels_input" ]; then
    labels="$labels_input"
fi

# location
echo -n "地理位置? (可选|自定义): " && read -r location_input
if [ -n "$location_input" ]; then
    location="$location_input"
fi


repo2="https://git.liteyuki.icu/snowykami/server-status-client"
# try 1 if failed try 2
git clone "$repo2" "$install_dir/server-status-client"
cd "$install_dir/server-status-client" || { echo "克隆失败"; exit 1; }

# create venv
python3 -m venv venv
python_exe="./venv/bin/python"

# check if venv is created
if [ ! -f "$python_exe" ]; then
    echo "创建虚拟环境失败"
    exit 1
fi
echo "虚拟环境创建成功"

# install the required packages
echo "正在安装依赖包..."
$python_exe -m pip install pdm -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
$python_exe -m pdm install

# create the systemd service
echo "正在创建服务..."

# generate random id
# shellcheck disable=SC2002
id=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)

bash -c "cat <<EOF > /etc/systemd/system/server-status-client.service
[Unit]
Description=Server Status Client
After=network-online.target

[Service]
Type=simple
ExecStart=$install_dir/server-status-client/venv/bin/python main.py $server $token $id run -n $hostname --labels $labels --location $location
WorkingDirectory=$install_dir/server-status-client
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# enable and start the service
systemctl enable server-status-client
systemctl start server-status-client

echo "安装完成，服务已启动"