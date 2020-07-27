# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bigoudi = fields.Char(string="Bigoudi", default="Trololol")

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        total = super(AccountPayment, self)._compute_payment_amount(invoices, currency)
        total *= 2
        for rec in self:
            rec.bigoudi = "Calcul effectué"
        return total
