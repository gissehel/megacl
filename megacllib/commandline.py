#!/usr/bin/env python

# from megaclient import MegaClient
from mega import Mega
import sys
import os
import time
import yaml
# import pyaml
import shutil
import getpass
import posixpath

from supertools import superable
from cltools import _
from cltools import ConfigurableCLRunnable
from cltools import CLRunner

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

    def get_client(self) :
        if (self._api is None) and (self._sid != '') :
            self._api = Mega()
            self._api.sid = self._sid
            self._api.master_key = self._master_key
            self._api.sequence_num = self._sequence_num
            self._api.users_keys = {}
        return self._api

    @CLRunner.param(aliases=['d'])
    def debug(self, **kwargs) :
        '''Provide some debug informations'''
        self.help()
        print yaml.dump(self._cl_params,default_flow_style=False)

    @CLRunner.param(name='help',aliases=['h'])
    def help_param(self,**kwargs) :
        '''Get help on specific command'''
        self.help_on_command(**kwargs)
        # print "!!%r=%r" % (name,value)

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
            
        self._api = Mega.login(self._email,password)
        try :
            pass
            # self._api.login()
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
            self.del_stream('root')
        self.status('logged out')

    def get_root(self) :
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
        client = self.get_client()
        if client is None :
            self.errorexit(_('You must login first'))
        files = client.get_files()
        root = {}
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
            if 'p' in file and file['p'] in files :
                phandle = file['p']
                if phandle not in treeitems :
                    treeitems[phandle] = {}
                    treeitems[phandle]['h'] = phandle
                ptreeitem = treeitems[phandle]
                if 'children' not in ptreeitem :
                    ptreeitem['children'] = {}
                ptreeitem['children'][handle] = treeitem
            else :
                root['tree'][handle] = treeitem
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
        'filter' : {
            'need_value' : True,
            'aliases' : ['f'],
            },
        })
    def find(self, args, kwargs) :
        """list files on mega"""
        root = self.get_root()
        for path in sorted(root['path']) :
            node = root['files'][root['path'][path]]
            if ('filter' not in kwargs) or (kwargs['filter'].lower() in node['a']['path'].lower()) :
                self.status(":%s '%s'" % (node['h'],node['a']['path']))

    @CLRunner.command(params={
        'filter' : {
            'need_value' : True,
            'aliases' : ['f'],
            },
        })
    def show(self, args, kwargs) :
        """list files on mega"""
        root = self.get_root()
        for path in sorted(root['path']) :
            node = root['files'][root['path'][path]]
            if ('filter' not in kwargs) or (kwargs['filter'].lower() in node['a']['n'].lower()) :
                self.status(":%s %s'%s'" % (node['h'],'  '*node['a']['level'], node['a']['n']))
    
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
        if isfile and node['t']!=0 :
            self.errorexit(_('Argument [%s] should be a file, but [%s] is not a file')%(arg, node['a']['n']))
        if isdir and node['t'] not in (1,2,4) :
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
        
            client = self.get_client()
            start_time = time.time()
            client.download((node['h'], node), '.')
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
            client = self.get_client()
            dirname, basename = os.path.split(filename)
            size = os.stat(filename).st_size
            self.status(_('Sending [%s] (%s bytes)')%(filename,size))
            start_time = time.time()
            client.upload(filename, node['h'])
            stop_time = time.time()
            self.status(self._get_status_transfert(size, start_time, stop_time))


    @CLRunner.command()
    def reload(self, args, kwargs) :
        """reload the filesystem"""
        self._root = None
        self.del_stream('root')
        self.get_root()

