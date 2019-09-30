from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from messaging_system.models import Message
from messaging_system.serializers import MessageSerializer


# Create your views here.
class WriteMessage( APIView ):
    permission_classes = ( IsAuthenticated, )

    def post( self, request ):
        data = request.data
        try:
            receiver = User.objects.get( username=data['username'] )
        except ObjectDoesNotExist :
            return Response( "User does not exist", status.HTTP_400_BAD_REQUEST )
        sender = User.objects.get( username=request.user.username )
        message = Message.objects.create( subject=data.get( 'subject', '' ), msg=data.get( 'msg', '' ), sender=sender, receiver=receiver )
        return Response( message.id, status.HTTP_200_OK )


class GetAllMessages( APIView ):
    permission_classes = ( IsAuthenticated, )

    def get( self, request ):
        messages = [MessageSerializer( msg ).data for msg in Message.objects.filter( receiver=request.user )]
        return Response( messages, status.HTTP_200_OK )


class GetAllUnreadMessages( APIView ):
    permission_classes = ( IsAuthenticated, )

    def get( self, request ):
        messages = [MessageSerializer( msg ).data for msg in Message.objects.filter( receiver=request.user, is_read=False )]
        return Response( messages, status.HTTP_200_OK )


class ReadMessage( APIView ):
    permission_classes = ( IsAuthenticated, )

    def post( self, request ):
        data = request.data
        try:
            msg = Message.objects.get( id=data.get( 'id' ) )
        except:
            return Response( {}, status.HTTP_400_BAD_REQUEST )
        msg.is_read = True
        msg.save()
        return Response( MessageSerializer( msg ).data, status.HTTP_200_OK )


class DeleteMessage( APIView ):
    permission_classes = ( IsAuthenticated, )

    def post( self, request ):
        data = request.data
        try:
            Message.objects.get( Q( sender__username=request.user ) | Q( receiver__username=request.user ), id=data.get( 'id' ) ).delete()
        except:
            return Response( {}, status.HTTP_400_BAD_REQUEST )
        return Response( status.HTTP_200_OK )
