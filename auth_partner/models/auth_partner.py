# Copyright 2024 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

import passlib

from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied

# please read passlib great documentation
# https://passlib.readthedocs.io
# https://passlib.readthedocs.io/en/stable/narr/quickstart.html#choosing-a-hash
# be carefull odoo requirements use an old version of passlib
DEFAULT_CRYPT_CONTEXT = passlib.context.CryptContext(["pbkdf2_sha512"])

_logger = logging.getLogger(__name__)


class AuthPartner(models.Model):
    _name = "auth.partner"
    _description = "Auth Partner"
    _rec_name = "login"

    partner_id = fields.Many2one(
        "res.partner", "Partner", required=True, ondelete="cascade", index=True
    )
    directory_id = fields.Many2one(
        "auth.directory", "Directory", required=True, index=True
    )
    user_can_impersonate = fields.Boolean(
        compute="_compute_user_can_impersonate",
        help="Technical field to check if the user can impersonate",
    )
    impersonating_user_ids = fields.Many2many(
        related="directory_id.impersonating_user_ids",
    )
    login = fields.Char(
        compute="_compute_login",
        store=True,
        required=True,
        index=True,
        precompute=True,
    )
    password = fields.Char(compute="_compute_password", inverse="_inverse_password")
    encrypted_password = fields.Char(index=True)
    nbr_pending_reset_sent = fields.Integer(
        index=True,
        help=(
            "Number of pending reset sent from your customer."
            "This field is usefull when after a migration from an other system "
            "you ask all you customer to reset their password and you send"
            "different mail depending on the number of reminder"
        ),
    )
    date_last_request_reset_pwd = fields.Datetime(
        help="Date of the last password reset request"
    )
    date_last_sucessfull_reset_pwd = fields.Datetime(
        help="Date of the last sucessfull password reset"
    )
    date_last_impersonation = fields.Datetime(
        help="Date of the last sucessfull impersonation"
    )

    mail_verified = fields.Boolean(
        help="This field is set to True when the user has clicked on the link sent by email"
    )

    _sql_constraints = [
        (
            "directory_login_uniq",
            "unique (directory_id, login)",
            "Login must be uniq per directory !",
        ),
    ]
