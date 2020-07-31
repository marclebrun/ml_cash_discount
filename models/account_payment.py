# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

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

            if inv.payment_term_id and inv.payment_term_id.cd_percent:
                validity = "(%d %s)" % (inv.payment_term_id.cd_delay, _("days"))
            else:
                validity = ""

            infos += "<table>"
            infos += "<tr><td>" + _("Invoice number")      + "</td><td><strong>%s  </strong></td></tr>" % inv.number
            infos += "<tr><td>" + _("Date of invoice")     + "</td><td><strong>%s  </strong></td></tr>" % inv.date_invoice
            infos += "<tr><td>" + _("Discount validity")   + "</td><td><strong>%s %s</strong></td></tr>" % (inv.date_cd, validity)
            infos += "<tr><td>" + _("Payment date")        + "</td><td><strong>%s  </strong></td></tr>" % self.payment_date
            infos += "<tr><td>" + _("Total to pay")        + "</td><td><strong>%.2f</strong></td></tr>" % inv.residual_signed
            infos += "<tr><td>" + _("Total with discount") + "</td><td><strong>%.2f</strong></td></tr>" % inv.total_cd
            infos += "<tr><td>" + _("Discount is applied") + "</td><td><strong>%s  </strong></td></tr>" % (_("Yes") if discount_applied else _("No"))
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
