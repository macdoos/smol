import os
from rocksdb_python import Options, PyDB, ReadOptions, WriteOptions
import json
import socket
import hashlib
import random

options = Options()
options.IncreaseParallelism()

print('sup', os.environ['TYPE'])

if os.environ['TYPE'] == 'master':
  volumes = os.environ['VOLUMES'].split(',')

  for v in volumes:
    print(v)

  db = PyDB(options, "./olivedb")

def master(env, start_response):
    key = env['REQUEST_URI']
    try:
        metakey = db.Get(ReadOptions(), key.encode('utf-8'))
    except RuntimeError as e:
        if 'NotFound' in str(e):
            metakey = None
        else:
            raise
            
    if metakey is None:
        if env['REQUEST_METHOD'] == 'PUT':
            # TODO: make it smarter
            volume = random.choice(volumes)

            # save volume to database
            meta = {"volume": volume}
            db.Put(WriteOptions(), key.encode('utf-8'), json.dumps(meta).encode('utf-8'))
        else:
            start_response('404 Not Found', [('Content-type', 'text/plain')])
            return [b'key not found']
    else:
        meta = json.loads(metakey.decode('utf-8'))

    # send redirect
    print(meta)
    volume = meta['volume']
    headers = [('Location', 'http://%s%s' % (volume, key))]
    start_response('307 Temporary Redirect', headers)
    return [b""]

# *** Volume Server ***

class FileCache(object):
  def __init__(self, basedir):
    self.basedir = os.path.realpath(basedir)
    os.makedirs(self.basedir, exist_ok=True)
    print("FileCache in %s" % basedir)

  def k2p(self, key, mkdir_ok=False):
    # must be MD5 hash
    assert len(key) == 32

    # 2 layers deep in nginx world
    path = self.basedir+"/"+key[0:2]+"/"+key[0:4]
    if not os.path.isdir(path) and mkdir_ok:
      # exist ok is fine, could be a race
      os.makedirs(path, exist_ok=True)

    return os.path.join(path, key)

  def exists(self, key):
    return os.path.isfile(self.k2p(key))

  def delete(self, key):
    os.unlink(self.k2p(key))

  def get(self, key):
    return open(self.k2p(key), "rb").read()

  def put(self, key, value):
    with open(self.k2p(key, True), "wb") as f:
      f.write(value)

if os.environ['TYPE'] == "volume":
  host = socket.gethostname()

  # create the filecache
  fc = FileCache(os.environ['VOLUME'])

def volume(env, start_response):
  key = env['REQUEST_URI'].encode('utf-8')
  hkey = hashlib.md5(key).hexdigest()
  print(hkey)

  if env['REQUEST_METHOD'] == 'GET':
    if not fc.exists(hkey):
      # key not in the FileCache
      start_response('404 Not Found', [('Content-type', 'text/plain')])
      return [b'key not found']
    start_response('200 OK', [('Content-type', 'text/plain')])
    return [fc.get(hkey)]

  if env['REQUEST_METHOD'] == 'PUT':
    flen = int(env.get('CONTENT_LENGTH', '0'))
    if flen > 0:
      fc.put(hkey, env['wsgi.input'].read(flen))
      start_response('200 OK', [('Content-type', 'text/plain')])
      return [b'']
    else:
      start_response('411 Length Required', [('Content-type', 'text/plain')])
      return [b'']

  if env['REQUEST_METHOD'] == 'DELETE':
    fc.delete(hkey)
