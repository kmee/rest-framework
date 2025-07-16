# Copyright 2024 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timezone
from secrets import token_urlsafe

import jwt

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.delay import chain


class AuthDirectory(models.Model):
    _name = "auth.directory"
    _description = "Auth Directory"
    _inherit = "server.env.mixin"

    name = fields.Char(required=True)
    auth_partner_ids = fields.One2many("auth.partner", "directory_id", "Auth Partners")
    set_password_token_duration = fields.Integer(
        default=1440, help="In minute, default 1440 minutes => 24h", required=True
    )
    impersonating_token_duration = fields.Integer(
        default=60, help="In seconds, default 60 seconds", required=True
    )
    reset_password_template_id = fields.Many2one(
        "mail.template",
        "Mail Template Forget Password",
        required=True,
        default=lambda self: self.env.ref(
            "auth_partner.email_reset_password",
            raise_if_not_found=False,
        ),
    )
    set_password_template_id = fields.Many2one(
        "mail.template",
        "Mail Template New Password",
        required=True,
        default=lambda self: self.env.ref(
            "auth_partner.email_set_password",
            raise_if_not_found=False,
        ),
    )
    validate_email_template_id = fields.Many2one(
        "mail.template",
        "Mail Template Validate Email",
        required=True,
        default=lambda self: self.env.ref(
            "auth_partner.email_validate_email",
            raise_if_not_found=False,
        ),
    )
    secret_key = fields.Char(
        groups="base.group_system",
        required=True,
        default=lambda self: self._generate_default_secret_key(),
    )
    count_partner = fields.Integer(compute="_compute_count_partner")

    impersonating_user_ids = fields.Many2many(
        "res.users",
        "auth_directory_impersonating_user_rel",
        "directory_id",
        "user_id",
        string="Impersonating Users",
        help="These odoo users can impersonate any partner of this directory",
        default=lambda self: (
            self.env.ref("base.user_root") | self.env.ref("base.user_admin")
        ).ids,
        groups="auth_partner.group_auth_partner_manager",
    )
    force_verified_email = fields.Boolean(
        help="If checked, email must be verified to be able to log in"
    )
