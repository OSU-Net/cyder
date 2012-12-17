from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydns.domain.models import Domain


ctnr = Ctnr.objects.get(id=1)

domains = Domain.objects.filter(id__lte=3)
for domain in domains:
    ctnr.domains.add(domain)

user = User.objects.get(username='development')
ctnr_user = CtnrUser(id=None, ctnr=ctnr, user=user, level=2)
ctnr_user.save()

ctnr.save()
