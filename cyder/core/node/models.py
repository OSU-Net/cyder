from django.db import models
from cyder.core.ctnr.models import Ctnr

class Node( models.Model ):
    id              = models.AutoField(primary_key=True)
    ctnr           = models.ForeignKey(Ctnr, null=False)

    class Meta:
        db_table = 'node'
