import boto3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from config import ConfigFactory
import argparse
from botocore.config import Config
from botocore.client import ClientError
import threading
import time

start = time.time()

ec2_config = Config(
    retries=dict(
        max_attempts=100
    ),
    signature_version='s3v4'
)

parser = argparse.ArgumentParser(description='Get Spot Pricing')
parser.add_argument('--region', metavar='R', type=str,
                    help='regions', default=(os.getenv('AWS_REGION', None)))
parser.add_argument('--srcbucket', metavar='S', type=str,
                    help='srcbucket', default=(os.getenv('SOURCE_BUCKET', None)))
parser.add_argument('--dstbucket', metavar='D', type=str,
                    help='dstbucket', default=(os.getenv('DEST_BUCKET', None)))
parser.add_argument('--s3endpoint', metavar='E', type=str,
                    help='s3endpoint', default=(os.getenv('S3_ENDPOINT', None)))

args = parser.parse_args()

client = boto3.client('s3', region_name=args.region, endpoint_url=args.s3endpoint)

## check if the buckets exists


try:
    s3.meta.client.head_bucket(Bucket=args.srcbucket)
    s3.meta.client.head_bucket(Bucket=args.dstbucket)

except ClientError:
    # The bucket does not exist or you have no access.
    print("The buckets don't exist")
    exit(999)

boilerplate_env = os.getenv("BOILERPLATE_ENV", "dev")
config = ConfigFactory().create_config(boilerplate_env)
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_size=60, max_overflow=20)

client = boto3.client('s3', region_name=args.region)
Session = sessionmaker(bind=engine)



results = []
pool = threading.BoundedSemaphore(10)




print("ALL DONE")
print("It took" + str(time.time() - start) + "seconds.")
