#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# You can change these variables if needed.
PROJECT_NAME="datetime_tool"
APP_USER="${PROJECT_NAME}_user"

# The final destination for your application code.
PROJECT_DIR="/opt/${PROJECT_NAME}"

# The source directory where your code (main.py, requirements.txt, etc.) is located.
# IMPORTANT: Make sure this directory exists and contains your files before running!
SOURCE_DIR_OWNER=$(logname) # Gets the user running sudo
SOURCE_DIR="/home/${SOURCE_DIR_OWNER}/datetime_tool_source"

VENV_DIR="${PROJECT_DIR}/venv"
GUNICORN_WORKERS=3 # Adjust based on your server's CPU cores

echo "--- Starting FastAPI Service Setup (No .env) ---"

# --- 1. Pre-flight Check ---
echo ">>> [1/7] Checking for source directory at ${SOURCE_DIR}..."
if [ ! -d "${SOURCE_DIR}" ]; then
    echo "Error: Source directory '${SOURCE_DIR}' not found."
    echo "Please create it and place your application files inside."
    exit 1
fi
if [ ! -f "${SOURCE_DIR}/main.py" ] || [ ! -f "${SOURCE_DIR}/requirements.txt" ]; then
    echo "Error: 'main.py' or 'requirements.txt' not found in source directory."
    exit 1
fi
echo "Source directory found."

# --- 2. System Update and Package Installation ---
echo ">>> [2/7] Updating system packages and installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx

# --- 3. Create Application User ---
echo ">>> [3/7] Creating a dedicated system user '${APP_USER}'..."
if id -u "${APP_USER}" >/dev/null 2>&1; then
    echo "User '${APP_USER}' already exists. Skipping creation."
else
    sudo useradd --system --no-create-home --shell /bin/false ${APP_USER}
    echo "User '${APP_USER}' created."
fi

# --- 4. Copy Application Code to /opt ---
echo ">>> [4/7] Setting up project directory at ${PROJECT_DIR}..."
sudo mkdir -p ${PROJECT_DIR}
echo "Copying application files from ${SOURCE_DIR}..."
sudo cp -r "${SOURCE_DIR}/." "${PROJECT_DIR}/"
sudo chown -R ${APP_USER}:${APP_USER} ${PROJECT_DIR}

# --- 5. Setup Python Virtual Environment and Install Dependencies ---
echo ">>> [5/7] Creating Python virtual environment..."
sudo -u ${APP_USER} python3 -m venv ${VENV_DIR}

echo ">>> Installing Python packages..."
sudo ${VENV_DIR}/bin/pip install --upgrade pip
sudo ${VENV_DIR}/bin/pip install -r "${PROJECT_DIR}/requirements.txt"

# --- 6. Create systemd Service File ---
echo ">>> [6/7] Creating systemd service file..."
sudo tee "/etc/systemd/system/${PROJECT_NAME}.service" > /dev/null <<EOF
[Unit]
Description=Gunicorn instance to serve ${PROJECT_NAME}
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${PROJECT_DIR}
# Point to the Gunicorn executable inside the virtual environment
ExecStart=${VENV_DIR}/bin/gunicorn -w ${GUNICORN_WORKERS} -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 main:app

Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# --- 7. Configure Nginx and Start Services ---
echo ">>> [7/7] Configuring Nginx and starting services..."
SERVER_IP=$(hostname -I | awk '{print $1}')
sudo tee "/etc/nginx/sites-available/${PROJECT_NAME}" > /dev/null <<EOF
server {
    listen 80;
    server_name ${SERVER_IP} _; # Replace _ with your domain if you have one

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security: deny access to hidden files like .git or a mistakenly uploaded .env
    location ~ /\. {
        deny all;
    }
}
EOF

# Enable the Nginx site and remove the default
if [ ! -L "/etc/nginx/sites-enabled/${PROJECT_NAME}" ]; then
    sudo ln -s "/etc/nginx/sites-available/${PROJECT_NAME}" "/etc/nginx/sites-enabled/"
fi
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Test Nginx configuration and restart
sudo nginx -t
sudo systemctl restart nginx

# Start and enable the application service
sudo systemctl daemon-reload
sudo systemctl start ${PROJECT_NAME}
sudo systemctl enable ${PROJECT_NAME}

echo "--- Setup Complete! ---"
echo ""
echo "Your FastAPI service has been deployed from '${SOURCE_DIR}' to '${PROJECT_DIR}' and is now running."
echo "You can access it at: http://${SERVER_IP}"
echo ""
echo "To check the status of your service, run: sudo systemctl status ${PROJECT_NAME}"
echo "To see the logs, run: sudo journalctl -u ${PROJECT_NAME} -f"
echo ""