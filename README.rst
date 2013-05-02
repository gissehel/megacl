megacl
======

mega.co.nz command line client

Installation
============

Just use::

    $ pip install megacl

or::

    $ sudo pip install megacl

Usage
=====

::

    $ mcl help
    Usage: mcl COMMAND_NAME [OPTIONS] [VALUES]
    A command line tool for mega.co.nz
    
    Commands:
        find                 list files on mega
        get                  get one or more files
        geturl               get from a url
        help                 give help
        login                login to mega
        logout               logout from mega
        ls                   list files in a mega directory
        mkdir                create a new remote directory
        put                  put one or more files
        quota                get account's quota
        reload               reload the filesystem
        show                 list files on mega
    
    General parameters:
        --debug              Provide some debug informations
                             (--debug,-d)
        --help               Get help on specific command
                             (--help,-h)
        --login=VALUE        The login to use when mode --no-config
        --no-config          Don't read/write config files
                             (--no-config,-X)
        --password=VALUE     The password to use when mode --no-config 
                             (not safe, prefer the login command)

Login
-----

To use this tool, you first need to login::

    $ mcl login --email=dave@example.com
    Login : [dave@example.com]
    Password:
    login success

Once you're loggin, while your password is not stored anywhere, 
your masterkey and the current sid for the loggin session are stored 
in the configuration file ``~/.megaclient/config``. If this is 
a problem of any sort, please **do not use this tool**.

Show & Find
-----------

To show all the directory and files on the account, use the show or the find command::

    $ mcl show
    :ybRwIWgK 'Cloud Drive'
    :2ZJ1Tata   ''
    :RTgRCjhY   'Documents'
    :3DBFSa9S     'mydoc.txt'
    :iSpGZz4J   'Test'
    :QKxQzDlD     'Image test.png'
    :DDAgCv1a     'xkcd'
    :gKJlhatb       '184-matrix_transform.png'
    :0TwEKCpb       '353-python.png'
    :CLRGYv5Y       '303-compiling.png'
    :TKhFSKhJ       '163-donald_knuth.png'
    :RIQXhqtZ 'Inbox'
    :TK5UwKlS 'Rubbish Bin'
    
    $ mcl find
    :ybRwIWgK '/Cloud Drive'
    :2ZJ1Tata '/Cloud Drive/'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'

You can also use filters::

    $ mcl show -f ytho
    :0TwEKCpb       '353-python.png'
    
    $ mcl find -f ytho
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    
    $ mcl show -f es
    :iSpGZz4J   'Test'
    :QKxQzDlD     'Image test.png'
    
    $ mcl find -f es
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'


Get & Put
---------

The first part of each result line is the file handle. When you 
need to specify a file or a directory, you can either use the full 
path or its handle (including the ":")::

    $ mcl get :0TwEKCpb
    Getting [353-python.png] (90835 bytes)
    Transfert completed in 0.1 seconds (1107.85 KiB/s)
    
    $ mcl get '/Cloud Drive/Test/xkcd/353-python.png'
    Getting [353-python.png] (90835 bytes)
    Transfert completed in 0.1 seconds (1217.35 KiB/s)
    
``get`` is to download file, you can also upload using ``put``::

    $ mcl put ../docs/README.md :iSpGZz4J
    Sending [README.md] (548655 bytes)
    Transfert completed in 1.8 seconds (297.7 KiB/s)

Reload
------

To reload the file list, use ``reload``::
    
    $ mcl reload
    
    $ mcl find
    :ybRwIWgK '/Cloud Drive'
    :2ZJ1Tata '/Cloud Drive/'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'

Ls
--

Use can also use unix-like ls command::

    $ mcl ls '/Cloud Drive/Test'
    Image test.png
    README.md
    xkcd

The command ``ls`` support the ``--long``/``-l`` paramater (like ``ls -l``)::

    $ mcl ls --help
    Command: ls [OPTIONS] [VALUES]
    list files in a mega directory

    Command parameters:
        --long               use a long listing format
                             (--long,-l)

::

    $ mcl ls -l '/Cloud Drive/Test'
    --rw- :QKxQzDlD 3102405 2013-02-01 18:12:47 Image test.png
    --rw- :4sMDajOQ    1850 2013-04-28 12:02:21 README.md
    durwx :DDAgCv1a         2013-04-11 15:37:01 xkcd

Quota
-----

Use can watch your space usage using::

    $ mcl quota
    Current quota: [21.00/50.00]

This means you're using 21.00 GiB of your 50.00 GiB.

Stateless usage with no config file involved
--------------------------------------------

Login informations and directory cache are stored on the 
filesystem. You can also use this tool stateless with
the switch ``--no-config`` (or ``-X``). You must then
provide ``--login`` and ``--password`` commands on every
calls. Note that providing password on the command line
is considered a **bad practice**.

Commands look like::

    $ mcl find -f es --no-config --login=dave@example.com --password=r_N71kL4ee:cG28p-N,aam4
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'

    $ mcl ls -l '/Cloud Drive/Test' --no-config --login=dave@example.com --password=r_N71kL4ee:cG28p-N,aam4
    --rw- :QKxQzDlD 3102405 2013-02-01 18:12:47 Image test.png
    --rw- :4sMDajOQ    1850 2013-04-28 12:02:21 README.md
    durwx :DDAgCv1a         2013-04-11 15:37:01 xkcd



