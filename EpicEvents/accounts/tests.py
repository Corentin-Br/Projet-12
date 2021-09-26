from django.test import TestCase
from unittest.mock import patch

import accounts.admin
from accounts.models import MyUser

default_password = "correcthorsebatterystaple"

@patch.object(accounts.admin.file_handler, 'stream', open('debug3.log', 'a'))
class AccountsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gestion_logs = {"email": "corentin@gmail.com", "password": default_password}
        cls.sales_logs = {"email": "thomas@gmail.com", "password": default_password}
        cls.support_logs = {"email": "timothee@gmail.com", "password": default_password}
        cls.gestion_user = MyUser.objects.create_user(
            first_name="Corentin",
            last_name="Bravo",
            role="gestion",
            email="corentin@gmail.com",
            password=default_password
        )
        cls.sales_user = MyUser.objects.create_user(
            first_name="Thomas",
            last_name="Bravo",
            email="thomas@gmail.com",
            role="sales",
            password=default_password
        )
        cls.support_user = MyUser.objects.create_user(
            first_name="Timothée",
            last_name="Bravo",
            email="timothee@gmail.com",
            role="support",
            password=default_password
        )
        cls.additional_user_data = {
            "first_name": "Matthieu",
            "last_name": "Bravo",
            "email": "matthieu@gmail.com",
            "role": "support",
            "password": default_password,
            "password2": default_password,
            "_save": "Save"
        }

    def test_unlogged_user_cant_access_the_app(self):
        resp = self.client.get("/admin/accounts")
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_unlogged_user_cant_access_the_user_list(self):
        resp = self.client.get("/admin/accounts/myuser/")
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_unlogged_user_cant_access_a_specific_user(self):
        for user in (self.gestion_user, self.sales_user, self.support_user):
            resp = self.client.get(f"/admin/accounts/myuser/{user.pk}/change/")
            assert resp.status_code == 302
            assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_unlogged_user_cant_modify_a_specific_user(self):
        resp = self.client.post(f"/admin/accounts/myuser/{self.gestion_user.pk}/change/",
                                {"first_name": "Thomas", "email": self.gestion_user.email,
                                 "last_name": self.gestion_user.last_name, "role": self.gestion_user.role,
                                 "is_active": self.gestion_user.is_active})
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert MyUser.objects.get_by_natural_key(self.gestion_user.email).first_name == "Corentin"

    def test_unlogged_user_cant_create_a_user(self):
        number_of_users = len(MyUser.objects.all())
        resp = self.client.post("/admin/accounts/myuser/add/", self.additional_user_data)
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert len(MyUser.objects.all()) == number_of_users

    def test_unlogged_user_cant_delete_a_user(self):
        number_of_users = len(MyUser.objects.all())
        resp = self.client.post(f"/admin/accounts/myuser/{self.gestion_user.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert len(MyUser.objects.all()) == number_of_users

    def test_gestion_user_can_access_the_app(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.get("/admin/accounts/")
        assert resp.status_code == 200

    def test_support_and_sales_user_cant_access_the_app(self):
        for logs in (self.support_logs, self.sales_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/accounts/")
            assert resp.status_code == 404

    def test_gestion_user_can_access_the_user_list(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.get("/admin/accounts/myuser/")
        assert resp.status_code == 200

    def test_support_and_sales_user_cant_access_the_user_list(self):
        for logs in (self.support_logs, self.sales_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/accounts/myuser/")
            assert resp.status_code == 403

    def test_gestion_user_can_access_a_specific_user(self):
        self.client.login(**self.gestion_logs)
        for user in (self.gestion_user, self.sales_user, self.support_user):
            resp = self.client.get(f"/admin/accounts/myuser/{user.pk}/change/")
            assert resp.status_code == 200

    def test_support_and_sales_user_cant_access_a_specific_user(self):
        for logs in (self.support_logs, self.sales_logs):
            for user in (self.gestion_user, self.sales_user, self.support_user):
                self.client.login(**logs)
                resp = self.client.get(f"/admin/accounts/myuser/{user.pk}/change/")
                assert resp.status_code == 403

    def test_gestion_user_can_modify_a_specific_user(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/accounts/myuser/{self.gestion_user.pk}/change/", {"first_name": "Jacques", "email": self.gestion_user.email, "last_name": self.gestion_user.last_name, "role": self.gestion_user.role, "is_active": self.gestion_user.is_active})
        assert resp.status_code == 302
        assert MyUser.objects.get_by_natural_key(self.gestion_user.email).first_name == "Jacques"

    def test_support_and_sales_user_cant_modify_a_specific_user(self):
        for logs in (self.support_logs, self.sales_logs):
            self.client.login(**logs)
            resp = self.client.post(f"/admin/accounts/myuser/{self.gestion_user.pk}/change/",
                                    {"first_name": "Thomas", "email": self.gestion_user.email,
                                     "last_name": self.gestion_user.last_name, "role": self.gestion_user.role,
                                     "is_active": self.gestion_user.is_active})
            assert resp.status_code == 403
            assert MyUser.objects.get_by_natural_key(self.gestion_user.email).first_name == "Corentin"

    def test_gestion_user_can_create_a_user(self):
        self.client.login(**self.gestion_logs)
        number_of_users = len(MyUser.objects.all())
        resp = self.client.post("/admin/accounts/myuser/add/", self.additional_user_data)
        assert resp.status_code == 302
        assert len(MyUser.objects.all()) == number_of_users + 1

    def test_support_and_sales_user_cant_create_a_user(self):
        for logs in (self.support_logs, self.sales_logs):
            self.client.login(**logs)
            number_of_users = len(MyUser.objects.all())
            resp = self.client.post("/admin/accounts/myuser/add/", self.additional_user_data)
            assert resp.status_code == 403
            assert len(MyUser.objects.all()) == number_of_users

    def test_gestion_user_can_delete_a_user(self):
        self.client.login(**self.gestion_logs)
        number_of_users = len(MyUser.objects.all())
        resp = self.client.post(f"/admin/accounts/myuser/{self.sales_user.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(MyUser.objects.all()) == number_of_users - 1

    def test_support_and_sales_user_cant_delete_a_user(self):
        for logs in (self.support_logs, self.sales_logs):
            self.client.login(**logs)
            number_of_users = len(MyUser.objects.all())
            resp = self.client.post(f"/admin/accounts/myuser/{self.gestion_user.pk}/delete/", {"post": "yes"})
            assert resp.status_code == 403
            assert len(MyUser.objects.all()) == number_of_users
