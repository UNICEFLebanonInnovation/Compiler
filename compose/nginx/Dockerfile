FROM nginx:latest
<<<<<<< HEAD
ADD nginx.conf /etc/nginx/nginx.conf
=======
ADD nginx.conf /etc/nginx/nginx.conf


# installs the `ps` command in the nginx image
RUN apt-get update && apt-get install -y procps

ADD start.sh /start.sh
ADD nginx-secure.conf /etc/nginx/nginx-secure.conf
ADD dhparams.pem /etc/ssl/private/dhparams.pem
CMD /start.sh

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
