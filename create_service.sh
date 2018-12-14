#!/bin/bash

#run .py as a service

#create service file
cd /lib/systemd/system/
echo "[Unit]" > garaspii.service
echo "Description=eVill's Garbage" >> garaspii.service
echo "After=multi-user.target" >> garaspii.service
echo "[Service]" >> garaspii.service
echo "Type=simple" >> garaspii.service
echo "ExecStart=/usr/bin/python /home/pi/garaspii/garaspii.py" >> garaspii.service
echo "Restart=on-abort" >> garaspii.service
echo "[Install]" >> garaspii.service
echo "WantedBy=multi-user.target" >> garaspii.service

#rights to .service file
sudo chmod 644 garaspii.service

#rights to .py file
cd /home/pi/garaspii/
chmod +x garaspii.py

#start service and make it persistent
sudo systemctl daemon-reload
sudo systemctl enable garaspii.service
sudo systemctl start garaspii.service

#stop service, disable service
# sudo systemctl stop garaspii.service
# sudo systemctl disable garaspii.service

#check log
# sudo journalctl -f -u garaspii.service
