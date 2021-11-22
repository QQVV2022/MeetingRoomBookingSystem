from django.db import models


# Create your models here.
from django.contrib.auth.models import User

class UserInfo(User):
    phone = models.CharField(max_length=32)
    def __str__(self):
        return self.username


class Room(models.Model):
    """
    Meeting Room
    """
    roomname = models.CharField(max_length=32)
    num = models.IntegerField()  # number of holding

    def __str__(self):
        return self.roomname


class Booking(models.Model):
    """
    Meeting room booking info
    """
    time_choice = (
        (1,'8:00'),
        (2,'8:30'),
        (3,'9:00'),
        (4,'9:30'),
        (5,'10:00'),
        (6,'10:30'),
        (7,'11:00'),
        (8,'11:30'),
        (9,'12:00'),
        (10,'12:30'),
        (11,'13:00'),
        (12,'13:30'),
        (13,'14:00'),(14,'14:30'),(15,'15:00'),
        (16,'15:30'),
        (17,'16:00'),
        (18,'16:30'),
        (19,'17:00'),
        (20,'17:30'),
        (21,'18:00'),
        (22,'18:30'),
        (23,'19:00'),
        (24,'19:30'),
        (25,'20:00')

    )

    user = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    date = models.DateField()
    time_id = models.IntegerField(choices=time_choice)

    class Meta:
        # unique_together = (
        #     ('room','date','time_id'),
        # )
        # https://stackoverflow.com/questions/2201598/how-to-define-two-fields-unique-as-couple
        constraints = [
            models.UniqueConstraint(fields=['room','date','time_id'], name='unique_booking')
        ]

    def __str__(self):
        return str(self.user)+' has booked '+str(self.room)

