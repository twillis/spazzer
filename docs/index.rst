.. spazzer documentation master file, created by
   sphinx-quickstart on Mon Dec 14 08:47:24 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Spazzer
=======

Spazzer is a web application that can be used to share your music
collection via web browser. It provdes an interface for browsing
artists, albums and songs in your collection as well as search
functionality. Songs can either be downloaded individually or as a
per-album zip file.

Setup
-----

Spazzer is a `wsgi`_ application written in `python`_ so, it's setup
does not deviate much from what you would normally do to setup any
`wsgi`_ application.  

Prerequisites
~~~~~~~~~~~~~

Python
------

Before you begin, `python`_ needs to be installed and accessible by
your account. To check to see if `python`_ is installed, open up a
terminal or DOS prompt and type ::

  $ python -V

what should be output is the version of `python`_ you have installed,
if not, you need to install `python`_ for your operating system. The
supported version as of this writing is version 2.6.4. 

Distribute
----------

Distribute is an application that installs applications in your
`python`_ installation. As of this writing it must be installed
separately. To see if you have distribute installed, type ::

  $ easy_install --help

which should output the easy_install help message. If it doesn't you
need to install distribute which can be done by downloading
`distribute_setup.py`_ and running it on the commandline like so. ::

  $ python distribute_setup.py

When this command runs successfully, the easy_install command should be available.  


Installing Spazzer
~~~~~~~~~~~~~~~~~~

Once `python`_ and `distribute`_ are installed successfully, you
should be able to setup spazzer. From the commandline you must first
"cd" to to the path where you unzipped spazzer. ::

  $ cd /path/to/spazzer
  /path/to/spazzer$

Next you need to run ::

  /path/to/spazzer$ python setup.py install

This command will download all the packages and libraries that spazzer
requires to run into your `python`_ installation. Note: if you are
installing this into your system `python`_ installation you will need to
run this command as a user that has permissions to write files into
the python distribution such as an Administrator.

Creating an Instance
~~~~~~~~~~~~~~~~~~~~

Once spazzer has been successfully installed, you are ready to create
an instance to run. The reason you create an instance to run is so
that you can have multiple instances for different reasons or in the
case of a machine used by many users, each user can have their own
configuration. 

In other words, your view of your music collection does not have to
include your 10 year old daughters Hannah Montana collection that she
begged to buy you from amazon a while back.

When spazzer was installed a new command should have been put in your
path called "spazzer-create" running this command will walk you
through creating an instance that you can run. ::

  $ spazzer-create col

Where "col" is the name you want to give to the directory that will
store all your files necessary to run spazzer. You will be prompted to
enter a port number, or you can accept the default (8088). When the
command completes you will have a directory called whatever you named
it.


Running Spazzer
---------------

Once you have created an instance you are ready to run your new
spazzer site. Inside the directory where your spazzer instance was
created there are some commands

run.sh/run.bat
~~~~~~~~~~~~~~

To run your spazzer instance you will need to run either "run.bat" on
windows, or "run.sh" on presumably everything else. These commands are
inside your spazzer instance directory

On Linux::

  $ sh col/run.sh

On Windows::

  c:\> col\run.bat

At this point you should have it running, you can then access it via 
a web browser at the following url. If you accepted the default port
setting ::

 http://localhost:8088/

Setting up your collection
--------------------------

Once spazzer is running, you need to tell it where to look for files
that you want to make accessible. The page to do that on is at ::

  http://localhost:8088/admin

This is where you tell spazzer what directories it should search for
files in. You can add any number of directories however you need at
least read permission on the files in those directories in order for
spazzer to be able to build an index of your music files.

At anytime, you may want to re-build or update your collection index,
like perhaps when you have new files. To do this simply click the
update icon on the admin page, depending on how many files you are
sharing, it may take a long time. New files will appear in the index
when they have been processed. Clicking update will also remove files
from your index if they no longer exist in your collection, are no
longer accessible, or are no longer contained in directories you have
told spazzer to index.

scan.bat/scan.sh
----------------

If ever you want to rescan your collection you can do it from the
admin web page, or you can simply run the scan.bat command on windows
or scan.sh on everything that's not windows.

If you have a large collection being indexed it can take a while the
first time through. 

.. _`python`: http://python.org/download/
.. _`wsgi`: http://wsgi.org
.. _`distribute_setup.py`: http://pypi.python.org/pypi/distribute#distribute-setup-py
.. _`distribute`: http://pypi.python.org/pypi/distribute
