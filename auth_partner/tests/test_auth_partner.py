# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from datetime import datetime, timedelta
from freezegun import freeze_time
from odoo.exceptions import AccessDenied, UserError
from .common import CommonTestAuthPartner

class TestAuthPartner(CommonTestAuthPartner):
    @contextmanager
    def assert_no_new_mail(self):
        with self.new_mails() as new_mails:
            yield
        self.assertFalse(new_mails)
    def test_default_secret_key(self):
        self.assertGreaterEqual(len(self.directory.secret_key), 64)
    def test_login_ok(self):
        with self.assert_no_new_mail():
            auth_partner = self.env["auth.partner"]._login(
                self.directory,
                login="partner-auth@example.org",
                password="Super-secret$1",
            )
        self.assertTrue(auth_partner)
    def test_login_inactive_partner(self):
        self.partner.active = False
        with self.assertRaisesRegex(AccessDenied, "Invalid Login or Password"):
            self.env["auth.partner"]._login(
                self.directory,
                login="partner-auth@example.org",
                password="Super-secret$1",
            )
    def test_login_no_auth(self):
        self.auth_partner.unlink()
        with self.assertRaisesRegex(AccessDenied, "Invalid Login or Password"):
            self.env["auth.partner"]._login(
                self.directory,
                login="partner-auth@example.org",
                password="Super-secret$1",
            )
