# The [web.py](http://webpy.org/) (really basic) [blog example](http://webpy.org/src/blog/0.3) 
# using **RethinkDB as the backend for web.py applications**.
#
# For details about the complete stack, installation, and running the app see
# the [README](https://github.com/rethinkdb/rethinkdb-example-webpy-blog).
import os, socket, sys, time

import web

from contextlib import contextmanager

from rethinkdb import r

#### Connection details

# We will use these settings later in the code to
# connect to the RethinkDB server.
RDB_CONFIG = {
  'host' : os.getenv('RDB_HOST', 'localhost'),
  'port' : os.getenv('RDB_PORT', 28015),
  'db'   : os.getenv('RDB_DB', 'webpy'),
  'table': os.getenv('RDB_TABLE', 'blogposts')
}


# We define a [context manager](http://docs.python.org/2/library/stdtypes.html#typecontextmanager)
# for the RethinkDB connection.
@contextmanager
def connection():
  conn = None
  try:
    # Connect to a specific RethinkDB database
    conn = r.connect(host=RDB_CONFIG['host'], port=RDB_CONFIG['port'], db_name=RDB_CONFIG['db'])
    yield conn
  except socket.error, err:
    msg = "Couldn't connect to RethinkDB on host:%s, port:%s" % (RDB_CONFIG['host'], RDB_CONFIG['port'])
    print >> sys.stderr, msg
    raise EnvironmentError(msg)
  finally:
    if conn:
      conn.close()

#### Listing existing posts

# To retrieve all existing tasks, we are using the
# [`r.table`](http://www.rethinkdb.com/api/#py:selecting_data-table)
# command to query the database in response to a GET request from the
# browser. We also [`order_by`](http://www.rethinkdb.com/api/#py:transformations-orderby)
# the `posted_at` attribute in a descending manner.
#    
# Running the query returns an iterator that automatically streams
# data from the server in efficient batches.
def get_posts():
  with connection() as conn:
    return r.table(RDB_CONFIG['table']).order_by(r.desc('posted_at')).run(conn)

#### Creating a new post

# We create a new blog entry using
# [`insert`](http://www.rethinkdb.com/api/#py:writing_data-insert).
#
# The `insert` operation returns a single object specifying the number
# of successfully created objects and their corresponding IDs:
# `{ "inserted": 1, "errors": 0, "generated_keys": ["b3426201-9992-4a21-ab84-974603657671"] }`
def new_post(title, text):
  new_post = {'title': title, 
    'content': text, 
    'posted_at': time.time(),
    'last_modified': time.time()
  }
  with connection() as conn:
    result = r.table(RDB_CONFIG['table']).insert(new_post).run(conn)
    if result['inserted'] == 1:
      new_post['id'] = result['generated_keys'][0]
      return new_post
    else:
      return None

#### Retrieving a single post

# Every new post gets assigned a unique ID. The browser can retrieve
# a specific task by GETing `/view/<post_id>`. To query the database
# for a single document by its ID, we use the
# [`get`](http://www.rethinkdb.com/api/#py:selecting_data-get)
# command.
def get_post(id):
  with connection() as conn:
    return r.table(RDB_CONFIG['table']).get(id).run(conn)

#### Updating a post

# To update the post we'll use the 
# [`update`](http://www.rethinkdb.com/api/#py:writing_data-update)
# command, which will merge the JSON object stored in the database with the
# new one.
#
# The `update` operation returns an object specifying how many rows
# have been updated.
def update_post(id, title, text):
  with connection() as conn:
    result = r.table(RDB_CONFIG['table']).get(id) \
      .update({'title': title, 'content': text, 'last_modified': time.time()}) \
      .run(conn)
    return result.get('modified', 0) == 1

#### Deleting a post

# To delete a post we'll call a
# [`delete`](http://www.rethinkdb.com/api/#py:writing_data-delete)
# command.
#
# The `delete` operation returns an object specifying how many
# rows have been deleted.
def del_post(id):
  with connection() as conn:
    result = r.table(RDB_CONFIG['table']).get(id).delete().run(conn)
    return result.get('deleted', 0) == 1


#### Database setup


# The app will use the table `blogposts` in the database `webpy`. 
# You can override these defaults by defining the `RDB_DB` and `RDB_TABLE`
# env variables.
# 
# We'll create the database and table here using
# [`db_create`](http://www.rethinkdb.com/api/#py:manipulating_databases-db_create)
# and
# [`table_create`](http://www.rethinkdb.com/api/#py:manipulating_tables-table_create) 
# commands.
def dbSetup():
    connection = r.connect(host=RDB_CONFIG['host'], port=RDB_CONFIG['port'])
    try:
        connection.run(r.db_create(RDB_CONFIG['db']))
        connection.run(r.db(RDB_CONFIG['db']).table_create(RDB_CONFIG['table']))
        print 'Database setup completed. Now run the app without --setup.'
    except Exception:
        print 'App database already exists. Run the app like this: `python blog.py`'
    finally:
        connection.close()


# ### Best practices ###
#
# #### Managing connections: a connection per request ####
#
# The RethinkDB server doesn't use a thread-per-connnection approach
# so opening connections per request will not slow down your database.
#
# #### Fetching multiple rows: batched iterators ####
#
# When fetching multiple rows from a table, RethinkDB returns a
# batched iterator initially containing a subset of the complete
# result. Once the end of the current batch is reached, a new batch is
# automatically retrieved from the server. From a coding point of view
# this is transparent:
#   
#     for result in r.table('blogposts').run(conn):
#         print result
#     
#    
# #### `update` vs `replace` ####
#
# Both [`update`](http://www.rethinkdb.com/api/#py:writing_data-update) and 
# [`replace`](http://www.rethinkdb.com/api/#py:writing_data-replace) 
# operations can be used to modify one or multiple rows. Their behavior is different:
#    
# *   `update` will merge existing rows with the new values
# *   `replace` will completely replace the existing rows with new values


#
# Licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
#
# Copyright (c) 2012 RethinkDB
#
