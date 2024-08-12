from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import *
# from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
import json

# class ChatroomConsumer(WebsocketConsumer):
    
#     def connect(self):
#         self.user = self.scope['user']
#         self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name'] 
#         # print("what is here----------", self.scope['url_route']['kwargs']['chatroom_name'])
#         self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        
#         async_to_sync(self.channel_layer.group_add)(
#             self.chatroom_name, self.channel_name
#         )
        
#         self.accept()
        
#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.chatroom_name, self.channel_name
#         )
        
        
#     def receive(self, text_data=None, bytes_data=None):
        
#         text_data_json = json.loads(text_data)
#         # print("is it really data+++++++++++++++" , text_data_json)
#         body = text_data_json['body']
        
#         message = GroupMessage.objects.create(
#             body = body,
#             author = self.user,
#             group = self.chatroom
#         )
        
#         event = {
#             'type': 'message_handler',
#             'message_id': message.id,
#         }
        
#         async_to_sync(self.channel_layer.group_send)(
#             self.chatroom_name, event
#         )
        
#     def message_handler(self, event):
#         message_id = event['message_id']
#         message = GroupMessage.objects.get(id=message_id)
#         context = {
#             'message': message,
#             'user': self.user,
#             'chat_group': self.chatroom
#         }
#         html = render_to_string("a_rtchat/partials/chat_message_p.html", context=context)
#         self.send(text_data=html)



#---------------------------------------------------------------------------------
class ChatroomConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        #getting login user
        self.user = self.scope['user']
        print("Login User+++++++++++", self.user)
        
        #getting chatroom name (public chat)
        #it can be static or dynamic
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        print("chat group name +++++++++++", self.chatroom_name)
        
        #convert sync funtion to async (get_object_or_404 is sync funtion)
        #match chat group name with chat message model
        self.chatroom = await sync_to_async(get_object_or_404)(ChatGroup, group_name=self.chatroom_name)
        print("chat model name +++++++++++", self.chatroom)
        
        #group add with channel layer
        await self.channel_layer.group_add(self.chatroom_name, self.channel_name)
        print("layer information",self.channel_name)
        
        #accept the connection
        await self.accept()
    
    
    #function for disconnect    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chatroom_name, self.channel_name)
    
    
    #function for receive data    
    async def receive(self, text_data=None, bytes_data=None):
        #receive data and convert data to python dictionary
        text_data_json = json.loads(text_data)
        print("convert data", text_data_json)
        #get only data
        body = text_data_json['body']
        
        #save message to message model and also convert it sync to async function
        message = await sync_to_async(GroupMessage.objects.create)(
            body=body,
            author=self.user,
            group=self.chatroom
        )
        
        
        #event for handling data (passing two parameter as dictionary)
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        
        #send chat room name and event object to channel layer
        await self.channel_layer.group_send(
            self.chatroom_name, 
            event
        )
    
    #get data in event and this function called from event dictionary    
    async def message_handler(self, event):
        #get every message id
        message_id = event['message_id']
        print("message id-----", message_id)
        #convert function
        message = await sync_to_async(GroupMessage.objects.get)(id=message_id)
        
        # context to pass html
        context = {
            'message': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        
        #render to string html also this render_to_string is sync, so convert async
        html = await sync_to_async(render_to_string)("a_rtchat/partials/chat_message_p.html", context=context)
        #called send function to send html
        await self.send(text_data=html)

