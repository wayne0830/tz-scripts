#!/usr/bin/env python
# coding=utf8

import sys
from pymongo import MongoClient

usercenter_host = "192.168.160.77"
usercenter_username = "tzuser"
usercenter_password = "asdf"

core_host = "192.168.160.77"
core_usename = "tz"
core_password = "tz"

province_region = {}
regoin_name = {"CNXNR":"西南", "CNHBR":"华北", "CNSHR":"华东", "CNHDR":"华东", "CNSAR":"港澳台", "CNHNR":"华南" }

info_log = open('filler-info.log','w')
error_log = open('filler-error.log','w')

def info(msg):
    print msg
    info_log.write(msg + "\n")

def error(msg):
    print msg
    error_log.write(msg + "\n")

def prepare_regions():
    core_client = MongoClient(core_host)
    db = core_client["core"]
    db.authenticate(core_usename,core_password)
    for province in db["core.entity.Province"].find():
        province_region[province["code"]] = province["regionCode"]
    error("%d provinces loaded from MongoDB.COREd" % (len(province_region)))

def init_customer_collection():
    client = MongoClient(usercenter_host)
    db = client["usercenter"]
    db.authenticate(usercenter_username,usercenter_password)
    return db["Customer"]

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')

    prepare_regions()
    coll_customer = init_customer_collection()
    for cus in coll_customer.find():
        if 'type' not in cus:
            error("type field missing for Customer[%s]" % str(cus['_id']))
            continue
        if cus['type'] == 'COMPANY':
            if 'companyInfo' not in cus or 'addr' not in cus['companyInfo']:
                error('addr field missing for Customer[%s]' % str(cus['_id']))
                continue
            province = cus['companyInfo']['addr'].get('province')
        elif cus['type'] == 'INDIVIDUAL':
            if 'personalInfo' not in cus or 'addr' not in cus['personalInfo']:
                error('addr field missing for Customer[%s]' % str(cus['_id']))
                continue
            province = cus['personalInfo']['addr'].get('province')
        if province is None:
            error('province field missing for Customer[%s]' % str(cus['_id']))
            continue
        if province not in province_region:
            error('cannot find region of this province[%s], Customer[%s]' % (province, str(cus['_id'])))
        else:
            region = province_region[province]
            region_name = regoin_name[region]
            info('find region[%s(%s)] of province[%s], Customer[%s]' % (region_name, region, province, str(cus['_id'])))
            coll_customer.update({'_id':cus['_id']},{"$set":{'region':region_name}})


