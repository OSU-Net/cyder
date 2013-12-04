from django.db import models


class DNSManager(models.Manager):
    def get_queryset(self):
        return super(DNSManager, self).get_queryset().filter(ttype='dns')


class Task(models.Model):
    task = models.CharField(max_length=255, blank=False)
    ttype = models.CharField(max_length=255, blank=False)

    objects = models.Manager()
    dns = DNSManager()

    class Meta:
        app_label = 'cyder'
        db_table = u'task'
        ordering = ['task']

    def __repr__(self):
        return "<Task: {0}>".format(self)

    def __str__(self):
        return "{0} {1}".format(self.ttype, self.task)

    def save(self):
        super(Task, self).save()

    @staticmethod
    def schedule_zone_rebuild(soa):
        if not Task.objects.filter(task=str(soa.pk), ttype='dns').exists():
            Task(task=str(soa.pk), ttype='dns').save()
