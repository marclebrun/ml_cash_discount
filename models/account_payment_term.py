# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountPaymentTerm(models.Model):

    _inherit = "account.payment.term"

    cd_percent = fields.Float(
        string = "Discount (%)"
    )

    cd_delay = fields.Integer(
        string = "Discount delay (days)"
    )

    cd_include_tax = fields.Selection(
        string = "Include Taxes in calculation of Cash Discount amount ?",
        selection = [
            ("untaxed", _("Excluding tax")),
            ("total",   _("Including all taxes")),
        ],
        default = "untaxed"
    )
