def range_usage_get_create(Klass, **kwargs):
    created = False
    try:
        obj = Klass.objects.get(**kwargs)
    except Klass.DoesNotExist:
        obj = Klass(**kwargs)
        created = True

    obj.save(**{'update_range_usage': False})
    return obj, created
