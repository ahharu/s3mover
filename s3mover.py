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
from datetime import datetime
from threading import BoundedSemaphore
from threading import Thread
from models import Avatar
import sys


class CopyObject(Thread):
  def __init__(self, avatar_id, aws_key, aws_secret, src_bucket, dst_bucket, pool, oldprefix, newprefix):
    Thread.__init__(self)
    self.avatar_id = avatar_id
    self.aws_key = aws_key
    self.aws_secret = aws_secret
    self.src_bucket = src_bucket
    self.dst_bucket = dst_bucket
    self.oldprefix = oldprefix
    self.newprefix = newprefix
    self.pool = pool

    self.status = False

  def prefix_exists(self, client,  bucket, prefix):
    res = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    return 'Contents' in res

  def remove_prefix(self, text, prefix):
    if text.startswith(prefix):
      return text[len(prefix):]
    return text  # or whatever

  def run(self):
    boilerplate_env = os.getenv("BOILERPLATE_ENV", "dev")
    config = ConfigFactory().create_config(boilerplate_env)
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_size=60, max_overflow=20)
    Session = sessionmaker(bind=engine)
    cursession = Session()
    client = boto3.client('s3', region_name=args.region, endpoint_url=args.s3endpoint,
                          aws_access_key_id=args.awsaccesskey,
                          aws_secret_access_key=args.awssecretkey, config=Config(signature_version='s3v4'))

    pool = self.pool

    avatar = cursession.query(Avatar).get(self.avatar_id)

    prefix = "{}/".format(self.oldprefix)

    filename = self.remove_prefix(avatar.path, prefix )

    # Only copy if not exists on dest bucket
    if not self.prefix_exists(client, self.dst_bucket,  "{}/{}".format(self.newprefix , filename)):
      pool.acquire()
      self.status = "{} : Sempahore Acquired, Copy Next".format(datetime.now())
      try:

        client.copy_object(CopySource="{}/{}{}".format(self.src_bucket,prefix,filename), Bucket=self.dst_bucket, Key="{}/{}".format(self.newprefix,filename))
        avatar.path = "{}/filename".format(self.newprefix)
        cursession.commit()

        self.status = "{} : Copy Success : {}".format(datetime.now(), filename)
      except:
        self.status = "{} : Copy Error : {}".format(datetime.now(), sys.exc_info())
      finally:
        pool.release()
        cursession.close()
    else:
      self.status = "{} : Key Already Exists, will not overwrite.".format(datetime.now())


###################3

def copy_s3_bucket(src_bucket, dst_bucket, aws_access_key_id, aws_secret_access_key, prefix=None, threads=10,
                  sessionmaker=None, oldprefix=None, newprefix=None, chunksize=5, region='us-east-1', s3endpoint=None):
  """
  Example usage: copy_s3_bucket(SOURCE_BUCKET='my-source-bucket', DEST_BUCKET='my-destination-bucket', prefix='parent/child/dir/', threads=20)
  """


  key_copy_thread_list = []
  pool_sema = BoundedSemaphore(threads)

  cursession = sessionmaker()

  for avatar in cursession.query(Avatar).filter(Avatar.path.startswith(args.oldprefix)).yield_per(chunksize):
    print(avatar.path)
    print("{} : Requesting copy thread for key {}".format(datetime.now(), avatar.id))
    current = CopyObject(avatar.id, aws_access_key_id, aws_secret_access_key, src_bucket, dst_bucket, pool_sema, oldprefix,
                      newprefix)
    key_copy_thread_list.append(current)
    current.start()

    # Pause when max threads reached
    if len(threading.enumerate()) >= threads:
      print("{} : Max Threads ({}) Reached: Pausing until threadcount reduces.".format(datetime.now(), threads))
      for key_copy_thread in key_copy_thread_list:
        key_copy_thread.join(
          30)
        if key_copy_thread.isAlive():
          print("{} : TIMEOUT on key {}".format(datetime.now(), key_copy_thread.avatar))
          continue
        print("{} : Status Output: {}".format(datetime.now(), key_copy_thread.status))
      key_copy_thread_list = []
      while 1:
        if len(threading.enumerate()) < threads:
          print("{} : Continuing thread creation.".format(datetime.now()))
          break
        time.sleep(1)


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
parser.add_argument('--s3endpoint', metavar='P', type=str,
                    help='s3endpoint', default=(os.getenv('S3_ENDPOINT_URL', None)))
parser.add_argument('--awsaccesskey', metavar='K', type=str,
                    help='s3endpoint', default=(os.getenv('AWS_ACCESS_KEY_ID', None)))
parser.add_argument('--awssecretkey', metavar='X', type=str,
                    help='s3endpoint', default=(os.getenv('AWS_SECRET_ACCESS_KEY', None)))
parser.add_argument('--oldprefix', metavar='F', type=str,
                    help='prefix', default=(os.getenv('OLDPREFIX', None)))
parser.add_argument('--newprefix', metavar='N', type=str,
                    help='prefix', default=(os.getenv('NEWPREFIX', None)))

parser.add_argument('--threads', metavar='T', type=int,
                    help='threads', default=(os.getenv('THREADS', 10)))

parser.add_argument('--chunksize', metavar='T', type=int,
                    help='chunksize', default=(os.getenv('CHUNKSIZE', 5)))

args = parser.parse_args()

print(args.awsaccesskey)
print(args.awssecretkey)
print(args.s3endpoint)
print(args.region)

client = boto3.client('s3', region_name=args.region, endpoint_url=args.s3endpoint, aws_access_key_id=args.awsaccesskey,
                      aws_secret_access_key=args.awssecretkey, config=Config(signature_version='s3v4'))

response = client.list_buckets()

# Output the bucket names
print('Existing buckets:')
for bucket in response['Buckets']:
  print(f'  {bucket["Name"]}')

## check if the buckets exists


try:
  client.head_bucket(Bucket=args.srcbucket)
  client.head_bucket(Bucket=args.dstbucket)

except ClientError:
  # The bucket does not exist or you have no access.
  print("The buckets don't exist")
  exit(999)

boilerplate_env = os.getenv("BOILERPLATE_ENV", "dev")
config = ConfigFactory().create_config(boilerplate_env)
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_size=60, max_overflow=20)

Session = sessionmaker(bind=engine)

cursession = Session()

copy_s3_bucket(src_bucket=args.srcbucket, dst_bucket=args.dstbucket, threads=args.threads,
               aws_access_key_id=args.awsaccesskey, aws_secret_access_key=args.awssecretkey, sessionmaker=Session,
               oldprefix=args.oldprefix, newprefix=args.newprefix, chunksize=args.chunksize)

print("ALL DONE")
print("It took" + str(time.time() - start) + "seconds.")
