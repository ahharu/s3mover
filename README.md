# S3 Mover

## Description
Move from s3 to another..

## Commands!
### Implement the following commands:

- make dev : Clean and stop all running containers and images, run docker-compose ( migrations + running python script for predictions ) 
- make clean : Stop and remove all the containers and images
- make dev (builds and run s3mover)
- make rundev ( runs s3mover , without build)
- make runminio (runs minio)
- make rundb (runs db)
- make stop ( stops all containers )
- make 

### Get it Started

You can start by doing

- make runminio

- make rundb

- make createbucket

- ./SRESeeder.sh

- make stop

then you can just `make dev`

### Extra ball

It would require INSERT and UPDATE permissions on the table

#### Permissions for S3

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": ["arn:aws:s3:::bucket-name"]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": "s3:*Object",
            "Resource": ["arn:aws:s3:::bucket-name/*"]
        }
    ]
}
``
