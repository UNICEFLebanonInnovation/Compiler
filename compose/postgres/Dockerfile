<<<<<<< HEAD
FROM postgres:9.5
=======
FROM postgres:9.6
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

# add backup scripts
ADD backup.sh /usr/local/bin/backup
ADD restore.sh /usr/local/bin/restore
ADD list-backups.sh /usr/local/bin/list-backups

# make them executable
RUN chmod +x /usr/local/bin/restore
RUN chmod +x /usr/local/bin/list-backups
RUN chmod +x /usr/local/bin/backup
