from django.http import response
from django.shortcuts import render
import json
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework import request


# Connect to redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


@api_view(['GET', 'POST'])
def manage_items(request, *args, **kwargs):
    if request.method == 'GET':
        items = {}
        count = 0
        for key in redis_instance.keys("*"):
            items[key.decode("utf-8")] = redis_instance.get(key)
            count+=1
        response ={
            'count': count,
            'message': f"Found {count} items.",
            'items': items
        }
        return Response(response, status=200)
    elif request.method == 'POST':
        item = json.loads(request.body)
        print(item, "------------------->")
        key = list(item.key())
        print(key, "-------------------->")
        value = item[key]
        redis_instance.set(key, value)
        response = {
            'message': f"{key} successfully set to {value}"
        }

@api_view(['GET', 'PUT', 'DELETE'])
def manage_item(request, *args, **kwargs):
    if request.method == 'GET':
        if kwargs['key']:
            value = redis_instance.get(kwargs['key'])
            if value:
                response = {
                    'key': kwargs['key'],
                    'value': value,
                    'message': 'Success'
                }
                return Response(response, status=200)
            else:
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'message': 'Not found!'
                }
                return Response(response, status=404)
    elif request.method == 'PUT':
        if kwargs['key']:
            request_data = json.loads(request.body)
            new_value = request_data['new_value']
            value = redis_instance.get(kwargs['key'])
            if value:
                redis_instance.set(kwargs['key'], new_value)
                response = {
                    'key': kwargs['key'],
                    'value': value,
                    'message': f"Successfully upadted {kwargs['key']}"
                }
                return Response(response, status=200)
            else:
                response = {
                    'key': kwargs['key'],
                    'value': None,
                    'message': 'Not Found'
                }
                return Response(response, status=404)
            
    elif request.method == 'DELETE':
        if kwargs['key']:
            result = redis_instance.delete(kwargs['key'])
            response = {
                'message': f"{kwargs['key']} successfully deleted"
            }
            return Response(response, status=204)
        else:
            response = {
                'key': kwargs['key'],
                'value': None,
                'message': 'Not found to delete'
            }
            return Response(response, status=404)