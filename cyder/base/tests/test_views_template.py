import random
import string

from nose.tools import eq_


class GenericViewTests(object):
    """
    An object that builds test funtions.
    You need to define a setUp function like this.
    def setUp(self):
        # A name of domain to use when creating records
        dname = "food"
        self.domain, create = Domain.objects.get_or_create(name=dname)
        while not create: # This ensures that a domain is created.
            dname = "a"+dname
            self.domain, create = Domain.objects.get_or_create(name=dname)

        # Make a generic test "object". This object is called self.test_obj and
        # is used to test datail and update views
        server = "random"
        self.test_obj, create = Nameserver.objects.get_or_create(
            server=server, domain= self.domain)
        while not create:
            server = "a"+server
            self.test_obj, create = Nameserver.objects.get_or_create(
                server=server, domain= self.domain)

    This function is used to generate valid data to test views that require
    POST data.

        def post_data(self):
            server = random_label()
            return {'server': server, 'domain':self.domain.pk}
    """
    def get_tests(self):
        return (
            self.test_list_get(),
            self.test_create_post(),
            self.test_update_post(),
            self.test_delete_post(),
            self.test_detail_get(),
            self.test_table_update_post(),
            lambda junk: True
        )

    def get_helpers(self):
        return (
            self.do_create(),
        )

    def do_create(self):
        def do_create(self):
            return self.client.post(self.test_class.get_create_url(),
                                    self.post_data(), follow=True)
        return do_create

    def test_list_get(self):
        """List view."""
        def test_list_get(self):
            resp = self.client.get(self.test_class.get_list_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_list_get

    def test_create_post(self):
        """Create view."""
        def test_create_post(self):
            count = self.test_class.objects.count()
            resp = self.do_create()
            self.assertTrue(resp.status_code in (302, 200))
            self.assertTrue(self.test_class.objects.count() > count)
        return test_create_post

    def test_update_post(self):
        """Update view, post."""
        def test_update_post(self):
            post_data = self.post_data()
            resp = self.client.post(self.test_obj.get_update_url(),
                                    post_data, follow=True)
            self.assertTrue(resp.status_code in (302, 200))

            # Check that the attributes we posted updated the object.
            test_obj = self.test_obj.__class__.objects.get(id=self.test_obj.id)
            for k, v in post_data.items():
                if k not in ['fqdn', 'label']:
                    obj_val = getattr(test_obj, k)
                    if hasattr(obj_val, 'id'):
                        eq_(obj_val.id, v)
                    else:
                        eq_(str(obj_val), str(v))

        return test_update_post

    def test_delete_post(self):
        """Delete view."""
        def test_delete_post(self):
            count = self.test_class.objects.count()
            resp = self.client.post(self.test_obj.get_delete_url(),
                                    follow=True)
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(self.test_class.objects.count() < count)
        return test_delete_post

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
            eq_(resp.status_code, 200)

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
                        eq_(obj_val.id, v)
                    else:
                        eq_(str(obj_val), str(v))
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
