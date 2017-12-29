#!/bin/bash

echo "Starting all Guindex services"

ln -fs /var/www/Guindex/GuindexProject/Guindex/service_scripts/backup_guindex_db.sh /usr/bin/backup_guindex_db.sh

cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/Guindex.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexStats.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexAlerts.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexDbBackup.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexUserContributions.service /etc/systemd/system/
cp /var/www/Guindex/GuindexProject/Guindex/service_scripts/GuindexTelegramBot.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable Guindex.service
systemctl restart Guindex.service

systemctl enable GuindexStats.service
systemctl restart GuindexStats.service

systemctl enable GuindexAlerts.service
systemctl restart GuindexAlerts.service

systemctl enable GuindexDbBackup.service
systemctl restart GuindexDbBackup.service

systemctl enable GuindexUserContributions.service
systemctl restart GuindexUserContributions.service

systemctl enable GuindexTelegramBot.service
systemctl restart GuindexTelegramBot.service

systemctl restart nginx
