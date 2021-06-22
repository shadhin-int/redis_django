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
        key = list(item.key())[0]
        value = item[key]
        redis_instance.set(key, value)
        response = {
            'message': f"{key} successfully set to {value}"
        }