# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    infos_cd = fields.Html(string="Cash Discount information")

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        """
        If the date of payment is less or equal to the Cash Discount validity date,
        then the total amount of the payment is replaced with the discounted amount
        of the invoice.
        """
        total = super(AccountPayment, self)._compute_payment_amount(invoices, currency)

        if not invoices:
            invoices = self.invoice_ids

        infos = ""

        for inv in invoices:
            discount_applied = self.payment_date and (self.payment_date <= inv.date_cd)

            infos += "<table>"
            infos += "<tr><td>Invoice            </td><td><strong>%s  </strong></td></tr>" % inv.number
            infos += "<tr><td>Total to pay       </td><td><strong>%.2f</strong></td></tr>" % inv.residual_signed
            infos += "<tr><td>Total with discount</td><td><strong>%.2f</strong></td></tr>" % inv.total_cd
            infos += "<tr><td>Discount validity  </td><td><strong>%s  </strong></td></tr>" % inv.date_cd
            infos += "<tr><td>Payment date       </td><td><strong>%s  </strong></td></tr>" % self.payment_date
            infos += "<tr><td>Discount is applied</td><td><strong>%s  </strong></td></tr>" % ("Yes" if discount_applied else "No")
            infos += "</table>"

            if discount_applied:
                total = inv.total_cd

        for rec in self:
            rec.infos_cd = infos
        
        return total

    @api.onchange('payment_date')
    def _onchange_payment_date(self):
        #res = super(account_register_payments, self)._onchange_journal()
        #active_ids = self._context.get('active_ids')
        #invoices = self.env['account.invoice'].browse(active_ids)
        #self.amount = abs(self._compute_payment_amount(invoices))
        #return res
        self.amount = self._compute_payment_amount()
