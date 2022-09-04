import boto3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from config import ConfigFactory
import argparse
from botocore.config import Config
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

args = parser.parse_args()

boilerplate_env = os.getenv("BOILERPLATE_ENV", "dev")
config = ConfigFactory().create_config(boilerplate_env)
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_size=60, max_overflow=20)

client = boto3.client('s3', region_name=args.region)
Session = sessionmaker(bind=engine)

results = []
pool = threading.BoundedSemaphore(10)




print("ALL DONE")
print("It took" + str(time.time() - start) + "seconds.")
