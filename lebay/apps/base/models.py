import datetime
from django.db import models

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(default=datetime.datetime.now)
    time_modified = models.DateTimeField(default=datetime.datetime.now)

    def save(self, force_insert=False, force_update=False):
        self.time_modified = datetime.datetime.now()
        super(BaseModel, self).save(force_insert=False, force_update=False)

    class Meta:
        abstract = True
    