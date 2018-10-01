#!/bin/bash

echo "Starting all Guindex services"

cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexGunicorn.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexStats.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexAlerts.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexDbBackup.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexTelegramBot.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexMap.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable GuindexGunicorn.service
systemctl restart GuindexGunicorn.service

systemctl enable GuindexStats.service
systemctl restart GuindexStats.service

systemctl enable GuindexAlerts.service
systemctl restart GuindexAlerts.service

systemctl enable GuindexDbBackup.service
systemctl restart GuindexDbBackup.service

systemctl enable GuindexTelegramBot.service
systemctl restart GuindexTelegramBot.service

systemctl enable GuindexMap.service
systemctl restart GuindexMap.service

systemctl restart nginx
