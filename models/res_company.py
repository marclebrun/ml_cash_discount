# -*- coding: utf-8 -*-

from odoo import fields, models

class res_company(models.Model):
    _inherit = 'res.company'

    out_inv_cd_account_id = fields.Many2one(
        string='Outgoing Invoice Cash Discount Account',
        comodel_name='account.account',
        domain=[('deprecated', '=', False)],
    )
    