# What is it #

The [web.py](http://webpy.org/) (really basic) [blog example](http://webpy.org/src/blog/0.3) 
using RethinkDB as the backend database.

This example application shows how to perform simple CRUD operations with RethinkDB:

*   create a new post
*   list blog posts (ordered by timestamp)
*   edit a post
*   delete a post

# Complete stack #

*   [web.py](http://webpy.org/)
*   [RethinkDB](http://www.rethinkdb.com)

# Installation #

```
git clone git://github.com/rethinkdb/rethinkdb-example-webpy-blog.git
pip install web.py
pip install rethinkdb
```

_Note_: If you don't have RethinkDB installed, you can follow [these instructions to get it up and running](http://www.rethinkdb.com/docs/install/).

# Running the application #

We'll firstly create the database `webpy` and the table `blogposts` by running the setup:

```
python blog.py --setup
```

_Note_: You can override the default names of the database and table by setting the following
environment variables: `RDB_DB` and `RDB_TABLE` respectively.

Now you can run the application:

```
python blog.py
```

Then open a browser: <http://localhost:5000>.

# License #

This demo application is licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
