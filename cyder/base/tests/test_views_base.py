import random
import string
from itertools import dropwhile

from cyder.base.constants import ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE
from cyder.core.ctnr.models import Ctnr
from cyder.core.cyuser.backends import _has_perm
from cyder.core.cyuser.models import User


class GenericViewTests(object):
    """
    Builds test funtions. Need to define a setUp function.

    Also requires post_data to generate test view POST data:

        def post_data(self):
            return {'server': 'foobie.bletch', 'domain':self.domain.pk}
    """
    def has_perm(self, user, action):
        if action == ACTION_CREATE:
            return _has_perm(user, Ctnr.objects.get(name='test_ctnr'),
                             action=action, obj_class=self.model)
        elif action in (ACTION_UPDATE, ACTION_DELETE):
            return _has_perm(user, Ctnr.objects.get(name='test_ctnr'),
                             action=action, obj=self.test_obj)

    def do_create(self, username='test_superuser'):
        self.client.login(username=username, password='password')

        count = self.model.objects.count()
        res = self.client.post(self.model.get_create_url(),
                               self.post_data(), follow=True)

        self.assertTrue(res.status_code in (302, 200),
                        u'Response code %s\n' % res.status_code +
                        format_response(res))

        if not self.has_perm(User.objects.get(username=username),
                             ACTION_CREATE):
            # Nothing should be created if no permissions.
            self.assertEqual(
                self.model.objects.count(), count,
                u'Should not have been able to create as %s' % username)
        else:
            # Check object was created.
            self.assertTrue(res.status_code in (302, 200),
                            u'Response code %s\n' % res.status_code +
                            format_response(res))
            self.assertTrue(self.model.objects.count() > count,
                            u'Could not create as %s\n' % username +
                            format_response(res))

    def do_update(self, username='test_superuser'):
        self.client.login(username=username, password='password')
        has_perm = self.has_perm(User.objects.get(username=username),
                                 ACTION_UPDATE)

        post_data = self.post_data()
        res = self.client.post(self.test_obj.get_update_url(),
                               post_data, follow=True)

        self.assertTrue(res.status_code in (302, 200),
                        u'Response code %s' % res.status_code +
                        format_response(res))

        test_obj = self.test_obj.__class__.objects.get(id=self.test_obj.id)
        if has_perm:
            # Check that the attributes we posted updated the object.
            for k, v in post_data.items():
                if k not in ['domain', 'label']:
                    obj_val = getattr(test_obj, k)
                    if hasattr(obj_val, 'id'):
                        self.assertEqual(
                            obj_val.id, v,
                            'The "%s" field was not updated' % k)
                    else:
                        self.assertEqual(
                            str(obj_val), str(v),
                            'The "%s" field was not updated' % k)
        else:
            # Check nothing has changed.
            for k, v in post_data.items():
                if k not in ['domain', 'label']:
                    self.assertEqual(
                        getattr(self.test_obj, k), getattr(test_obj, k),
                        '%s changed but was not supposed to' % k)

    def do_delete(self, username='test_superuser'):
        self.client.login(username=username, password='password')
        has_perm = self.has_perm(User.objects.get(username=username),
                                 ACTION_DELETE)

        count = self.model.objects.count()
        res = self.client.post(
            self.test_obj.get_delete_url(),
            {'follow': True, 'pk': self.test_obj.id,
             'obj_type': self.test_obj._meta.db_table})

        self.assertTrue(res.status_code in (302, 200),
                        'Response code %s' % res.status_code +
                        format_response(res))

        if has_perm:
            self.assertTrue(
                self.model.objects.count() < count,
                'Object was not deleted')
        else:
            self.assertEqual(
                self.model.objects.count(), count,
                'Object was not supposed to be deleted')

    def test_filter(self):
        url = self.model.get_list_url()
        query = 'fakeyfake'
        url = "{0}?filter={1}".format(url, query)
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_list_get(self):
        """List view."""
        resp = self.client.get(self.model.get_list_url(),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_create_post_guest(self):
        """Create view, guest."""
        self.do_create('test_guest')

    def test_create_post_user(self):
        """Create view, user."""
        self.do_create('test_user')

    def test_create_post_admin(self):
        """Create view, admin."""
        self.do_create('test_admin')

    def test_create_post_superuser(self):
        """Create view, superuser."""
        self.do_create('test_superuser')

    def test_update_post_guest(self):
        """Update view, guest."""
        self.do_update('test_guest')

    def test_update_post_user(self):
        """Update view, user."""
        self.do_update('test_user')

    def test_update_post_admin(self):
        """Update view, admin."""
        self.do_update('test_admin')

    def test_update_post_superuser(self):
        """Update view, superuser."""
        self.do_update('test_superuser')

    def test_delete_post_guest(self):
        """Delete view, guest."""
        self.do_delete('test_guest')

    def test_delete_post_user(self):
        """Delete view, user."""
        self.do_delete('test_user')

    def test_delete_post_admin(self):
        """Delete view, admin."""
        self.do_delete('test_admin')

    def test_delete_post_superuser(self):
        """Delete view, superuser."""
        self.do_delete('test_superuser')

    def test_detail_get(self):
        """Detail view."""
        resp = self.client.get(self.test_obj.get_detail_url(),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_table_update_post(self):
        """Table update view, post."""
        post_data = self.post_data()
        resp = self.client.post(self.test_obj.get_table_update_url(),
                                post_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Check that the attributes we posted updated the object, if they
        # were set to be editable.
        editable_attrs = [md['name'] for md in
                          self.test_obj.eg_metadata()['metadata']
                          if md['editable']]
        test_obj = self.test_obj.__class__.objects.get(id=self.test_obj.id)
        for k, v in post_data.items():
            if k in editable_attrs and k not in ['fqdn', 'label']:
                obj_val = getattr(test_obj, k)
                if hasattr(obj_val, 'id'):
                    self.assertEqual(obj_val.id, v)
                else:
                    self.assertEqual(str(obj_val), str(v))


def format_response(response):
    response = response.content.decode('utf_8').splitlines()
    if len(response) > 3:
        response = response[:3] + [u'...']
    response = u'Response:\n' + u'\n'.join(response)
    return response
