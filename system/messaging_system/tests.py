from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_302_FOUND

from messaging_system.models import Message


# Create your tests here.
class TestMessageViews( TestCase ):

    def create_user_and_login( self, username, password ):
        user = User.objects.create_user( username=username, password=password )
        client = Client()
        response = client.post( "/rest-auth/login/", {'username': username, 'password':password} )
        self.assertTrue( any( [HTTP_200_OK == response.status_code,
                              HTTP_302_FOUND == response.status_code] ) )
        return client, user
        self.assertTrue( self.client.login( username=username, password=password ) )

    def write_msg_from_sender_to_receiver( self, sender, receiver ):
        post_data = {"username":receiver, 'subject':'test_subject', 'msg':'kuku'}
        response = sender.post( self.write_message_url, post_data )
        if type( response.data ) is int:
            self.client_user[receiver]["msg_ids"].append( response.data )
        return response

    def setUp( self ):
        self.write_message_url = reverse( 'write_message' )
        self.get_all_messages_url = reverse( 'get_all_messages' )
        self.get_all_unread_messages_url = reverse( 'get_all_unread_messages' )
        self.read_message_url = reverse( "read_message" )
        self.delete_message_url = reverse( "delete_message" )
        TestCase.setUp( self )
        self.client_user = {}
        for username, password in {"client1":"client1", "client2":"client2", "client3":"client3"}.items():
            client, user = self.create_user_and_login( username, password )
            self.client_user[username] = {"client":client, "user":user, "msg_ids":[]}

        self.write_msg_from_sender_to_receiver( sender=self.client_user["client1"]["client"],
                                                receiver=self.client_user["client2"]["user"].username )
        self.write_msg_from_sender_to_receiver( sender=self.client_user["client2"]["client"],
                                                receiver=self.client_user["client3"]["user"].username )
        self.write_msg_from_sender_to_receiver( sender=self.client_user["client1"]["client"],
                                                receiver=self.client_user["client3"]["user"].username )

    def test_write_message( self ):
        self.assertEqual( Message.objects.count(), 3 )
        self.assertEqual( Message.objects.filter( receiver__username="client3" ).count(), 2 )
        response = self.write_msg_from_sender_to_receiver( sender=self.client_user["client1"]["client"],
                                                         receiver="kuku" )
        self.assertEqual( response.status_code, status.HTTP_400_BAD_REQUEST )
        self.assertEqual( response.data, "User does not exist" )
        self.assertEqual( Message.objects.count(), 3 )

    def test_get_all_messages_for_a_specific_user( self ):
        msgs_of_user3 = self.client_user["client3"]["client"].get( self.get_all_messages_url )
        self.assertEqual( len( msgs_of_user3.data ), 2 )
        self.assertTrue( msgs_of_user3.data[0]["owner"] in  ["client1", "client2"] )
        self.assertFalse( msgs_of_user3.data[0]["is_read"] )
        msgs_of_user1 = self.client_user["client1"]["client"].get( self.get_all_messages_url )
        self.assertEqual( len( msgs_of_user1.data ), 0 )

    def get_all_unread_messages( self ):
        msgs_of_user2 = self.client_user["client2"]["client"].get( self.get_all_unread_messages_url )
        self.assertEqual( len( msgs_of_user2.data ), 1 )
        self.assertFalse( msgs_of_user2.data[0]["is_read"] )
        msgs_of_user1 = self.client_user["client1"]["client"].get( self.get_all_unread_messages_url )
        self.assertFalse( len( msgs_of_user1.data ) )

    def test_read_message( self ):
        post_data = {"id":self.client_user["client2"]["msg_ids"][0]}
        client2_msg = self.client_user["client2"]["client"].post( self.read_message_url, post_data )
        client2_msg = client2_msg.data
        self.assertTrue( client2_msg["is_read"] )
        post_data = {"id":99}
        client2_msg = self.client_user["client2"]["client"].post( self.read_message_url, post_data )
        client2_msg = client2_msg.data
        self.assertEqual( client2_msg, {} )
        post_data = {"id":None}
        client2_msg = self.client_user["client2"]["client"].post( self.read_message_url, post_data )
        client2_msg = client2_msg.data
        self.assertEqual( client2_msg, {} )

    def test_delete_message( self ):
        post_data = {"id":self.client_user["client3"]["msg_ids"][0]}
        resp = self.client_user["client1"]["client"].post( self.delete_message_url, post_data )
        self.assertEqual( resp.data, {} )
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        post_data = {"id":self.client_user["client2"]["msg_ids"][0]}
        resp = self.client_user["client1"]["client"].post( self.delete_message_url, post_data )
        self.assertEqual( resp.data, status.HTTP_200_OK )
        post_data = {"id":self.client_user["client3"]["msg_ids"][0]}
        resp = self.client_user["client3"]["client"].post( self.delete_message_url, post_data )
        self.assertEqual( resp.data, status.HTTP_200_OK )

    def tearDown( self ):
        for client in self.client_user.values():
            client['client'].logout()
            client['user'].delete()
        self.assertEqual( Message.objects.count(), 0 )
        