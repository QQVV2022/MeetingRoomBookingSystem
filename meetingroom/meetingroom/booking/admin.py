from django.contrib import admin
from .models import UserInfo, Booking, Room

class BookingAdmin(admin.ModelAdmin):
    # https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/
    list_display = ('user', 'room', 'date','time_id')

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Room)
