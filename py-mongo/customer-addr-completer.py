#!/usr/bin/env python
# coding=utf8

import sys
from pymongo import MongoClient
import codecs
import csv

usercenter_host = "192.168.160.77"
usercenter_username = "tzuser"
usercenter_password = "asdf"

core_host = "192.168.160.77"
core_usename = "tz"
core_password = "tz"

mobile_region = {}
zip_code_region = {}
cd = 'utf8'
region_province = {}
region_city = {}

info_log = open('info.log','w')
error_log = open('error.log','w')

def info(msg):
    info_log.write(msg + "\n")

def error(msg):
    error_log.write(msg + "\n")

def prepare_mobile_prefixes():
    for words in csv.reader(open("mobile_guishudi.csv")):
        if len(words) < 4 or len(words[2]) == 0 or len(words[3]) == 0:
            continue
        mobile_region[words[1]] = (unicode(words[2],'gb18030'),unicode(words[3],'gb18030'))
    print "size of mobile_region:%d" % (len(mobile_region))
    
def prepare_zipcodes():
    for line in codecs.open("city_zipcode.txt",'r','utf8'):
        words = line.split()
        zip_code_region[words[2].encode(cd)] = (words[0],words[1])
    print "size of city_code_region:%d" % (len(zip_code_region))

def prepare_regions():
    core_client = MongoClient(core_host)
    db = core_client["core"]
    db.authenticate(core_usename,core_password)
    for province in db["core.entity.Province"].find():
        region_province[province["nameCn"].encode(cd).rstrip("省")] = province["code"]
    for city in db["core.entity.City"].find():
        region_city[city["nameCn"].encode(cd).rstrip("市")] = city["code"]
    print "size of region_province:%d" % (len(region_province))
    print "size of region_city:%d" % (len(region_city))

def init_customer_collection():
    client = MongoClient(usercenter_host)
    db = client["usercenter"]
    db.authenticate(usercenter_username,usercenter_password)
    return db["Customer"]

def guess_addr_name(contact):
    if "zipCode" in contact and len(contact["zipCode"]) > 0 and not contact["zipCode"].isspace():
        zipcode = contact["zipCode"]
        if zipcode in zip_code_region:
            return (zipcode,) + zip_code_region[zipcode]
        else:
            return (zipcode,None,None)
    elif "phone" in contact and len(contact["phone"]) > 0 and not contact["phone"].isspace():
        mobile_prefix = contact["phone"][0:7]
        mobile = contact["phone"]
        if mobile_prefix in mobile_region:
            return (mobile,) + mobile_region[mobile_prefix]
        else:
            return (mobile,None,None)
    else:
        return (None,None,None)

def guess_province_code(province_name):
    if isinstance(province_name, unicode):
        province_name = province_name.encode(cd)
    province_key = province_name.rstrip("省")
    return region_province.get(province_key)

def guess_city_code(city_name):
    if isinstance(city_name, unicode):
        city_name = city_name.encode(cd)
    city_key = city_name.rstrip("市")
    return region_city.get(city_key)

def guess_addr_code(cus, info_field, contact_field, mongo_collection):
    if info_field not in cus or contact_field not in cus[info_field]:
        error("contact info of Customer[%s - %s] missing." % (str(cus["_id"]), cus["shortName"]))
        return False
    contact = cus[info_field][contact_field]
    clue,province_name,city_name = guess_addr_name(contact)
    if province_name is None or city_name is None:
        error("address name fetch failed, for Customer[%s-%s-%s]" % (str(cus["_id"]), cus["shortName"],clue))
        return False
    province_code = guess_province_code(province_name)
    city_code = guess_city_code(city_name)
    info("Customer[%s-%s] => Province:%s(%s) City:%s(%s)" % (str(cus["_id"]), cus["shortName"], province_name,province_code,city_name,city_code))
#    mongo_collection.update({"_id":cus["_id"]},{"$set":{info_field+".addr.province":province_code,info_field+".addr.city":city_code}})
    return True

reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    try:
        prepare_mobile_prefixes()
        prepare_zipcodes()
        prepare_regions()

        guessed_addr = []
        coll_customer = init_customer_collection()
        successed_count = 0
        failed_count = 0

        individuals = coll_customer.find({"type":"INDIVIDUAL","$or":[{"personalInfo.addr.province":{"$exists":0}},{"personalInfo.addr.city":{"$exists":0}}]})
        for cus in individuals:
            if guess_addr_code(cus, "personalInfo", "personalContact",coll_customer):
                successed_count += 1
            else:
                failed_count += 1

        companies = coll_customer.find({"type":"COMPANY","$or":[{"companyInfo.addr.province":{"$exists":0}},{"companyInfo.addr.city":{"$exists":0}}]})
        for cus in companies:
            if guess_addr_code(cus, "companyInfo", "responsibleInfo",coll_customer):
                successed_count += 1
            else:
                failed_count += 1
        print "Successed:%d" % successed_count
        print "Failed:%d" % failed_count
    finally:
        info_log.close()
        error_log.close()

