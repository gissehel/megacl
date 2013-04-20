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
        mkdir                create a new remote directory
        put                  put one or more files
        reload               reload the filesystem
        show                 list files on mega
    
    General parameters:
        --debug              Provide some debug informations
                             (--debug,-d)
        --help               Get help on specific command
                             (--help,-h)

To use this tool, you first need to login::

    $ mcl login --email=dave@example.com
    Login : [dave@example.com]
    Password:
    login success

Once you're loggin, while your password is not stored anywhere, 
your masterkey and the current sid for the loggin session are stored 
in the configuration file ``~/.megaclient/config``. If this is 
a problem of any sort, please **do not use this tool**.

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

