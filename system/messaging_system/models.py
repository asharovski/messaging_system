from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Message( models.Model ):
    is_read = models.BooleanField( default=False )
    msg = models.TextField( null=True, blank=True )
    subject = models.TextField( null=True, blank=True )
    creation_date = models.DateTimeField( auto_now_add=True )
    sender = models.ForeignKey( User, on_delete=models.CASCADE, related_name='sends' )
    receiver = models.ForeignKey( User, on_delete=models.CASCADE, related_name='received' )

    class Meta:
        app_label = "messaging_system"
        verbose_name = 'Message'
        verbose_name_plural = 'Message'
        db_table = "message"

    def __str__( self ):
        return '%s' % ( self.msg )