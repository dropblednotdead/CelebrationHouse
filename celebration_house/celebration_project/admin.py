from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserInformation)
admin.site.register(Zones)
admin.site.register(Locations)
admin.site.register(Regions)
admin.site.register(Services)
admin.site.register(Booking)
admin.site.register(BookingServices)
admin.site.register(RegionTypes)