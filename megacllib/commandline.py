#!/usr/bin/env python

from mega import Mega
import sys
import os
import re
import time
#import yaml
# import pyaml
import shutil
import getpass
import posixpath

from supertools import superable
from cltools import _
from cltools import ConfigurableCLRunnable
from cltools import CLRunner

re_url = re.compile(r'https://mega.co.nz/#!.{52}',re.M+re.I)

@CLRunner.runnable(
    runnable=ConfigurableCLRunnable,
    runnable_kwargs={
        'config_dirname' : '~/.megaclient',
        'config_filename' : 'config',
        },
    )
@superable
class MegaCommandLineClient(object) :
    """A command line tool for mega.co.nz"""
    def __init__(self) :
        self._init_account_config()

        self._use_config = True

        self._login = None
        self._password = None
        self._force_reload = False
        self._profile = None

    def _init_account_config(self) :
        self._sid = ''
        self._master_key = None
        self._email = None
        self._api = None
        self._sequence_num = None

        self._root = None

    def export_config(self) :
        if self._api is not None :
            self._sequence_num = self._api.sequence_num
        return {
            'sid' : self._sid,
            'master_key' : self._master_key,
            'email' : self._email,
            'sequence_num' : self._sequence_num,
            }

    def import_config(self,config) :
        self._sid = config.get('sid','')
        self._email = config.get('email',None)
        self._master_key = config.get('master_key',None)
        self._sequence_num = config.get('sequence_num',None)

    def get_api(self) :
        if (self._api is None) :
            if (self._sid != '') :
                self._api = Mega()
                self._api.sid = self._sid
                self._api.master_key = self._master_key
                self._api.sequence_num = self._sequence_num
                self._api.users_keys = {}
            elif self._login is not None and self._password is not None :
                self._api = Mega()
                try :
                    self._api.login(self._login, self._password)
                except Exception :
                    self.errorexit(_('login failled'))
                
        return self._api

    def load_stream(self,*args,**kwargs) :
        if self._use_config :
            return self.__super.load_stream(*args,**kwargs)

    def save_stream(self,*args,**kwargs) :
        if self._use_config :
            self.__super.save_stream(*args,**kwargs)

    @CLRunner.param(aliases=['P'],need_value=True)
    def profile(self, kwargs, **rem_kwargs) :
        """Use a different profile than the default"""
        if 'profile' in kwargs :
            self._profile = kwargs['profile']
            self.set_profile(self._profile)
            self._init_account_config()
            self.load_config()

    #@CLRunner.param(aliases=['d'])
    #def debug(self, **kwargs) :
    #    '''Provide some debug informations'''
    #    self.help()
    #    print yaml.dump(self._cl_params,default_flow_style=False)

    @CLRunner.param(name='help',aliases=['h'])
    def help_param(self,**kwargs) :
        '''Get help on specific command'''
        self.help_on_command(**kwargs)
        # print "!!%r=%r" % (name,value)

    @CLRunner.param(name='no-config',aliases=['X'])
    def no_config(self,**kwargs) :
        '''Don't read/write config files'''
        self._init_account_config()

        self._use_config = False

    @CLRunner.param(name='login', need_value=True)
    def param_login(self, kwargs, **rem_kwargs) :
        '''The login to use when mode --no-config'''
        if 'login' in kwargs :
            self._login = kwargs['login']

    @CLRunner.param(name='password', need_value=True)
    def param_password(self, kwargs, **rem_kwargs) :
        '''The password to use when mode --no-config (not safe, prefer the login command)'''
        if 'password' in kwargs :
            self._password = kwargs['password']

    @CLRunner.param(name='reload',aliases=['r'])
    def param_reload(self, **kwargs) :
        """Force reload before the first action that need the filesystem"""
        self._force_reload = True

    @CLRunner.command()
    def help(self, args=[], kwargs={}) :
        """give help"""
        self.__super.help()

    @CLRunner.command(params={
        'email':{
            'need_value' : True,
            'doc' : _('The login/email'),
            'aliases' : ['e'],
            },
        })
    def login(self,args,kwargs) :
        """login to mega"""
        if 'email' in kwargs :
            self._email = kwargs['email']
            self.save_config()
        elif len(args) > 0 :
            self._email = args[0]
            self.save_config()
        if self._email is None :
            self.errorexit(_('need email to login'))
        sys.stdout.write('Login : [%s]\n' % (self._email,))
        password = getpass.getpass()
        if len(password) == 0 :
            self.errorexit(_('need a password to login'))
            
        self._api = Mega()
        try :
            self._api.login(self._email,password)
        except Exception :
            self.errorexit(_('login failled'))
        self._sid = self._api.sid
        self._master_key = self._api.master_key
        self.save_config()

        self.status('login success')

    @CLRunner.command()
    def logout(self,args,kwargs) :
        """logout from mega"""
        if self._sid != '' or self._master_key != '' :
            self._master_key = ''
            self._sid = ''
            self._sequence_num = None
            self.save_config()
            self._root = None
            self.del_stream('files')
            self.del_stream('root')
        self.status('logged out')

    def get_root(self) :
        root = None
        if self._force_reload :
            self._root = None
            self._force_reload = False
        else :
            if self._root is not None :
                return self._root
            root = self.load_stream('root')
        if root is not None :
            self._root = root
            for hfile in self._root['files'] :
                for kprop in self._root['files'][hfile] :
                    if type(self._root['files'][hfile][kprop]) == list :
                        self._root['files'][hfile][kprop] = tuple(self._root['files'][hfile][kprop])
            return self._root
        api = self.get_api()
        if api is None :
            self.errorexit(_('You must login first'))
        files = api.get_files()
        root = {}
        rootnode = {
            'h' : '00000000',
            'p' : '',
            's' : 0,
            't' : -1,
            'a' : { 'n' : '' },
            'isFile' : False,
            'isDir' : True,
            'canUpload' : False,
            }
        files[rootnode['h']] = rootnode
        self.save_stream('files',files)
        root['files'] = files
        root['tree'] = {}
        root['path'] = {}
        treeitems = {}
        for handle in files :
            file = files[handle]
            if handle not in treeitems :
                treeitems[handle] = {}
                treeitems[handle]['h'] = handle
            treeitem = treeitems[handle]
            if file is rootnode :
                root['tree'][handle] = treeitem
            else :
                if 'p' in file and file['p'] in files :
                    phandle = file['p']
                else :
                    phandle = rootnode['h']
                if phandle not in treeitems :
                    treeitems[phandle] = {}
                    treeitems[phandle]['h'] = phandle
                ptreeitem = treeitems[phandle]
                if 'children' not in ptreeitem :
                    ptreeitem['children'] = {}
                ptreeitem['children'][handle] = treeitem
                file['isFile'] = (file['t'] == 0)
                file['isDir'] = (file['t'] in (1,2,3,4))
                file['canUpload'] = (file['t'] in (1,2,4))

        def updatepath(dictchildren, parentpath, level) :
            for treeitem in dictchildren.values() :
                node = files[treeitem['h']]
                if not(node['a']) or type(node['a']) in (str,unicode) :
                    node['a'] = { 'n' : '?(%s)' % (node['h'],) }
                node['a']['path'] = posixpath.join(parentpath,node['a']['n'])
                node['a']['level'] = level
                root['path'][ node['a']['path'] ] = node['h']
                if 'children' in treeitem :
                    updatepath(treeitem['children'],node['a']['path'],level+1)
        updatepath(root['tree'],'/',0)
        self.save_stream('root',root)
        self._root = root
        return self._root

    @CLRunner.command(params={
        'filter': {'need_value': True, 'aliases': ['f'], 'doc': "filter the result using VALUE"},
        'short': {'aliases': ['s'], 'doc': "use short listing format (only the path)"},
        'long': {'aliases': ['l'], 'doc': "use a long listing format"},
        })
    def find(self, args, kwargs) :
        """list files on mega"""
        root = self.get_root()

        filter = kwargs['filter'] if 'filter' in kwargs else None
        enumerator = self._enumerate_all_nodes(root, filter, lambda node:node['a']['path'])
        if 'long' in kwargs :
            on_name = lambda node, info: "'%s'" % (node['a']['path'],)
        elif 'short' in kwargs :
            on_name = lambda node, info: node['a']['path']
        else :
            on_name = lambda node, info: ":%s '%s'" % (node['h'], node['a']['path'])

        self._display_nodes( enumerator, 'long' in kwargs, on_name)

    @CLRunner.command(params={
        'filter' : {'need_value' : True, 'aliases' : ['f'], 'doc' : "filter the result using VALUE"},
        'short': {'aliases': ['s'], 'doc': "use short listing format (only the indent and the name)"},
        'long': {'aliases': ['l'], 'doc': "use a long listing format"},
        })
    def show(self, args, kwargs) :
        """list files on mega"""
        root = self.get_root()

        filter = kwargs['filter'] if 'filter' in kwargs else None
        enumerator = self._enumerate_all_nodes(root, filter, lambda node:node['a']['n'])
        if 'long' in kwargs :
            on_name = lambda node, info: "%s'%s'" % ('  '*node['a']['level'], node['a']['n'],)
        elif 'short' in kwargs :
            on_name = lambda node, info: "%s%s" % ('  '*node['a']['level'], node['a']['n'])
        else :
            on_name = lambda node, info: ":%s %s'%s'" % (node['h'],'  '*node['a']['level'], node['a']['n'])

        self._display_nodes( enumerator, 'long' in kwargs, on_name)

    def _enumerate_all_nodes(self, root, filter, filter_on) :
        for path in sorted(root['path']) :
            node = root['files'][root['path'][path]]
            if (filter is None) or (filter.lower() in filter_on(node).lower()) :
                yield node


    def _enumerate_nodes(self, root, path) :
        if path == '/' :
            pathparts = [ '/' ]
        else :
            # pathparts => [ '/', '/Poide', '/Praf', '/Pido' ] if path == '/Poide/Praf/Pido'
            pathparts = [ '/' ] + [ '/' + part for part in path.split('/')[1:] ]
        current_tree = root['tree']
        current_path = ''
        for pathpart in pathparts :
            current_path += pathpart
            current_path = current_path.replace('//','/')
            if current_path in root['path'] :
                current_handle = root['path'][current_path]
                if current_handle in current_tree :
                    if 'children' in current_tree[current_handle] :
                        current_tree = current_tree[current_handle]['children']
                    else :
                        current_tree = {}
                        # self.errorexit(_('Hum... Something went wrong somewhere...'))
                else :
                    self.errorexit(_('Hum... Something went wrong somewhere...'))
            else :
                self.errorexit(_('Hum... Something went wrong somewhere...'))
        file_handles = current_tree.keys()
        for handle in sorted(file_handles, key=lambda h:root['files'][h]['a']['n']) :
            yield root['files'][handle]

    def _get_infos(self, file) :
        infos = {}
        file.get('t',None)
        types = {
            0 : 'File',
            1 : 'Folder',
            2 : 'Drive Folder',
            3 : 'Inbox Folder',
            -1 : 'Root Folder',
        }
        infos['types'] = types.get(file.get('t', None),'??')
        infos['canUpload'] = file['canUpload']
        infos['name'] = file['a']['n']
        infos['path'] = file['a']['path']
        infos['size'] = str(file.get('s',''))
        ts = file.get('ts', None)
        if ts is not None :
            tm = time.gmtime(ts)
            infos['time'] = "%04d-%02d-%02d %02d:%02d:%02d" % (tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
        else :
            infos['time'] = ''
        infos['handle'] = ':'+file['h']
        letters = infos['letters'] = {}
        letters['dir'] = 'd' if file['isDir'] else '-'
        letters['upload'] = 'u' if file['canUpload'] else '-'
        letters['read'] = 'r'
        letters['write'] = 'w'
        letters['execute'] = 'x' if file['isDir'] else '-'
        infos['attr'] = '%(dir)s%(upload)s%(read)s%(write)s%(execute)s' % letters
        return infos


    @CLRunner.command(params={
        'long' : {
            'need_value' : False,
            'aliases' : ['l'],
            'doc' : "use a long listing format",
            },
        })
    def ls(self, args, kwargs) :
        """list files in a mega directory"""
        root = self.get_root()
        if len(args) == 0:
            self.errorexit(_('Need a folder to list'))
        dirnode = self.findnode(root, args[0], isdir=True)
        path = dirnode['a']['path']

        self._display_nodes(self._enumerate_nodes(root, path), 'long' in kwargs, lambda node, infos:node['a']['n'])

    def _display_nodes(self, node_enumerator, is_long, on_name):
        if is_long :
            lines = []
            for node in node_enumerator :
                infos = self._get_infos(node)
                lines.append((infos['attr'],infos['handle'],infos['size'],infos['time'],on_name(node, infos)))
            aligns = ('-','-','','-','-')
            pattern = " ".join( "%" + align + str(max(map(len,col))) + "s" for col,align in zip(zip(*lines),aligns) )
            for line in lines :
                self.status(pattern % line)
        else :
            for node in node_enumerator :
                self.status(on_name(node, None))


    @CLRunner.command(params={
        'name' : {'doc': "show only name", 'aliases': ['n']},
        'path' : {'doc': "show only path", 'aliases': ['p']},
        'size' : {'doc': "show only size", 'aliases': ['s']},
        'time' : {'doc': "show only time", 'aliases': ['t']},
        'handle' : {'doc': "show only handle", 'aliases': ['H']},
        'attributes' : {'doc': "show only attributes", 'aliases': ['a','attr']},
        })
    def info(self, args, kwargs) :
        """get informations on a file or folder"""
        root = self.get_root()
        if len(args) == 0 :
            self.errorexit(_('Need a file or a folder'))
        nodes = []
        for item in args :
            node = self.findnode(root, item)
            nodes.append(node)
        restricted_view = False
        params = {}
        for key in ('name','path','size','time','handle','attributes') :
            if key in kwargs :
                restricted_view = True
                params[key] = True
        for node in nodes :
            infos = self._get_infos(node)
            if restricted_view :
                if 'name' in params :
                    self.status(infos['name'])
                if 'path' in params :
                    self.status(infos['path'])
                if 'size' in params :
                    self.status(infos['size'])
                if 'time' in params :
                    self.status(infos['time'])
                if 'handle' in params :
                    self.status(infos['handle'])
                if 'attributes' in params :
                    self.status(infos['attr'])
            else :
                self.status('Name: [%s]' % (infos['name'],))
                self.status('Path: [%s]' % (infos['path'],))
                self.status('Size: [%s]' % (infos['size'],))
                self.status('Time: [%s]' % (infos['time'],))
                self.status('Handle: [%s]' % (infos['handle'],))
                self.status('Attributes: [%s]' % (infos['attr'],))

    def findnode(self, root, arg, isfile=False, isdir=False) :
        if arg.startswith(':') :
            handle = arg[1:]
            if handle not in root['files'] :
                self.errorexit(_('No node with handle [%s]')%(handle,))
            node = root['files'][handle]
        else :
            path = arg
            if path not in root['path'] :
                self.errorexit(_('No node with path [%s]')%(path,))
            node = root['files'][root['path'][path]]
        if isfile and not node['isFile'] :
            self.errorexit(_('Argument [%s] should be a file, but [%s] is not a file')%(arg, node['a']['n']))
        if isdir and not node['isDir'] :
            self.errorexit(_('Argument [%s] should be a folder,  but [%s] is not a folder')%(arg, node['a']['n']))
        return node

    def _get_time_speed(self, size, start_time, stop_time):
        return (int((stop_time-start_time)*10)/10., int((size*100)/(1024*(stop_time-start_time)))/100. )

    def _get_status_transfert(self, size, start_time, stop_time):
        return _('Transfert completed in %s seconds (%s KiB/s)') % self._get_time_speed(size, start_time, stop_time)

    @CLRunner.command()
    def get(self, args, kwargs) :
        """get one or more files"""
        root = self.get_root()
        if len(args) == 0 :
            self.errorexit(_('Need a file handle to download'))
        for arg in args :
            node = self.findnode(root, arg, isfile=True)
            filename = node['a']['n']
            size = node['s']
            self.status(_('Getting [%s] (%s bytes)')%(filename, size))
        
            api = self.get_api()
            start_time = time.time()
            api.download((node['h'], node), '.')
            stop_time = time.time()
            self.status(self._get_status_transfert(size, start_time, stop_time))



    @CLRunner.command()
    def put(self, args, kwargs) :
        """put one or more files"""
        root = self.get_root()
        if len(args) < 2:
            self.errorexit(_('Need one or more file to upload and a directory handle where to upload'))
        for filename in args[:-1]:
            if not(os.path.exists(filename)):
                self.errorexit(_("File [%s] doesn't exists") % (filename,))

        node = self.findnode(root, args[-1], isdir=True)
        for filename in args[:-1]:
            api = self.get_api()
            dirname, basename = os.path.split(filename)
            size = os.stat(filename).st_size
            self.status(_('Sending [%s] (%s bytes)')%(filename,size))
            start_time = time.time()
            api.upload(filename, node['h'])
            stop_time = time.time()
            self.status(self._get_status_transfert(size, start_time, stop_time))


    @CLRunner.command()
    def reload(self, args, kwargs) :
        """reload the filesystem"""
        self._root = None
        self.del_stream('root')
        self.get_root()

    @CLRunner.command()
    def mkdir(self, args, kwargs) :
        """create a new remote directory"""
        if len(args) < 2:
            self.errorexit(_('Need a directory name and a place where to create it (directory path or handle'))
        api = self.get_api()
        root = self.get_root()
        node = self.findnode(root, args[1], isdir=True)
        api.create_folder(args[0], node['h'])

    @CLRunner.command()
    def geturl(self, args, kwargs) :
        """get from a url"""
        if len(args) == 0 :
            self.errorexit(_('Need at least a url to download'))
        for arg in args :
            if '!' not in arg :
                self.errorexit(_("[%s] is not a valid mega url") % (arg,))
        api = self.get_api()
        for arg in args :
            file_handle, file_key = arg.split('!')[-2:]
            self.status(_('Downloading https://mega.co.nz/#!%s!%s') % (file_handle, file_key))
            api.download_file(file_handle, file_key, is_public=True)

    @CLRunner.command()
    def quota(self, args, kwargs) :
        """get account's quota"""
        api = self.get_api()
        storage = api.get_storage_space(giga=True)
        self.status(_("Current quota: [%(used).2f/%(total).2f]") % storage)

    @CLRunner.command(aliases=['move'])
    def mv(self, args, kwargs) :
        """move an item into another directory"""
        if len(args) < 2 :
            self.errorexit(_('Need at least an item to move, and a diretcory where to move'))
        items = args[:-1]
        destination = args[-1]
        root = self.get_root()
        nodes = []
        for item in items :
            node = self.findnode(root, item)
            nodes.append(node)
        destination_node = self.findnode(root, destination)
        api = self.get_api()
        for node in nodes :
            api.api_request({'a': 'm', 'n': node['h'], 't': destination_node['h'], 'i': api.request_id})

    @CLRunner.command()
    def rename(self, args, kwargs) :
        """rename an item"""
        if len(args) != 2 :
            self.errorexit(_('Need an item to rename, and a new name'))
        root = self.get_root()
        api = self.get_api()
        node = self.findnode(root, args[0])
        newname = args[1]
        api.rename((node['h'],node), newname)

    def _assert_public_url(self, url) :
        'https://mega.co.nz/#!rwQnTIZb!c4Wri1IAVU92FSgzJvk2z3uXonY7Rf3yQotO03Kyhrs'
        url_parts = url.split('!')
        if not(url.startswith('https://mega.co.nz/#!')) or len(url_parts)!=3 :
            self.errorexit(_('Not a valid public url: [%s]') % url)
        url_handle, url_key = url_parts[1:]
        if len(url_handle) != 8 or len(url_key) != 43 :
            self.errorexit(_('Not a valid public url: [%s]') % url)
        return url_handle, url_key


    @CLRunner.command(name='import', params={
        'stdin' : {'doc': "parse stdin in order to find urls", 'aliases': ['i']},
        })
    def import_command(self, args, kwargs):
        """import urls into a folder"""
        is_stdin = False
        folder_arg = '/Cloud Drive'
        urls = []

        if 'stdin' in kwargs:
            is_stdin = True
            if len(args) > 1:
                self.errorexit(_('Too much arguments, you need at most a folder where to put file in stdin mode'))
            if len(args) == 1:
                folder_arg = args[-1]
        else:
            is_stdin = False
            if len(args) == 0:
                self.errorexit(_('Need one or more url to import, and eventually a folder where to put files'))
            urls = args
            if (args[-1][:1] in ('/',':')):
                urls = args[:-1]
                folder_arg = args[-1]

        if is_stdin:
            for line in sys.stdin:
                urls += re_url.findall(line)

        public_infos = [ self._assert_public_url(url) for url in urls ]
        api = self.get_api()
        root = self.get_root()

        node = self.findnode(root, folder_arg, isdir=True)
        for pfile_handle, pfile_key in public_infos:
            self.status(_("Importing [https://mega.co.nz/#!%s!%s!] into [%s]") % (pfile_handle, pfile_key, node['a']['n']))
            api.import_public_file(pfile_handle, pfile_key, dest_node=node)

    @CLRunner.command(params={
        'name' : {'doc': "show only name", 'aliases': ['n']},
        'size' : {'doc': "show only size", 'aliases': ['s']},
        })
    def infourl(self, args, kwargs):
        """get info on a url"""
        if len(args) == 0:
            self.errorexit(_('Need a public url to get info'))
        urls = args
        public_infos = [ list(self._assert_public_url(url)) + [url] for url in urls ]
        api = self.get_api()

        datas = []
        for pfile_handle, pfile_key, url in public_infos:
            try:
                data = api.get_public_file_info(pfile_handle, pfile_key)
            except Exception:
                data = {'name': '', 'size': ''}
            if data is None :
                data = {'name': '', 'size': ''}
            data['url'] = url
            datas.append(data)

        restricted_view = False
        params = {}
        for key in ('name','size') :
            if key in kwargs :
                restricted_view = True
                params[key] = True
        for infos in datas :
            if restricted_view :
                if 'name' in params :
                    self.status(infos['name'])
                if 'size' in params :
                    self.status(infos['size'])
            else :
                self.status('Url: [%s]' % (infos['url'],))
                self.status('Name: [%s]' % (infos['name'],))
                self.status('Size: [%s]' % (infos['size'],))

    @CLRunner.command(aliases=['remove'])
    def rm(self, args, kwargs):
        """remove one or more file or folder"""
        if len(args) == 0 :
            self.errorexit(_('Need at least an item to delete'))
        api = self.get_api()
        root = self.get_root()
        nodes = [ self.findnode(root, arg) for arg in args ]
        for node in nodes:
            self.status(_("Removing [%s] (:%s)") % (node['a']['n'],node['h']))
            api.destroy(node['h'])
            self.status(_("    [%s] (:%s) removed.") % (node['a']['n'],node['h']))




        

