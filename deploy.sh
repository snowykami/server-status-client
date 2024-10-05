#!/bin/bash

# check if sudo is used
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# check install dir
install_dir="/opt"
echo -n "Install directory? (default: $install_dir/server-status-client): " && read -r install_dir_input
if [ -n "$install_dir_input" ]; then
    install_dir="$install_dir_input"
fi

# check server
echo -n "Server? (required): " && read -r server
if [ -z "$server" ]; then
    echo "Server is required"
    exit 1
fi

# check token
echo -n "Token? (required): " && read -r token
if [ -z "$token" ]; then
    echo "Token is required"
    exit 1
fi

# check hostname
hostname=$(hostname)
echo -n "Hostname? (default: $hostname): " && read -r hostname_input
if [ -n "$hostname_input" ]; then
    hostname="$hostname_input"
fi

# labels
echo -n "Labels? (space separated): " && read -r labels_input
if [ -n "$labels_input" ]; then
    labels="$labels_input"
fi

# location
echo -n "Location? (optional): " && read -r location_input
if [ -n "$location_input" ]; then
    location="$location_input"
fi

# clone repo
repo1="https://github.com/snowykami/server-status-client"
repo2="https://git.liteyuki.icu/snowykami/server-status-client"
# try 1 if failed try 2
git clone "$repo1" "$install_dir/server-status-client" || git clone "$repo2" "$install_dir/server-status-client"
cd "$install_dir/server-status-client" || { echo "Failed to clone repo"; exit 1; }

# create venv
python3 -m venv venv
python_exe="./venv/bin/python"

# check if venv is created
if [ ! -f "$python_exe" ]; then
    echo "Failed to create venv"
    exit 1
fi
echo "venv created successfully"

# activate the virtual environment


# install the required packages
echo "Installing the required packages"
$python_exe -m pip install pdm
$python_exe -m pdm install

# create the systemd service
echo "Creating the systemd service"

# generate random id
# shellcheck disable=SC2002
id=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

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

echo "server-status-client installed successfully"