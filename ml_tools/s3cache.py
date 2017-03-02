import os.path
import boto.s3


def s3cache(bucket, key, cache_prefix='s3cache', check_update=False):
    cache = os.path.expanduser("~/.{prefix}".format(prefix=cache_prefix))

    path_parts = [cache, bucket] + key.split("/")
    item = "/".join(path_parts)
    parent = "/".join(path_parts[:-1])
    digest_file = item + ".digest"

    if not os.path.exists(parent):
        os.makedirs(parent)

    if os.path.exists(item):
        if check_update:
            digest = "none"
            if os.path.exists(digest_file):
                with open(digest_file) as f:
                    digest = f.read()

            conn = boto.connect_s3()

            bucket = conn.get_bucket(bucket)
            key = bucket.get_key(key)
            remote_digest = key.etag.strip('"')

            print("local digest: {}".format(digest))
            print("remote digest: {}".format(remote_digest))

            if remote_digest != digest:
                print("file %s is outdated, downloading...".format(item))
                key.get_contents_to_filename(item)
                with open(digest_file, 'w') as f:
                    f.write(remote_digest)
            else:
                print("file {} is up to date".format(item))
        else:
            print("file {} is already stored locally".format(item))
    else:
        print("file {} is missing, downloading...".format(item))

        conn = boto.connect_s3()

        bucket = conn.get_bucket(bucket)
        key = bucket.get_key(key)
        remote_digest = key.etag.strip('"')

        key.get_contents_to_filename(item)
        with open(digest_file, 'w') as f:
            f.write(remote_digest)

    return item