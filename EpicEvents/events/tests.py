import datetime

from django.test import TestCase
from unittest.mock import patch

import events.admin
from accounts.models import MyUser
from clients.models import Client, Contract
from .models import Event

default_password = "correcthorsebatterystaple"

@patch.object(events.admin.file_handler, 'stream', open('debug_test.log', 'a'))
class EventsTest(TestCase):
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
        cls.support_user1 = MyUser.objects.create_user(
            first_name="Timothée",
            last_name="Bravo",
            email="timothee@gmail.com",
            role="support",
            password=default_password
        )
        cls.support_user2 = MyUser.objects.create_user(
            first_name="Timothée_2",
            last_name="Bravo",
            email="timothee_2@gmail.com",
            role="support",
            password=default_password
        )
        cls.client1 = Client(first_name="client_test", last_name="1", email="client_test_1@gmail.com", phone_number="+33666666666", mobile_number="", company_name="test_1", sales_contact=None)
        cls.client2 = Client(first_name="client_test", last_name="2", email="client_test_2@gmail.com", phone_number="+33677777777", mobile_number="", company_name="test_2",
                             sales_contact=cls.sales_user_1)
        cls.client1.save()
        cls.client2.save()
        cls.contract1 = Contract(sales_contact=cls.sales_user_1, client=cls.client2, status=False, amount=320.54, payment_due=datetime.datetime.now())
        cls.contract2 = Contract(sales_contact=cls.sales_user_1, client=cls.client2, status=False, amount=320.54, payment_due=datetime.datetime.now())
        cls.contract3 = Contract(sales_contact=cls.sales_user_1, client=cls.client2, status=False, amount=320.54, payment_due=datetime.datetime.now())
        cls.contract1.save()
        cls.contract2.save()
        cls.contract3.save()
        cls.event1 = Event(client=cls.client2, support=cls.support_user1, contract=cls.contract1, attendees=10, date=datetime.datetime.now(), notes="")
        cls.event2 = Event(client=cls.client2, support=cls.support_user2, contract=cls.contract2, attendees=10, date=datetime.datetime.now(), notes="")
        cls.event_additional_data_1 = {"client": cls.client1.pk,
                                       "support": cls.support_user1.pk,
                                       "contract": cls.contract3.pk,
                                       "attendees": 10,
                                       "date": datetime.datetime.now(),
                                       "notes": ""}
        cls.event_additional_data_2 = {"client": cls.client2.pk,
                                       "support": cls.support_user1.pk,
                                       "contract": cls.contract3.pk,
                                       "attendees": 10,
                                       "date": datetime.datetime.now(),
                                       "notes": ""}
        cls.event1.save()
        cls.event2.save()

    def test_unlogged_user_cant_access_the_app(self):
        resp = self.client.get("/admin/events/")
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_unlogged_user_cant_access_the_events_list(self):
        resp = self.client.get("/admin/events/event/")
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_unlogged_user_cant_access_a_specific_event(self):
        resp = self.client.get(f"/admin/events/event/{self.event1.pk}/change/")
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"

    def test_unlogged_user_cant_modify_a_specific_event(self):
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/change/",
                                {"client": self.client2.pk,
                                 "support": self.support_user1.pk,
                                 "contract": self.contract1.pk,
                                 "attendees": 10,
                                 "date": datetime.datetime.now(),
                                 "notes": "note"})
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert Event.objects.get(pk=self.event1.pk).notes == ""

    def test_unlogged_user_cant_create_an_event(self):
        number_of_events = len(Event.objects.all())
        resp = self.client.post("/admin/events/event/add/", self.event_additional_data_1)
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert len(Event.objects.all()) == number_of_events

    def test_unlogged_user_cant_delete_an_event(self):
        number_of_events = len(Event.objects.all())
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert resp.url == f"/admin/login/?next={resp.request['PATH_INFO']}"
        assert len(Event.objects.all()) == number_of_events

    def test_logged_users_can_access_the_app(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/events/")
            assert resp.status_code == 200

    def test_logged_users_can_access_the_event_list(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get("/admin/events/event/")
            assert resp.status_code == 200

    def test_logged_users_can_access_a_specific_event(self):
        for logs in (self.gestion_logs, self.sales_logs, self.support_logs):
            self.client.login(**logs)
            resp = self.client.get(f"/admin/events/event/{self.event1.pk}/change/")
            assert resp.status_code == 200

    def test_gestion_user_can_modify_a_specific_event(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/change/",
                                {"client": self.client2.pk,
                                 "support": self.support_user1.pk,
                                 "contract": self.contract1.pk,
                                 "attendees": 10,
                                 "date": datetime.datetime.now(),
                                 "notes": "note"})
        assert resp.status_code == 302
        assert Event.objects.get(pk=self.event1.pk).notes == "note"

    def test_gestion_user_cant_modify_event_with_wrong_contract(self):
        self.client.login(**self.gestion_logs)
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/change/",
                                {"client": self.client1.pk,
                                 "support": self.support_user1.pk,
                                 "contract": self.contract1.pk,
                                 "attendees": 10,
                                 "date": datetime.datetime.now(),
                                 "notes": "note"})
        assert resp.status_code == 200
        assert Event.objects.get(pk=self.event1.pk).notes == ""

    def test_support_users_can_modify_their_events(self):
        self.client.login(**self.support_logs)
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/change/",
                                {"client": self.client2.pk,
                                 "support": self.support_user1.pk,
                                 "contract": self.contract1.pk,
                                 "attendees": 10,
                                 "date": datetime.datetime.now(),
                                 "notes": "note"})
        assert resp.status_code == 302
        assert Event.objects.get(pk=self.event1.pk).notes == "note"

    def test_support_users_cant_modify_unowned_events(self):
        self.client.login(**self.support_logs)
        resp = self.client.post(f"/admin/events/event/{self.event2.pk}/change/",
                                {"client": self.client2.pk,
                                 "support": self.support_user1.pk,
                                 "contract": self.contract1.pk,
                                 "attendees": 10,
                                 "date": datetime.datetime.now(),
                                 "notes": "note"})
        assert resp.status_code == 403
        assert Event.objects.get(pk=self.event2.pk).notes == ""

    def test_sales_users_cant_modify_events(self):
        self.client.login(**self.sales_logs)
        resp = self.client.post(f"/admin/events/event/{self.event2.pk}/change/",
                                {"client": self.client2.pk,
                                 "support": self.support_user1.pk,
                                 "contract": self.contract1.pk,
                                 "attendees": 10,
                                 "date": datetime.datetime.now(),
                                 "notes": "note"})
        assert resp.status_code == 403
        assert Event.objects.get(pk=self.event2.pk).notes == ""

    def test_gestion_user_can_create_an_event(self):
        self.client.login(**self.gestion_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post("/admin/events/event/add/", self.event_additional_data_2)
        assert resp.status_code == 302
        assert len(Event.objects.all()) == number_of_events + 1

    def test_sales_user_can_create_an_event(self):
        self.client.login(**self.sales_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post("/admin/events/event/add/", self.event_additional_data_2)
        assert resp.status_code == 302
        assert len(Event.objects.all()) == number_of_events + 1

    def test_support_user_cant_create_an_event(self):
        self.client.login(**self.support_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post("/admin/events/event/add/", self.event_additional_data_2)
        assert resp.status_code == 403
        assert len(Event.objects.all()) == number_of_events

    def test_gestion_user_can_delete_an_event(self):
        self.client.login(**self.gestion_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Event.objects.all()) == number_of_events - 1

    def test_sales_user_cant_delete_an_event(self):
        self.client.login(**self.sales_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 403
        assert len(Event.objects.all()) == number_of_events

    def test_support_user_can_delete_their_events(self):
        self.client.login(**self.support_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post(f"/admin/events/event/{self.event1.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 302
        assert len(Event.objects.all()) == number_of_events - 1

    def test_support_user_cant_delete_other_events(self):
        self.client.login(**self.support_logs)
        number_of_events = len(Event.objects.all())
        resp = self.client.post(f"/admin/events/event/{self.event2.pk}/delete/", {"post": "yes"})
        assert resp.status_code == 403
        assert len(Event.objects.all()) == number_of_events
