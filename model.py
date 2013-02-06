import os, socket, sys, time
import web
import logging

RDB_CONFIG = {
  'host' : os.getenv('RDB_HOST', 'localhost'),
  'port' : os.getenv('RDB_PORT', 28015),
  'db'   : os.getenv('RDB_DB', 'webpy'),
  'table': os.getenv('RDB_TABLE', 'blogposts')
}

# db = web.database(dbn='mysql', db='blog', user='justin')
class Db(object):
  def select(self, tbl_name, **args):
    logging.debug('select: %s (%s)', tbl_name, args)
    with connection() as conn:
      conn.run(r.table(RDB_CONFIG['table']))
    return [Post()]

  def insert(self, tbl_name, **args):
    logging.debug('insert: %s (%s)', tbl_name, args)

  def delete(self, tbl_name, **args):
    logging.debug('delete: %s (%s)', tbl_name, args)    

  def update(self, tbl_name, **args):
    logging.debug('update: %s (%s)', tbl_name, args)    

class Post(object):
  def __init__(self):
    self.id = 1
    self.title = 'Title'
    self.content = 'Content'
    self.posted_on = datetime.datetime.utcnow()

from rethinkdb import r
from rethinkdb.net import ExecutionError
from contextlib import contextmanager

@contextmanager
def connection():
  conn = None
  try:
    print 'connection:1'
    conn = r.connect(host=RDB_CONFIG['host'], port=RDB_CONFIG['port'])
    print 'connection:2'
    conn.use(RDB_CONFIG['db'])
    print 'connection:3'
    yield conn
    print 'connection:4'
  except socket.error, err:
    print 'connection:5'
    msg = "Couldn't connect to RethinkDB on host:%s, port:%s" % (RDB_CONFIG['host'], RDB_CONFIG['port'])
    logging.error(msg)
    raise EnvironmentError(msg)
  except ExecutionError, err:
    print 'connection:6'
    logging.exception("connection:6")
  except Exception, ex:
    print 'connection:7'
    logging.exception('connection:7')
  finally:
    if conn:
      conn.close


db = Db()

def get_posts():
  with connection() as conn:
    return conn.run(r.table(RDB_CONFIG['table']).order_by(r.desc('posted_at')))

def get_post(id):
  with connection() as conn:
    return conn.run(r.table(RDB_CONFIG['table']).get(id))

def new_post(title, text):
  new_post = {'title': title, 
    'content': text, 
    'posted_at': time.time(),
    'last_modified': time.time()
  }
  with connection() as conn:
    result = conn.run(r.table(RDB_CONFIG['table']).insert(new_post))
    print "insert:", result
    if result['inserted'] == 1:
      new_post['id'] = result['generated_keys'][0]
      return new_post
    else:
      return None

def del_post(id):
  with connection() as conn:
    result = conn.run(r.table(RDB_CONFIG['table']).get(id).delete())
    print "DELETE:", result
    return result.get('deleted', 0) == 1

def update_post(id, title, text):
  with connection() as conn:
    result = conn.run(r.table(RDB_CONFIG['table']).get(id).update({'title': title, 'content': text, 'last_modified': time.time()}))
    print "UPDATE:", result
    return result.get('modified', 0) == 1
