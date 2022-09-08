.PHONY: clean system-packages python-packages install run all migrations rundb rundev

clean:
		find . -type f -name '*.pyc' -delete
		find . -type f -name '*pycache*' -delete
		find . -type f -name '*.log' -delete
		sudo rm -rf db/data/*
		docker ps -a -q  --filter ancestor=s3mover/s3mover --filter ancestor=s3mover/db --filter ancestor=s3mover/migrations | xargs docker stop || echo "No Dockers to stop"
		docker ps -a -q  --filter ancestor=s3mover/s3mover --filter ancestor=s3mover/db --filter ancestor=s3mover/migrations | xargs docker rm || echo "No Dockers to remove"
		docker images -q --filter "reference=s3mover/s3mover" --filter "reference=s3mover/db" --filter "reference=s3mover/migrations" | xargs docker rmi || echo "No Images to remove"
		docker-compose down

stop:
		docker-compose down

python-packages:
		workon=$CWD/.env3
		virtualenv -p /usr/bin/python3
		source $workon/bin/activate
		cd s3mover; \
		pip install -r requirements.txt; \
		cd -

install: python-packages

dev:
		docker-compose build
		docker-compose run --rm s3mover
		docker-compose down

rundev:
		docker-compose run --rm s3mover
		docker-compose down

rundb:
		docker-compose run -p 3306:3306 db

createbucket:
		docker-compose run createbuckets
		docker-compose down

runminio:
		docker-compose run -p 9000:9000 minio

migrate:
		docker-compose run --rm migration
		docker-compose down


migrations:
		docker-compose build
		docker-compose run --rm -v $(PWD)/alembic/versions:/app/alembic/versions --entrypoint "./wait-for.sh db\:3306 -t 120 -- dockerize -template ./alembic.ini.tmpl\:./alembic.ini alembic" migration revision --autogenerate -m "create initial tables"
		docker ps -a -q  --filter ancestor=s3mover/s3mover --filter ancestor=s3mover/db --filter ancestor=s3mover/migrations | xargs docker stop || echo "No Dockers to stop"
		docker ps -a -q  --filter ancestor=s3mover/s3mover --filter ancestor=s3mover/db --filter ancestor=s3mover/migrations | xargs docker rm || echo "No Dockers to remove"
		docker images -q --filter "reference=s3mover/s3mover" --filter "reference=s3mover/db" --filter "reference=s3mover/migrations" | xargs docker rmi || echo "No Images to remove"
		docker-compose down

all: clean migrate createbucket dev
