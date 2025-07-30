from django.contrib import admin
from .models import Contact
from .models import Cause
from .models import Donation


admin.site.register(Contact)

admin.site.register(Cause)

admin.site.register(Donation)
