megacl
======

mega.co.nz command line client

Installation
============

Just use::

    $ pip install megacl

or::

    $ sudo pip install megacl

pip will take care of dependency. Note that among all dependencies, megacl needs ``pycrypto``, which is not a pure python module and doesn't provide binaries through pypi for legal matters.

Some people may find usefull to install pycrypto separatly especially if you don't have a C-compiling environnement installed.

- You may find ``pycrypto`` for *Windows* on http://www.voidspace.org.uk/python/modules.shtml 
- You may find ``pycrypto`` for *Ubuntu* under the name ``python-crypto``

Usage
=====

::

    $ mcl help
    Usage: mcl [GLOBAL OPTIONS] COMMAND_NAME [OPTIONS] [VALUES]
    A command line tool for mega.co.nz
    
    Commands:
        find                 list files on mega                      
        get                  get one or more files                   
        geturl               get from a url                          
        help                 give help                               
        info                 get informations on a file or folder    
        login                login to mega                           
        logout               logout from mega                        
        ls                   list files in a mega directory          
        mkdir                create a new remote directory           
        mv                   move an item into another directory     
                             (move,mv)
        put                  put one or more files                   
        quota                get account's quota                     
        reload               reload the filesystem                   
        rename               rename an item                          
        show                 list files on mega                      
    
    Global options:
        --debug              Provide some debug informations         
                             (--debug,-d)
        --help               Get help on specific command            
                             (--help,-h)
        --login=VALUE        The login to use when mode --no-config  
        --no-config          Don't read/write config files           
                             (--no-config,-X)
        --password=VALUE     The password to use when mode --no-config (not safe, prefer the login command)
        --profile=VALUE      Use a different profile than the default
                             (--profile,-P)
        --reload             Force reload before the first action that need the filesystem
                             (--reload,-r)

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
    :RTgRCjhY   'Documents'
    :3DBFSa9S     'mydoc.txt'
    :iSpGZz4J   'Test'
    :QKxQzDlD     'Image test.png'
    :DDAgCv1a     'xkcd'
    :TKhFSKhJ       '163-donald_knuth.png'
    :gKJlhatb       '184-matrix_transform.png'
    :CLRGYv5Y       '303-compiling.png'
    :0TwEKCpb       '353-python.png'
    :RIQXhqtZ 'Inbox'
    :TK5UwKlS 'Rubbish Bin'
    
    $ mcl find
    :ybRwIWgK '/Cloud Drive'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
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
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'

Both commands support the ``--long``/``-l`` paramater (which reminds the ``ls -l`` presentation)::

    $ mcl find -l -f es
    durwx :iSpGZz4J         2013-02-01 15:45:01 '/Cloud Drive/Test'
    --rw- :QKxQzDlD 3102405 2013-02-01 18:12:47 '/Cloud Drive/Test/Image test.png'
    durwx :DDAgCv1a         2013-04-11 15:37:01 '/Cloud Drive/Test/xkcd'
    --rw- :TKhFSKhJ   32884 2006-09-27 09:51:44 '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    --rw- :gKJlhatb    6903 2006-11-15 07:14:22 '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    --rw- :CLRGYv5Y   28315 2007-08-15 12:10:02 '/Cloud Drive/Test/xkcd/303-compiling.png'
    --rw- :0TwEKCpb   90835 2007-12-05 09:32:48 '/Cloud Drive/Test/xkcd/353-python.png'

Both commands support the ``--short``/``-s`` paramater that provide an output more suited for scripts/pipes::

    $ mcl find -s -f es
    /Cloud Drive/Test
    /Cloud Drive/Test/Image test.png
    /Cloud Drive/Test/xkcd
    /Cloud Drive/Test/xkcd/163-donald_knuth.png
    /Cloud Drive/Test/xkcd/184-matrix_transform.png
    /Cloud Drive/Test/xkcd/303-compiling.png
    /Cloud Drive/Test/xkcd/353-python.png

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
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'

Ls
--

You can also use unix-like ``ls`` command::

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

Mkdir
-----

You can create a new folder using ``mkdir`` command::

    $ mcl find
    :ybRwIWgK '/Cloud Drive'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'
    
    $ mcl mkdir Subdir '/Cloud Drive/Test'
    
    $ mcl find --reload
    :ybRwIWgK '/Cloud Drive'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :bU7dxMP4 '/Cloud Drive/Test/Subdir'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'

Note the presence of the ``:bU7dxMP4 '/Cloud Drive/Test/Subdir'`` line.

You could specify either the parent dir full path or it's handle::

    $ mcl mkdir Subdir :iSpGZz4J

Move
----

You can move a file or a folder into another folder using the ``move``/``mv`` command::

    $ mcl find
    :ybRwIWgK '/Cloud Drive'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'
    
    $ mcl move '/Cloud Drive/Test/Image test.png' '/Cloud Drive/Documents'
    
    $ mcl find --reload
    :ybRwIWgK '/Cloud Drive'
    :RTgRCjhY '/Cloud Drive/Documents'
    :QKxQzDlD '/Cloud Drive/Documents/Image test.png'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :bU7dxMP4 '/Cloud Drive/Test/Subdir'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'

    $ # To move back the file using the handles
    $ mcl move :QKxQzDlD :iSpGZz4J

You can also move several files or folders using this command::

    $ mcl find
    :ybRwIWgK '/Cloud Drive'
    :RTgRCjhY '/Cloud Drive/Documents'
    :3DBFSa9S '/Cloud Drive/Documents/mydoc.txt'
    :iSpGZz4J '/Cloud Drive/Test'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :gKJlhatb '/Cloud Drive/Test/xkcd/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/xkcd/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/xkcd/353-python.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'
    
    $ mcl move :gKJlhatb :0TwEKCpb :CLRGYv5Y :RTgRCjhY '/Cloud Drive/Test'
    
    $ mcl find --reload
    :ybRwIWgK '/Cloud Drive'
    :iSpGZz4J '/Cloud Drive/Test'
    :gKJlhatb '/Cloud Drive/Test/184-matrix_transform.png'
    :CLRGYv5Y '/Cloud Drive/Test/303-compiling.png'
    :0TwEKCpb '/Cloud Drive/Test/353-python.png'
    :RTgRCjhY '/Cloud Drive/Test/Documents'
    :3DBFSa9S '/Cloud Drive/Test/Documents/mydoc.txt'
    :QKxQzDlD '/Cloud Drive/Test/Image test.png'
    :4sMDajOQ '/Cloud Drive/Test/README.md'
    :bU7dxMP4 '/Cloud Drive/Test/Subdir'
    :DDAgCv1a '/Cloud Drive/Test/xkcd'
    :TKhFSKhJ '/Cloud Drive/Test/xkcd/163-donald_knuth.png'
    :RIQXhqtZ '/Inbox'
    :TK5UwKlS '/Rubbish Bin'

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

Profiles
--------

Some commands are stored in configuration files / cache files in the default 
configuration directory.

If for some reason you need to use a different profile without logging out
of the first profile, you can use the global parameter ``--profile`` (``-P``).

Let's suppose your logged in as usual as ``dave@example.com`` and your with 
Jonathan who want to download a file from his how account (``jonathan@example.com``) to show you. You
can then simply use profiles::

    $ # you are logged
    $ mcl ls '/Cloud Drive'
    Documents
    Test
    
    $ # jonathan will login
    $ mcl -P jonathan login --email=jonathan@example.com
    Login : [jonathan@example.com]
    Password:
    login success
    
    $ mcl -P jonathan ls '/Cloud Drive'
    Sintel.2010.1080p.mkv
    sintel_en.srt
    sintel_es.srt
    sintel_fr.srt
    sintel_de.srt
    sintel_nl.srt
    sintel_it.srt
    sintel_pt.srt
    sintel_pl.srt
    sintel_ru.srt
    sintel_trailer-1080p.mp4
    
    $ # Note you're still logged in as dave on default profile
    $ mcl ls --reload '/Cloud Drive'
    Documents
    Test
    
    $ mcl -P jonathan get '/Cloud Drive/Sintel.2010.1080p.mkv' '/Cloud Drive/sintel_it.srt'
    Getting [Sintel.2010.1080p.mkv] (1180090590 bytes)
    Transfert completed in 57.0 seconds (20218.1 KiB/s)
    Getting [sintel_it.srt] (1544 bytes)
    Transfert completed in 0.8 seconds (1.88 KiB/s)
    
    $ mcl -P jonathan logout
    
    $ mcl -P jonathan ls '/Cloud Drive'
    Error : You must login first
    
    $ mcl ls --reload '/Cloud Drive'
    Documents
    Test

Detailled help
--------------

On each command, you can get detailled help using ``--help``::
    
    $ mcl find --help
    Command: [GLOBAL OPTIONS] find [OPTIONS] [VALUES]
    list files on mega
    
    Command options:
        --filter=VALUE       filter the result using VALUE           
                             (--filter,-f)
        --long               use a long listing format               
                             (--long,-l)
        --short              use short listing format (only the path)
                             (--short,-s)
    
    Global options:
        --debug              Provide some debug informations         
                             (--debug,-d)
        --help               Get help on specific command            
                             (--help,-h)
        --login=VALUE        The login to use when mode --no-config  
        --no-config          Don't read/write config files           
                             (--no-config,-X)
        --password=VALUE     The password to use when mode --no-config (not safe, prefer the login command)
        --profile=VALUE      Use a different profile than the default
                             (--profile,-P)
        --reload             Force reload before the first action that need the filesystem
                             (--reload,-r)

When you use this on option on command ``help`` you detail for all commands::

    $ mcl help --help
    Usage: mcl [GLOBAL OPTIONS] COMMAND_NAME [OPTIONS] [VALUES]
    A command line tool for mega.co.nz
    
    Commands:
        find                 list files on mega                      
        get                  get one or more files                   
        geturl               get from a url                          
        help                 give help                               
        info                 get informations on a file or folder    
        login                login to mega                           
        logout               logout from mega                        
        ls                   list files in a mega directory          
        mkdir                create a new remote directory           
        mv                   move an item into another directory     
                             (move,mv)
        put                  put one or more files                   
        quota                get account's quota                     
        reload               reload the filesystem                   
        rename               rename an item                          
        show                 list files on mega                      
    
    Global options:
        --debug              Provide some debug informations         
                             (--debug,-d)
        --help               Get help on specific command            
                             (--help,-h)
        --login=VALUE        The login to use when mode --no-config  
        --no-config          Don't read/write config files           
                             (--no-config,-X)
        --password=VALUE     The password to use when mode --no-config (not safe, prefer the login command)
        --profile=VALUE      Use a different profile than the default
                             (--profile,-P)
        --reload             Force reload before the first action that need the filesystem
                             (--reload,-r)
    
    find options:
        --filter=VALUE       filter the result using VALUE           
                             (--filter,-f)
        --long               use a long listing format               
                             (--long,-l)
        --short              use short listing format (only the path)
                             (--short,-s)
    
    info options:
        --attributes         show only attributes                    
                             (--attr,--attributes,-a)
        --handle             show only handle                        
                             (--handle,-H)
        --name               show only name                          
                             (--name,-n)
        --path               show only path                          
                             (--path,-p)
        --size               show only size                          
                             (--size,-s)
        --time               show only time                          
                             (--time,-t)
    
    login options:
        --email=VALUE        The login/email                         
                             (--email,-e)
    
    ls options:
        --long               use a long listing format               
                             (--long,-l)
    
    show options:
        --filter=VALUE       filter the result using VALUE           
                             (--filter,-f)
        --long               use a long listing format               
                             (--long,-l)
        --short              use short listing format (only the indent and the name)
                             (--short,-s)

