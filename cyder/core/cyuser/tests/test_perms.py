from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase

from cyder.base.constants import (
    ACTION_CREATE, ACTION_VIEW, ACTION_UPDATE, ACTION_DELETE)
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.views import login_session, become_user, unbecome_user
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.txt.models import TXT
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.middleware.dev_authentication import DevAuthenticationMiddleware


class AuthenticationTest(TestCase):
    fixtures = ['core/users']

    def setUp(self):
        self.setup_request()
        self.dev_middleware = DevAuthenticationMiddleware()

    def test_middleware_login_dev(self):
        """Test development middleware logs on development user"""
        self.setup_request()
        self.request.user = AnonymousUser()

        self.dev_middleware.process_request(self.request)

        self.assertNotEqual(str(self.request.user), 'AnonymousUser',
                            "")

    def test_user_profile_create(self):
        """Test that user profile is created on user creation"""
        user = User(username='user_profile_test')
        user.save()
        try:
            self.assertTrue(user.get_profile())
        except:
            self.fail("DoesNotExist: user profile was not created on "
                      "user creation")

    def test_session_has_ctnr_dev(self):
        """Test session ctnr set on log in"""
        self.setup_request()
        self.request.user = AnonymousUser()

        dev_middleware = DevAuthenticationMiddleware()
        dev_middleware.process_request(self.request)

        self.assertIn('ctnr', self.request.session)

    def test_become_user(self):
        """
        Tests the functionality to be able to become and unbecome another
        user if superuser
        """
        self.setup_request()
        self.request = login_session(self.request, 'test_superuser')

        test_new_superuser = User.objects.create(username="test_new_superuser")
        test_new_superuser.is_superuser = True
        test_new_superuser.save()

        test_new_user = User.objects.create(username='test_new_user')
        test_new_user.save()

        become_user(self.request, 'test_new_superuser')
        self.assertEqual(self.request.user.username, 'test_new_superuser')
        become_user(self.request, 'test_new_user')
        self.assertEqual(self.request.user.username, 'test_new_user')

        unbecome_user(self.request)
        self.assertEqual(self.request.user.username, 'test_new_superuser')
        unbecome_user(self.request)
        self.assertEqual(self.request.user.username, 'test_superuser')
        unbecome_user(self.request)
        self.assertEqual(self.request.user.username, 'test_superuser')

    def setup_request(self):
        """
        Utility function for flushing and setting up request object for testing
        """
        self.request = HttpRequest()
        self.request.user = AnonymousUser()
        self.request.session = SessionStore()


class PermissionsTest(TestCase):
    fixtures = ['core/users.json']

    def setUp(self):
        self.test_user = User.objects.create(username='test_user')
        self.setup_request()

        # Superuser.
        self.superuser = User.objects.get(username='test_superuser')

        # Cyder admin.
        self.cyder_admin = User.objects.create(username='cyder_admin')
        self.ctnr_global = Ctnr.objects.get(id=1)
        self.ctnr_user_cyder_admin_global = CtnrUser(
            id=None, ctnr=self.ctnr_global, user=self.cyder_admin, level=2)
        self.ctnr_user_cyder_admin_global.save()

        # Admin.
        self.ctnr_admin = Ctnr(id=None, name="admin")
        self.ctnr_admin.save()
        self.ctnr_user_admin = CtnrUser(id=None, ctnr=self.ctnr_admin,
                                        user=self.test_user, level=2)
        self.ctnr_user_admin.save()
        self.ctnr_user_cyder_admin = CtnrUser(id=None, ctnr=self.ctnr_admin,
                                              user=self.cyder_admin, level=2)
        self.ctnr_user_cyder_admin.save()

        # User.
        self.ctnr_user = Ctnr(id=None, name="user")
        self.ctnr_user.save()
        self.ctnr_user_user = CtnrUser(id=None, ctnr=self.ctnr_user,
                                       user=self.test_user, level=1)
        self.ctnr_user_user.save()

        # Guest.
        self.ctnr_guest = Ctnr(id=None, name="guest")
        self.ctnr_guest.save()
        self.ctnr_user_guest = CtnrUser(id=None, ctnr=self.ctnr_guest,
                                        user=self.test_user, level=0)
        self.ctnr_user_guest.save()

        # Pleb.
        self.pleb_user = User.objects.create(username='pleb_user')

    def test_soa_perms(self):
        """Test SOA perms"""
        self.setup_request()

        perm_table = {
            'cyder_admin': ['all'],
            'admin': [ACTION_VIEW],
            'user': [ACTION_VIEW],
            'guest': [ACTION_VIEW],
        }

        # initialize obj into ctnrs
        domain = Domain(id=None, name='foo')
        domain.save()
        obj = SOA(root_domain=domain)
        obj.primary = 'foo.bar'
        obj.contact = 'foo.gaz'
        obj.save()
        self.ctnr_admin.domains.add(domain)
        self.ctnr_user.domains.add(domain)
        self.ctnr_guest.domains.add(domain)
        self.save_all_ctnrs()

        self.check_perms_each_user(obj, perm_table)

    def test_domain_perms(self):
        """Test domain perms"""
        self.setup_request()

        perm_table = {
            'cyder_admin': [ACTION_VIEW, ACTION_UPDATE],
            'admin': [ACTION_VIEW],
            'user': [ACTION_VIEW],
            'guest': [ACTION_VIEW],
        }

        # Initialize obj into ctnrs.
        obj = Domain(id=None, name='foo')
        obj.save()
        self.ctnr_admin.domains.add(obj)
        self.ctnr_user.domains.add(obj)
        self.ctnr_guest.domains.add(obj)
        self.save_all_ctnrs()

        self.check_perms_each_user(obj, perm_table)

    def test_domain_records_perms(self):
        """Test common domain record perms (CNAME, MX, TXT, SRV, NS)"""
        self.setup_request()

        perm_table = {
            'cyder_admin': ['all'],
            'admin': ['all'],
            'user': ['all'],
            'guest': [ACTION_VIEW],
        }
        ns_perm_table = {
            'cyder_admin': ['all'],
            'admin': [ACTION_VIEW],
            'user': [ACTION_VIEW],
            'guest': [ACTION_VIEW],
        }

        # Initialize objs into ctnrs.
        domain = Domain(id=None, name='foo')
        domain.save()
        self.ctnr_admin.domains.add(domain)
        self.ctnr_user.domains.add(domain)
        self.ctnr_guest.domains.add(domain)
        self.save_all_ctnrs()
        domain_records = []
        domain_records.append(AddressRecord(domain=domain))
        domain_records.append(CNAME(domain=domain))
        domain_records.append(MX(domain=domain))
        domain_records.append(SRV(domain=domain))
        domain_records.append(TXT(domain=domain))

        self.check_perms_each_user(Nameserver(domain=domain), ns_perm_table)

        for obj in domain_records:
            self.check_perms_each_user(obj, perm_table, set_same_ctnr=True)

    def setup_request(self):
        """
        Utility function for flushing and setting up request object for testing
        """
        self.request = HttpRequest()
        self.request.user = self.test_user
        self.request.session = SessionStore()

    def save_all_ctnrs(self):
        """Utility function that simply saves all of the defined ctnrs

        Called after adding an object to each one
        """
        self.ctnr_admin.save()
        self.ctnr_user.save()
        self.ctnr_guest.save()

    def check_perms_each_user(self, obj, perm_table, set_same_ctnr=False):
        """
        Utility function for checking permissions
        """

        # Superuser.
        self.request.user = self.superuser
        self.request.session['ctnr'] = self.ctnr_guest
        if set_same_ctnr:
            obj.ctnr = self.ctnr_guest
        self.assert_perms(obj, perm_table, 'superuser')

        # Cyder admin.
        self.request.user = self.cyder_admin
        self.request.session['ctnr'] = self.ctnr_admin
        if set_same_ctnr:
            obj.ctnr = self.ctnr_admin
        self.assert_perms(obj, perm_table, 'cyder_admin')

        # Admin.
        self.request.user = self.test_user
        self.request.session['ctnr'] = self.ctnr_admin
        if set_same_ctnr:
            obj.ctnr = self.ctnr_admin
        self.assert_perms(obj, perm_table, 'admin')

        # User.
        self.request.session['ctnr'] = self.ctnr_user
        if set_same_ctnr:
            obj.ctnr = self.ctnr_user
        self.assert_perms(obj, perm_table, 'user')

        # Guest.
        self.request.session['ctnr'] = self.ctnr_guest
        if set_same_ctnr:
            obj.ctnr = self.ctnr_guest
        self.assert_perms(obj, perm_table, 'guest')

        # Pleb.
        self.request.user = self.pleb_user
        self.assert_perms(obj, perm_table, 'pleb')

    def assert_perms(self, obj, perm_table, user_level):
        """
        Utility function that gets each type of permissions for an object and
        asserts against perm table.
        """

        create_perm = self.request.user.get_profile().has_perm(
            self.request, ACTION_CREATE, obj=obj)
        view_perm = self.request.user.get_profile().has_perm(
            self.request, ACTION_VIEW, obj=obj)
        update_perm = self.request.user.get_profile().has_perm(
            self.request, ACTION_UPDATE, obj=obj)
        delete_perm = self.request.user.get_profile().has_perm(
            self.request, ACTION_DELETE, obj=obj)

        actual_perms = {
            'all': create_perm and view_perm and update_perm and delete_perm,
            ACTION_CREATE: create_perm,
            ACTION_VIEW: view_perm,
            ACTION_UPDATE: update_perm,
            ACTION_DELETE: delete_perm,
        }

        # Superuser.
        actual_perms_list = [create_perm, view_perm, update_perm, delete_perm]
        if user_level == 'superuser':
            for perm in actual_perms_list:
                self.assertTrue(perm, "Superuser should have all permissions")
            return

        # Pleb.
        if not user_level in perm_table:
            for actual_perm in actual_perms_list:
                self.assertTrue(
                    not actual_perm, "%s should not have any permissions to %s"
                    % (user_level, obj.__class__.__name__)
                )
            return

        # Get what permissions should be from permissions table.
        test_perm_list = perm_table[user_level]

        # Generically compare actual perms to what they should be
        # (test_perm_list).
        for perm_type, actual_perm in actual_perms.iteritems():

            # If should have perm.
            if perm_type in test_perm_list:
                self.assertTrue(
                    actual_perm, "%s should have %s perms to %s"
                    % (user_level, perm_type, obj.__class__.__name__))

            # If should not have perm.
            elif 'all' not in test_perm_list:
                self.assertTrue(
                    not actual_perm, "%s should not have %s perms to %s"
                    % (user_level, perm_type, obj.__class__.__name__)
                )
