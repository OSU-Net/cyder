from django.db import models
from cyder.core.ctnr import Ctnr

class Node( models.Model ):
    id              = models.AutoField(primary_key=True)
    ctnr           = models.ForeignKey(Ctnr, null=False)

