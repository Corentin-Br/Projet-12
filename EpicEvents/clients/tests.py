import datetime

from django.test import TestCase
from unittest.mock import patch

from django.utils.timezone import make_aware

import clients.admin
from accounts.models import MyUser
from .models import Client, Contract

default_password = "correcthorsebatterystaple"


@patch.object(clients.admin.file_handler, 'stream', open('debug_test.log', 'a'))
class ClientsTest(TestCase):
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
        cls.sales_user_1 = MyUser.objects.create_user(
            first_name="Thomas",
            last_name="Bravo",
            email="thomas@gmail.com",
            role="sales",
            password=default_password
        )
        cls.sales_user_2 = MyUser.objects.create_user(
            first_name="Thomas_2",
            last_name="Bravo",
            email="thomas_2@gmail.com",
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
        cls.client1 = Client(first_name="client_test", last_name="1", email="client_test_1@gmail.com",
                             phone_number="+33666666666", mobile_number="", company_name="test_1", sales_contact=None)
        cls.client2 = Client(first_name="client_test", last_name="2", email="client_test_2@gmail.com",
                             phone_number="+33677777777", mobile_number="", company_name="test_2",
                             sales_contact=cls.sales_user_1)
        cls.client3 = Client(first_name="client_test", last_name="3", email="client_test_3@gmail.com",
                             phone_number="+33688888888", mobile_number="", company_name="test_3",
                             sales_contact=cls.sales_user_2)
        cls.additional_client_data = {"first_name": "client_test",
                                      "last_name": "4",
                                      "email": "client_test_4@gmail.com",
                                      "phone_number": "+33699999999",
                                      "company_name": "test_4"
                                      }
        cls.client1.save()
        cls.client2.save()
        cls.client3.save()
        cls.contract1 = Contract(sales_contact=cls.sales_user_1, client=cls.client2, status=False, amount=320.54,
                                 payment_due=make_aware(datetime.datetime.now()))
        cls.contract2 = Contract(sales_contact=cls.sales_user_2, client=cls.client2, status=False, amount=320.54,
                                 payment_due=make_aware(datetime.datetime.now()))
        cls.additional_contract_data = {"sales_contact": cls.sales_user_1.pk,
                                        "client": cls.client2.pk,
                                        "status": False,
                                        "amount": 320.54,
                                        "payment_due": make_aware(datetime.datetime.now())}
        cls.contract1.save()
        cls.contract2.save()

    def test_logged_users_can_access_the_app(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/clients/")
            assert resp.status_code == 200

    def test_unlogged_users_cant_access_the_app(self):
        resp = self.client.get("/admin/clients/")
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_logged_users_can_access_the_list_of_clients(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/clients/client/")
            assert resp.status_code == 200

    def test_logged_users_can_access_the_list_of_contracts(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/clients/contract/")
            assert resp.status_code == 200

    def test_unlogged_user_cant_access_the_models_list(self):
        for model in ("contract", "client"):
            resp = self.client.get(f"/admin/clients/{model}/")
            assert resp.status_code == 302
            assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_logged_users_can_access_a_specific_client(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get(f"/admin/clients/client/{self.client1.pk}/change/")
            assert resp.status_code == 200

    def test_logged_users_can_access_a_specific_contract(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get(f"/admin/clients/contract/{self.contract1.pk}/change/")
            assert resp.status_code == 200

    def test_unlogged_user_cant_access_to_a_specific_model(self):
        for model in ("contract", "client"):
            resp = self.client.get(f"/admin/clients/{model}/{getattr(self, f'{model}1').pk}/change")
            assert resp.status_code == 302
            assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_gestion_user_can_modify_a_specific_client(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client1.pk}/change/",
                                {"first_name": "client_test",
                                 "last_name": "1",
                                 "email": "client_test_1@gmail.com",
                                 "phone_number": "+33666666666",
                                 "mobile_number": "+33666666666",
                                 "company_name": "test_1",
                                 "sales_contact": ""})
        assert resp.status_code == 302
        assert Client.objects.first().mobile_number == "+33666666666"

    def test_sales_user_can_modify_unowned_clients(self):
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client1.pk}/change/",
                                {"first_name": "client_test",
                                 "last_name": "1",
                                 "email": "client_test_1@gmail.com",
                                 "phone_number": "+33666666666",
                                 "mobile_number": "+33666666666",
                                 "company_name": "test_1",
                                 "sales_contact": self.sales_user_1.pk})
        assert resp.status_code == 302
        assert Client.objects.get(pk=self.client1.pk).sales_contact == self.sales_user_1

    def test_sales_user_can_modify_their_clients(self):
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client2.pk}/change/",
                                {"first_name": "client_test",
                                 "last_name": "2",
                                 "email": "client_test_2@gmail.com",
                                 "phone_number": "+33666666666",
                                 "mobile_number": "+33666666666",
                                 "company_name": "test_1",
                                 "sales_contact": self.sales_user_1.pk})
        assert resp.status_code == 302
        assert Client.objects.get(pk=self.client2.pk).sales_contact == self.sales_user_1

    def test_sales_user_cant_modify_other_clients(self):
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client3.pk}/change/",
                                {"first_name": "client_test",
                                 "last_name": "3",
                                 "email": "client_test_3@gmail.com",
                                 "phone_number": "+33666666666",
                                 "mobile_number": "+33666666666",
                                 "company_name": "test_1",
                                 "sales_contact": self.sales_user_1.pk})
        assert resp.status_code == 403
        assert Client.objects.get(pk=self.client3.pk).sales_contact == self.sales_user_2

    def test_support_user_cant_modify_other_clients(self):
        self.client.login(**self.support_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client3.pk}/change/",
                                {"first_name": "client_test",
                                 "last_name": "3",
                                 "email": "client_test_3@gmail.com",
                                 "phone_number": "+33666666666",
                                 "mobile_number": "+33666666666",
                                 "company_name": "test_1",
                                 "sales_contact": self.sales_user_1.pk})
        assert resp.status_code == 403
        assert Client.objects.get(pk=self.client3.pk).sales_contact == self.sales_user_2

    def test_unlogged_user_cant_modify_other_clients(self):
        resp = self.client.post(f"/admin/clients/client/{self.client3.pk}/change/",
                                {"first_name": "client_test",
                                 "last_name": "3",
                                 "email": "client_test_3@gmail.com",
                                 "phone_number": "+33666666666",
                                 "mobile_number": "+33666666666",
                                 "company_name": "test_1",
                                 "sales_contact": self.sales_user_1.pk})
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_gestion_user_can_modify_a_specific_contract(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract1.pk}/change/",
                                {"sales_contact": self.sales_user_1.pk,
                                 "client": self.client2.pk,
                                  "status": False,
                                  "amount": 100,
                                  "payment_due": make_aware(datetime.datetime.now())})
        assert resp.status_code == 302
        assert Contract.objects.first().amount == 100

    def test_sales_user_can_modify_a_owned_contract(self):
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract1.pk}/change/",
                                {"sales_contact": self.sales_user_1.pk,
                                 "client": self.client2.pk,
                                 "status": False,
                                 "amount": 100,
                                 "payment_due": make_aware(datetime.datetime.now())})
        assert resp.status_code == 302
        assert Contract.objects.first().amount == 100

    def test_sales_user_cant_modify_an_unowned_contract(self):
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract2.pk}/change/",
                                {"sales_contact": self.sales_user_1.pk,
                                 "client": self.client2.pk,
                                 "status": False,
                                 "amount": 100,
                                 "payment_due": make_aware(datetime.datetime.now())})
        assert resp.status_code == 403
        assert Contract.objects.get(pk=self.contract2.pk).amount == 320.54

    def test_support_user_cant_modify_a_contract(self):
        self.client.login(**self.support_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract2.pk}/change/",
                                {"sales_contact": self.sales_user_1.pk,
                                 "client": self.client2.pk,
                                 "status": False,
                                 "amount": 100,
                                 "payment_due": make_aware(datetime.datetime.now())})
        assert resp.status_code == 403
        assert Contract.objects.get(pk=self.contract2.pk).amount == 320.54

    def test_unlogged_user_cant_modify_a_contract(self):
        resp = self.client.post(f"/admin/clients/contract/{self.contract2.pk}/change/",
                                {"sales_contact": self.sales_user_1.pk,
                                 "client": self.client2.pk,
                                 "status": False,
                                 "amount": 100,
                                 "payment_due": make_aware(datetime.datetime.now())})
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert Contract.objects.get(pk=self.contract2.pk).amount == 320.54

    def test_gestion_user_can_create_a_client(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.gestion_logs)
        resp = self.client.post("/admin/clients/client/add/", self.additional_client_data)
        assert resp.status_code == 302
        assert len(Client.objects.all()) == number_of_objects + 1

    def test_sales_user_can_create_a_client(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.sales_logs)
        resp = self.client.post("/admin/clients/client/add/", self.additional_client_data)
        assert resp.status_code == 302
        assert len(Client.objects.all()) == number_of_objects + 1

    def test_support_user_cant_create_a_client(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.support_logs)
        resp = self.client.post("/admin/clients/client/add/", self.additional_client_data)
        assert resp.status_code == 403
        assert len(Client.objects.all()) == number_of_objects

    def test_unlogged_user_cant_create_a_client(self):
        number_of_objects = len(Client.objects.all())
        resp = self.client.post("/admin/clients/client/add/", self.additional_client_data)
        assert resp.status_code == 302
        assert len(Client.objects.all()) == number_of_objects
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_gestion_user_can_create_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.gestion_logs)
        resp = self.client.post("/admin/clients/contract/add/", self.additional_contract_data)
        assert resp.status_code == 302
        assert len(Contract.objects.all()) == number_of_objects + 1

    def test_sales_user_can_create_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.sales_logs)
        resp = self.client.post("/admin/clients/contract/add/", self.additional_contract_data)
        assert resp.status_code == 302
        assert len(Contract.objects.all()) == number_of_objects + 1

    def test_support_user_cant_create_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.support_logs)
        resp = self.client.post("/admin/clients/contract/add/", self.additional_contract_data)
        assert resp.status_code == 403
        assert len(Contract.objects.all()) == number_of_objects

    def test_unlogged_user_cant_create_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        resp = self.client.post("/admin/clients/contract/add/", self.additional_contract_data)
        assert resp.status_code == 302
        assert len(Contract.objects.all()) == number_of_objects
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_gestion_user_can_delete_a_client(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Client.objects.all()) == number_of_objects - 1

    def test_sales_user_can_delete_their_clients(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client2.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Client.objects.all()) == number_of_objects - 1

    def test_sales_user_cant_delete_other_clients(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client3.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 403
        assert len(Client.objects.all()) == number_of_objects

    def test_support_user_cant_delete_a_client(self):
        number_of_objects = len(Client.objects.all())
        self.client.login(**self.support_logs)
        resp = self.client.post(f"/admin/clients/client/{self.client1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 403
        assert len(Client.objects.all()) == number_of_objects

    def test_unlogged_user_cant_delete_a_client(self):
        number_of_objects = len(Client.objects.all())
        resp = self.client.post(f"/admin/clients/client/{self.client1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Client.objects.all()) == number_of_objects
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_gestion_user_can_delete_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Contract.objects.all()) == number_of_objects - 1

    def test_sales_user_can_delete_their_contracts(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Contract.objects.all()) == number_of_objects - 1

    def test_sales_user_cant_delete_other_contracts(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract2.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 403
        assert len(Contract.objects.all()) == number_of_objects

    def test_support_user_cant_delete_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        self.client.login(**self.support_logs)
        resp = self.client.post(f"/admin/clients/contract/{self.contract1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 403
        assert len(Contract.objects.all()) == number_of_objects

    def test_unlogged_user_cant_delete_a_contract(self):
        number_of_objects = len(Contract.objects.all())
        resp = self.client.post(f"/admin/clients/contract/{self.contract1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Contract.objects.all()) == number_of_objects
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
