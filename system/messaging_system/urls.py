'''
Created on 30 Sep 2019

@author: alex
'''

from django.conf.urls import url

from messaging_system.views import WriteMessage, GetAllMessages, \
    GetAllUnreadMessages, ReadMessage, DeleteMessage

urlpatterns = [
    url( r'^write_message', WriteMessage.as_view(), name='write_message' ),
    url( r'^get_all_messages', GetAllMessages.as_view(), name='get_all_messages' ),
    url( r'^get_all_unread_messages', GetAllUnreadMessages.as_view(), name='get_all_unread_messages' ),
    url( r'^read_message', ReadMessage.as_view(), name='read_message' ),
    url( r'^delete_message', DeleteMessage.as_view(), name='delete_message' ),
    ]