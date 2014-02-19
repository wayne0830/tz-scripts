#!/usr/bin/env python
#coding=utf8
import os, sys
import paramiko
from datetime import *
import threading as thr
import coloration as col

class ModuleDeployer(thr.Thread):
    ''' thread to deploy a module'''

    def __init__(self, module_config):
        thr.Thread.__init__(self)
        self.config = module_config

        # init ssh tools
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(module_config.hostname, int(module_config.port), module_config.username, module_config.password)
        self.sftp = self.ssh.open_sftp()

    def log(self, msg, newline = True):
        msg = '[' + self.config.module_name + '] ' + str(msg)
        if newline:
            print msg
        else:
            print msg + ','

    def sshExec(self, cmd):
        self.log(col.green('==> ') + col.yellow(cmd))
        return self.ssh.exec_command(cmd)

    def sshCmd(self, cmd, ignoreError = False):
        stdin, stdout, stderr = self.sshExec(cmd)
        line = stdout.readline()
        while len(line) > 0:
            self.log(line)
            line = stdout.readline()
        errInfo = stderr.read()
        if len(errInfo) > 0:
            self.log(col.red('execute cmd failed => ' + errInfo))
            if not ignoreError:
                sys.exit(1)

    def upload(self):
        target_path = '/tmp/%s' % (self.package_filename)
        self.log(col.yellow('transfer package(%s), from %s to %s' % (self.package_filename, self.config.package_path, target_path)));
        self.sftp.put(self.config.package_path, target_path)

    def stop_tomcat(self):
        stdin, stdout, stderr = self.sshExec("ps aux|grep %s/bin|grep -v 'grep'|awk '{print $2}'" % (self.config.tomcat_dir))
        pidlist = stdout.read()
        for pid in pidlist.split('\n'):
            if len(pid.strip()) == 0:
                continue
            self.sshCmd("kill -9 " + pid)

    def backup_package(self):
        placeholders = { 'tomcat_dir' : self.config.tomcat_dir, 'package_filename' : self.package_filename, 'backup_dir' : self.config.backup_dir }
        self.sshCmd('test -d %(backup_dir)s || mkdir -p %(backup_dir)s' % placeholders)
        placeholders["timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sshCmd('test -f %(tomcat_dir)s/webapps/%(package_filename)s && mv %(tomcat_dir)s/webapps/%(package_filename)s %(backup_dir)s/%(package_filename)s_%(timestamp)s' % placeholders, True)

    def replace_package(self):
        placeholders = { 'tomcat_dir' : self.config.tomcat_dir, 'package_filename' : self.package_filename }
        self.sshCmd('rm -rf %(tomcat_dir)s/webapps/%(package_filename)s*' % placeholders)
        self.sshCmd('rm -rf %(tomcat_dir)s/work/*' % placeholders)
        self.sshCmd('mv /tmp/%(package_filename)s %(tomcat_dir)s/webapps/%(package_filename)s' % placeholders)

    def start_tomcat(self):
        self.sshCmd('%s/bin/startup.sh' % (self.config.tomcat_dir))

    def run(self):
        if not os.path.exists(self.config.package_path):
            self.log(col.red('package not found, fail this deployment.'))
            return False
        self.package_filename = os.path.basename(self.config.package_path)
        self.upload()
        self.stop_tomcat()
        self.backup_package()
        self.replace_package()
        self.start_tomcat()
        
        self.log(col.green('==> finish!'))

        return True

class ModuleConfig:

    def __init__(self, values):
        self.module_name = values["module-name"]
        self.hostname = values["hostname"]
        self.port = int(values["port"])
        self.username = values["username"]
        self.password = values["password"]
        self.tomcat_dir = values["tomcat-dir"]
        self.package_path = values["package-path"]
        self.backup_dir = values["backup-dir"]


