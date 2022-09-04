# A MySQL container.
FROM mysql:8
LABEL maintainer="Ahharu"

RUN usermod -u 1000 mysql

RUN chmod -R 777 /var/lib/mysql
RUN chown -R mysql:mysql /var/lib/mysql

RUN mkdir -p /var/run/mysqld
RUN chmod -R 777 /var/run/mysqld
RUN chown -R mysql:mysql /var/run/mysqld

EXPOSE 3306
CMD ["mysqld"]
