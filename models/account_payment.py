# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bigoudi = fields.Char(string="Bigoudi", default="Trololol")
    infos_cd = fields.Html(string="Cash Discount information")

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        total = super(AccountPayment, self)._compute_payment_amount(invoices, currency)

        if not invoices:
            invoices = self.invoice_ids

        infos = ""

        for inv in invoices:
            discount_applied = inv.date_cd.today() <= inv.date_cd

            infos += "<table>"
            infos += "<tr><td>Invoice            </td><td><strong>%s  </strong></td></tr>" % inv.number
            infos += "<tr><td>Total to pay       </td><td><strong>%.2f</strong></td></tr>" % inv.residual_signed
            infos += "<tr><td>Total with discount</td><td><strong>%.2f</strong></td></tr>" % inv.total_cd
            infos += "<tr><td>Discount validity  </td><td><strong>%s  </strong></td></tr>" % inv.date_cd
            infos += "<tr><td>Discount is applied</td><td><strong>%s  </strong></td></tr>" % ("Yes" if discount_applied else "No")
            infos += "</table>"

            if discount_applied:
                total = inv.total_cd

        for rec in self:
            rec.infos_cd = infos
        
        return total
