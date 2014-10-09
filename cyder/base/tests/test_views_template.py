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
            server = random_label()
            return {'server': server, 'domain':self.domain.pk}
    """
    def get_tests(self):
        return (
            self.test_filter(),
            self.test_list_get(),
            self.test_create_post_guest(),
            self.test_create_post_user(),
            self.test_create_post_admin(),
            self.test_create_post_superuser(),
            self.test_update_post_guest(),
            self.test_update_post_user(),
            self.test_update_post_admin(),
            self.test_update_post_superuser(),
            self.test_delete_post_guest(),
            self.test_delete_post_user(),
            self.test_delete_post_admin(),
            self.test_delete_post_superuser(),
            self.test_detail_get(),
            self.test_table_update_post(),
            lambda junk: True
        )

    def get_helpers(self):
        return (
            self.has_perm(),
            self.do_create(),
            self.do_update(),
            self.do_delete(),
        )

    def has_perm(self):
        def has_perm(self, user, action):
            if action == ACTION_CREATE:
                return _has_perm(user, Ctnr.objects.get(name='test_ctnr'),
                                 action=action, obj_class=self.test_class)
            elif action in (ACTION_UPDATE, ACTION_DELETE):
                return _has_perm(user, Ctnr.objects.get(name='test_ctnr'),
                                 action=action, obj=self.test_obj)
        return has_perm

    def do_create(self):
        def do_create(self, username='test_superuser'):
            self.client.login(username=username, password='password')

            count = self.test_class.objects.count()
            res = self.client.post(self.test_class.get_create_url(),
                                   self.post_data(), follow=True)

            self.assertTrue(res.status_code in (302, 200),
                            u'Response code %s\n' % res.status_code +
                            format_response(res))

            if not self.has_perm(User.objects.get(username=username),
                                 ACTION_CREATE):
                # Nothing should be created if no permissions.
                self.assertEqual(
                    self.test_class.objects.count(), count,
                    u'Should not have been able to create as %s' % username)
            else:
                # Check object was created.
                self.assertTrue(res.status_code in (302, 200),
                                u'Response code %s\n' % res.status_code +
                                format_response(res))
                self.assertTrue(self.test_class.objects.count() > count,
                                u'Could not create as %s\n' % username +
                                format_response(res))
        return do_create

    def do_update(self):
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
        return do_update

    def do_delete(self):
        def do_delete(self, username='test_superuser'):
            self.client.login(username=username, password='password')
            has_perm = self.has_perm(User.objects.get(username=username),
                                     ACTION_DELETE)

            count = self.test_class.objects.count()
            res = self.client.post(
                self.test_obj.get_delete_url(),
                {'follow': True, 'pk': self.test_obj.id,
                 'obj_type': self.test_obj._meta.db_table})

            self.assertTrue(res.status_code in (302, 200),
                            'Response code %s' % res.status_code +
                            format_response(res))

            if has_perm:
                self.assertTrue(
                    self.test_class.objects.count() < count,
                    'Object was not deleted')
            else:
                self.assertEqual(
                    self.test_class.objects.count(), count,
                    'Object was not supposed to be deleted')
        return do_delete

    def test_filter(self):
        def test_filter(self):
            url = self.test_class.get_list_url()
            query = random_label()
            url = "{0}?filter={1}".format(url, query)
            resp = self.client.get(url, follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_filter

    def test_list_get(self):
        """List view."""
        def test_list_get(self):
            resp = self.client.get(self.test_class.get_list_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_list_get

    def test_create_post_guest(self):
        """Create view, guest."""
        def test_create_post_guest(self):
            self.do_create('test_guest')
        return test_create_post_guest

    def test_create_post_user(self):
        """Create view, user."""
        def test_create_post_user(self):
            self.do_create('test_user')
        return test_create_post_user

    def test_create_post_admin(self):
        """Create view, admin."""
        def test_create_post_admin(self):
            self.do_create('test_admin')
        return test_create_post_admin

    def test_create_post_superuser(self):
        """Create view, superuser."""
        def test_create_post_superuser(self):
            self.do_create('test_superuser')
        return test_create_post_superuser

    def test_update_post_guest(self):
        """Update view, guest."""
        def test_update_post_guest(self):
            self.do_update('test_guest')
        return test_update_post_guest

    def test_update_post_user(self):
        """Update view, user."""
        def test_update_post_user(self):
            self.do_update('test_user')
        return test_update_post_user

    def test_update_post_admin(self):
        """Update view, admin."""
        def test_update_post_admin(self):
            self.do_update('test_admin')
        return test_update_post_admin

    def test_update_post_superuser(self):
        """Update view, superuser."""
        def test_update_post_superuser(self):
            self.do_update('test_superuser')
        return test_update_post_superuser

    def test_delete_post_guest(self):
        """Delete view, guest."""
        def test_delete_post_guest(self):
            self.do_delete('test_guest')
        return test_delete_post_guest

    def test_delete_post_user(self):
        """Delete view, user."""
        def test_delete_post_user(self):
            self.do_delete('test_user')
        return test_delete_post_user

    def test_delete_post_admin(self):
        """Delete view, admin."""
        def test_delete_post_admin(self):
            self.do_delete('test_admin')
        return test_delete_post_admin

    def test_delete_post_superuser(self):
        """Delete view, superuser."""
        def test_delete_post_superuser(self):
            self.do_delete('test_superuser')
        return test_delete_post_superuser

    def test_detail_get(self):
        """Detail view."""
        def test_detail_get(self):
            resp = self.client.get(self.test_obj.get_detail_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_detail_get

    def test_table_update_post(self):
        """Table update view, post."""
        def test_table_update_post(self):
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
        return test_table_update_post


def build(tests):
    """
    Attaches test methods and helper functions to test classes.
    """
    builder = GenericViewTests()
    for test in tests:
        for generic_test in builder.get_tests():
            # Set name of test.
            setattr(test, generic_test.__name__ + '_' + test.name,
                    generic_test)
        for helper in builder.get_helpers():
            setattr(test, helper.__name__, helper)


def random_label():
    """
    Utility function to generate a random *valid* label.
    """
    label = ''
    for i in range(random.randint(5, 30)):
        label += string.letters[random.randint(0, len(string.letters) - 1)]
    return label


def random_byte():
    """
    Utility function to generate a random byte for random IPs
    """
    return random.randint(0, 255)


def format_response(response):
    response = response.content.decode('utf_8').splitlines()
    if len(response) > 3:
        response = response[:3] + [u'...']
    response = u'Response:\n' + u'\n'.join(response)
    return response
