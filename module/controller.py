# coding=UTF-8
import requests
import json
import time
import re
import ast
import logging
import os
import math
import time
import ctypes 
import threading
from datetime import datetime
from langconv import Converter
from flask import Flask, Response, render_template, request, redirect, jsonify
from threading import Timer,Thread,Event
import dao
import const
from flask_restful import Resource
import log as logpy
import pymysql
import service
import utils
from datetime import datetime

log = logpy.logging.getLogger(__name__)

def setup_route(api):
    api.add_resource(default, '/')
    api.add_resource(healthCheck, '/healthCheck')
    api.add_resource(botstatus, '/botstatus')
    api.add_resource(botexecute, '/botexecute')
    api.add_resource(bot_work_status, '/workstatus')

class default(Resource):
    log.debug('default json')
    def get(self):
        return {
            'status': 0,
            'message': 'success'
        }, 200

class healthCheck(Resource):
    log.debug('check health')
    def get(self):
        return {
            'status': 0,
            'message': 'success'
        }, 200

class botstatus(Resource):
    def get(self):
        bot_id=request.args.get('bot_id')
        if bot_id == None:
            return {'status': 422,'message': "Missing required parameters [bot_id]",'result': {},}, 422

        try:
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,charset='utf8')
            data = dao.Database(conn).query_bot_work_list(bot_id)
            log.info(data)
            if len(data) == 1:
                return {'status': 200,'message': 'success','result': {'bot_id': data[0][0],'work': data[0][1] ,'return_flag':data[0][2] ,'return_finish':data[0][3]},}, 200
            else:
                return {'status': 204,'message': "bot_id: " + bot_id + " doesn't exist",'result': {},}, 204

        except Exception as e:
            log.info("query_bot_work_list occured some error: " + utils.except_raise(e))
            return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0])}, 500
        finally:
            try:
                conn.close()
            except Exception as e:
                log.info("close connection error: " + utils.except_raise(e))
                return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0])}, 500

    def post(self):
        content_type=request.headers.get('content-type')
        content_type=''.join( i.lower() for i  in content_type.split() )
        log.info(content_type)
        if content_type != 'application/json':
            return {'status': 415,'message':'content type should be [application/json]'}, 415

        receive_json=request.get_json()
        log.info(receive_json)
        if receive_json == None or receive_json.get('bot_id') == None or receive_json.get('work') == None or receive_json.get('return_flag') == None or receive_json.get('return_finish') == None:
            return {'status': 422,'message':'Error, missing necessary parameter [bot_id] or [work] or [return_flag] or [return_finish]'}, 422

        try:
            index=[0,1,2,3,4,5].index(receive_json.get('work'))
            log.info(index)
        except Exception as e:
            log.info("work parameter error: " + utils.except_raise(e))
            return {'status': 422,'message': 'work should be int [0, 1, 2, 3, 4, 5]'}, 422

        try:
            index=[0,1].index(receive_json.get('return_flag'))
            log.info(index)
        except Exception as e:
            log.info("work parameter error: " + utils.except_raise(e))
            return {'status': 422,'message': 'return_flag should be int [0, 1]'}, 422

        try:
            regResult=re.search(r"^\d{2}$", str(receive_json.get('return_finish')))
            if regResult == None:
                return {'status': 422,'message': 'return_finish should be regex [^\d{2}$]'}, 422
        except Exception as e:
            log.info("work parameter error: " + utils.except_raise(e))

        try:
            data = {}
            data['bot_id']=receive_json['bot_id']
            data['work']=receive_json['work']
            data['return_flag']=receive_json['return_flag']
            data['return_finish']=receive_json['return_finish']
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,charset='utf8')
            update_row = dao.Database(conn).insert_bot_work_list( data )
            log.info(update_row)
            # # if update_row != 0:
            return {'status': 200,'message': 'success','result': {'description': "Success, update work with param:" + json.dumps(data)},}, 200
        except Exception as e:
            log.info("query_bot_work_list occured some error: " + utils.except_raise(e))
            return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0])}, 500
        finally:
            try:
                conn.close()
            except Exception as e:
                log.info("close connection error: " + utils.except_raise(e))
                return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0]) }, 500

class botexecute(Resource):
    def post(self):
        json_from_request = json.loads(Converter('zh-hans').convert(request.stream.read().decode('utf-8')))
        user_execute_work = json_from_request['task_info']['bot_execute']
        log.info(json.dumps(json_from_request))
        app_id = json_from_request['app_id']
        log.info('app_id: ' + app_id)
        work_stats=0
        update_kv_map={}
        try:
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,charset='utf8')
            data = dao.Database(conn).query_bot_work_list(app_id)
            log.debug(data)
            if len(data) == 1:
                work_stats=data[0][1]
        except Exception as e:
            log.info("query_bot_work_list occured some error: "+utils.except_raise(e))
        finally:
            conn.close()

        if work_stats == 0:
            try:
                data = {}
                data['bot_id']=json_from_request['app_id']
                data['work']=user_execute_work
                conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,charset='utf8')
                update_row = dao.Database(conn).insert_work_to_bot_work_list( data )
            except Exception as e:
                log.info("insert_work_to_bot_work_list occured some error: "+utils.except_raise(e))
            finally:
                conn.close()
            log.info(user_execute_work)
            update_kv_map = {
                "bot_response": work_num_to_str(int(user_execute_work)) + '派車，成功'
            }
        else:
            update_kv_map = {
                "bot_response": '正在執行' + work_num_to_str(work_stats) + '任務，請稍後在下命令'
            }

        ret = encapsule_rtn_format(update_kv_map, None)
        return Response(json.dumps(ret), status=200)


class bot_work_status(Resource):
    def post(self):
        json_from_request = json.loads(Converter('zh-hans').convert(request.stream.read().decode('utf-8')))
        app_id = json_from_request['app_id']
        log.info('app_id: ' + app_id)
        try:
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,charset='utf8')
            data = dao.Database(conn).query_bot_work_list(app_id)
            log.info(data)
            if len(data) == 1:
                result = {'bot_id': data[0][0],'work': data[0][1] ,'return_flag':data[0][2] ,'return_finish':data[0][3]}
                log.info(result)
                update_kv_map = {
                   "bot_response": work_num_to_str(data[0][1]) + return_flag_to_str(data[0][2])
                }
                ret = encapsule_rtn_format(update_kv_map, None)
                return Response(json.dumps(ret), status=200)
        except Exception as e:
            log.info("query_bot_work_list occured some error: "+utils.except_raise(e))
        finally:
            conn.close()



def work_num_to_str(num):
    work = {
        0 : "機器人可執行任務",
        1 : "病房消毒",
        2 : "開刀房消毒",
        3 : "廢棄物回收",
        4 : "器械送到急診室",
        5 : "充電"
    }
    return work.get(num, None)

def return_flag_to_str(num):
    return_flag = {
        0 : "工作未完成",
        1 : "工作完成"
    }
    return return_flag.get(num, None)

def encapsule_rtn_format(update_kv_map, remove_kv_map):
    rtn_obj = {
                "status_code": 0,
                "msg_response": {}
            }
    if update_kv_map is not None:
        rtn_obj['msg_response']['update'] = update_kv_map
    if remove_kv_map is not None:
        rtn_obj['msg_response']['remove'] = remove_kv_map
    return rtn_obj