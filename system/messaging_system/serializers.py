'''
Created on 30 Sep 2019

@author: alex
'''

from messaging_system.models import Message
from rest_framework import serializers


class MessageSerializer( serializers.ModelSerializer ):
    owner = serializers.ReadOnlyField( source='sender.username' )

    class Meta:
        model = Message
        fields = ( 'owner', 'msg', 'subject', 'is_read' )
