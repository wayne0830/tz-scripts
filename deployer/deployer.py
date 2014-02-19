#!/usr/bin/env python
#coding=utf8

import os, sys
import argparse
import re
import ConfigParser
import paramiko
import time
import coloration as col
import module_deployer as md

GENERAL = 'general'
GLOBAL = 'global'
DEPLOY_OPTIONS = [ 'hostname','port','username','password','tomcat-dir' ]

# function to run system cmd
def local_cmd(cmd):
    print col.color("==> ",col.GREEN) + col.color(cmd,col.YELLOW)
    os.system(cmd)

# define arguments of this script
parser = argparse.ArgumentParser(description='deploy projects automatically.')
parser.add_argument("-c", "--config",
                    dest="config",
                    default="deploy.ini",
                    help="path of config file.")

def get_path_from_task(package_task):
    arr = package_task.split(':')
    path = config.get(GLOBAL, 'tz-dir')
    if not path.endswith("/"):
        path += '/'
    for s in arr:
        path += s + '/'
    extension = re.search("\/[^\/]+\/$", path).group()
    extension = re.sub('\/', '', extension)
    path = re.sub('\/[^\/]+\/$', '', path) + '/target/libs'
    for f in os.listdir(path):
        package_path = path + '/' + f
        if os.path.isfile(package_path) and f.endswith(extension):
            return package_path
    return None

if __name__ == '__main__':
    # prepare arguments
    args = parser.parse_args()

    # load configuration
    temp_config = ConfigParser.ConfigParser()
    temp_config.read(args.config)
    default_config = { key:value for key,value in temp_config.items(GENERAL) }
    config = ConfigParser.ConfigParser(default_config)
    config.read(args.config)

    # gather modules
    modules = []
    dModules = {}
    for module in config.sections():
        if module == GLOBAL or module == GENERAL:
            continue
        priority = config.getint(module, 'priority')
        if priority not in dModules:
            dModules[priority] = []
        dModules[priority].append(module)
        modules.append(module)

    print 'modules to deploy: ' + col.color(str(modules),col.GREEN)

    # prepare packages
    gradle_tasks = set()
    for mdl in modules:
        gradle_tasks.add(config.get(mdl, 'package-task'))
    package_cmd = "gradle --parallel -p %s -Pprofile=%s clean " % (config.get(GLOBAL, 'tz-dir'), config.get(GLOBAL, 'profile'))
    for task in gradle_tasks:
        package_cmd += task + ' '
    local_cmd(package_cmd)

    if config.has_option(GLOBAL, 'interval'):
        interval = config.getint(GLOBAL, 'interval')
    else:
        interval = 0
    # run deployers
    for target_modules in [dModules[key] for key in sorted(dModules.keys(),reverse=True)]:
        deployers = []
        for mdl in target_modules:
            package_path = get_path_from_task(config.get(mdl, 'package-task'))
            if package_path is None:
                print col.red("module[%s] don't has package, can't deploy it!" % (mdl))
                continue
            values = { "module-name" : mdl, "package-path" : package_path, "backup-dir" : config.get(GLOBAL, 'backup-dir')}
            for option in DEPLOY_OPTIONS:
                values[option] = config.get(mdl, option)
            mdl_cfg = md.ModuleConfig(values)
            deployer = md.ModuleDeployer(mdl_cfg)
            deployers.append(deployer)
            deployer.start()
        for dpl in deployers:
            dpl.join()

        if interval > 0:
            counter = interval
            while counter > 0:
                print '.',
                counter = counter - 1
                time.sleep(1)
            print ''


