from django.core.urlresolvers import reverse
from cyder.base.constants import ACTION_UPDATE
from cyder.base.helpers import cached_property


class Tablefier:
    def __init__(self, objects, request=None, extra_cols=None,
                 users=False, custom=None, update=True):
        if users:
            from cyder.core.cyuser.models import UserProfile
            objects = UserProfile.objects.filter(user__in=objects)

        self.objects = objects
        self.request = request
        self.custom = custom
        if self.custom:
            self.extra_cols = None
            self.update = False
        else:
            self.extra_cols = extra_cols
            self.update = update

    @cached_property
    def profile(self):
        if self.request:
            return self.request.user.get_profile()
        else:
            return None

    @cached_property
    def first_obj(self):
        return self.objects[0]

    @cached_property
    def klass(self):
        try:
            klass = self.objects.object_list.model
        except AttributeError:
            klass = self.first_obj.__class__
        return klass

    @cached_property
    def can_update(self):
        if (self.profile and self.profile.has_perm(
                self.request, ACTION_UPDATE, obj_class=self.klass) and
                hasattr(self.klass, 'get_update_url') and self.update):
            return True
        return False

    @cached_property
    def views(self):
        if self.custom:
            return False

        views = hasattr(self.first_obj, 'views')
        return views

    @cached_property
    def headers(self):
        headers = []
        if self.custom:
            data = self.custom(self.first_obj)['data']
        else:
            data = self.first_obj.details()['data']

        for title, sort_field, value in data:
            headers.append([title, sort_field])

        if self.views:
            headers.append(['Views', None])
            if hasattr(self.objects, 'object_list'):
                self.objects.object_list = (
                    self.objects.object_list.prefetch_related('views'))

        if self.extra_cols:
            for col in self.extra_cols:
                headers.append([col['header'], col['sort_field']])

        if self.can_update:
            headers.append(['Actions', None])

        if hasattr(self.objects, 'object_list'):
            self.objects.object_list = (self.objects.object_list
                .select_related(*[f for _, f in headers if f]))

        if self.add_info:
            headers.insert(0, ['Info', None])

        return headers

    @cached_property
    def add_info(self):
        return bool(self.grab_url(self.first_obj))

    @staticmethod
    def grab_url(value):
        try:
            if type(value) in [str, unicode]:
                from cyder.cydhcp.range.utils import find_range
                value = find_range(value)
            return value.get_detail_url()
        except (AttributeError, ValueError):
            return None

    def build_data(self, obj, value):
        if self.add_info and value == obj:
            col = {'value': [unicode(value)], 'url': [None]}
        else:
            col = {'value': [unicode(value)], 'url': [self.grab_url(value)]}
        return col

    @staticmethod
    def build_extra(d):
        data_fields = ['value', 'url', 'img', 'class']
        if not isinstance(d['value'], list):
            for k, v in d.items():
                d[k] = [v]
        col = dict(filter(lambda (k, v): k in data_fields, d.items()))
        return col

    @staticmethod
    def build_view_field(obj):
        view_field = None
        if hasattr(obj, 'views'):
            for view in obj.views.all():
                if view_field:
                    view_field += ' ' + view.name
                else:
                    view_field = view.name
            col = {'value': [view_field], 'url': [None]}
        else:
            col = {'value': ['None'], 'url': [None]}
        return col

    def build_update_field(self, obj):
        if self.profile and self.profile.has_perm(self.request, ACTION_UPDATE,
                                                  obj=obj):
            col = {'value': ['Update', 'Delete'],
                   'url': [obj.get_update_url(), obj.get_delete_url()],
                   'data': [[('pk', obj.id),
                             ('objName', obj.pretty_name),
                             ('objType', obj._meta.db_table),
                             ('getUrl', reverse('get-update-form')),
                             ('prettyObjType', obj.pretty_type)],
                            [('kwargs', '{"obj_type": "'
                             + str(obj._meta.db_table)
                             + '", "pk": "' + str(obj.id) + '"}')]],
                   'class': ['update', 'delete'],
                   'img': ['/media/img/update.png', '/media/img/delete.png']}
        else:
            col = {'value': []}

        return col

    def get_data(self):
        objs, data, urls = [], [], []
        if self.extra_cols:
            extra_datas = zip(*[col['data'] for col in self.extra_cols])
        else:
            extra_datas = [[]] * len(self.objects)

        for obj, extra_data in zip(self.objects, extra_datas):
            row_data = []
            if self.add_info:
                row_data.append({
                    'value': ['Info'], 'url': [self.grab_url(obj)],
                    'class': ['info'], 'img': ['/media/img/magnify.png']})

            details = self.custom(obj) if self.custom else obj.details()
            for title, field, value in details['data']:
                row_data.append(self.build_data(obj, value))

            if self.views:
                row_data.append(self.build_view_field(obj))

            for d in extra_data:
                row_data.append(self.build_extra(d))

            if self.can_update:
                row_data.append(self.build_update_field(obj))

            objs.append(obj)
            data.append(row_data)
            urls.append(details['url'])

        return objs, data, urls

    def get_table(self):
        if not self.objects:
            return None

        self.headers  # generate headers first to select related objects
        objs, data, urls = self.get_data()
        return {
            'headers': self.headers,
            'postback_urls': urls,
            'data': data,
        }
