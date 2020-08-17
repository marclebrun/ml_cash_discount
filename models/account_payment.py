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
        print("IN  _compute_payment_amount")

        total = super()._compute_payment_amount(invoices, currency)
        infos = ""

        print("Montant initial : %.2f" % total)

        if not invoices:
            invoices = self.invoice_ids

        for inv in invoices:
            print("Facture %s %s" % (inv.type, inv.number))

            discount_applied = False
            
            if inv.show_cd:
                print("show_cd")
                if inv.date_cd:
                    discount_applied = self.payment_date and (self.payment_date <= inv.date_cd)

                if inv.payment_term_id and inv.payment_term_id.cd_percent:
                    delay = "%d %s" % (inv.payment_term_id.cd_delay, _("days"))   
                else:
                    delay = ""

                user_date_format   = self.env['res.lang']._lang_get(self.env.user.lang).date_format

                strValidity       = _("Discount validity :")
                strValidityValue  = "<strong>%s</strong>" % delay
                strDiscount       = _("Amount to be paid by <strong>%s</strong> at the latest :") % inv.date_cd.strftime(user_date_format)
                strDiscountValue  = "<strong>%.2f</strong>" % inv.total_cd
                strNormal         = _("Amount to be paid after that date :")
                strNormalValue    = "<strong>%.2f</strong>" % inv.residual_signed

                infos += "<table>"
                infos += "<tr><td>" + strValidity  + "</td><td>" + strValidityValue + "</td></tr>"
                infos += "<tr><td>" + strDiscount  + "</td><td>" + strDiscountValue + "</td></tr>"
                infos += "<tr><td>" + strNormal    + "</td><td>" + strNormalValue   + "</td></tr>"
                infos += "</table>"

        for payment in self:
            payment.infos_cd = infos
        
        print("OUT _compute_payment_amount")
        return total

    # @api.onchange('payment_date')
    # def _onchange_payment_date(self):
    #     print("IN  _onchange_payment_date")
    #     self.amount = self._compute_payment_amount()
    #     print("OUT _onchange_payment_date")

    # def _compute_payment_difference(self):
    #     print("IN  _compute_payment_difference")
    #     super()._compute_payment_difference()
    #     print("_compute_payment_difference() : amount = %.2f ; payment_difference = %.2f" % (self.amount, self.payment_difference))
    #     print("OUT _compute_payment_difference")







    #--------------------------------------------------------------------------------------------------

    # @api.onchange('amount')
    # def _onchange_amount(self):
    #     print("MONTANT MODIFIÉ")
    #     super()._onchange_amount()

    # def action_validate_invoice_payment(self):
    #     print("===============================")
    #     print("action_validate_invoice_payment")
    #     print("===============================")

    #     for payment in self:
    #         for invoice in payment.invoice_ids:
    #             print("Invoice %s - State %s" % (invoice.number, invoice.state))
    #             invoice.state = 'paid'
    #             # invoice.write({'state': 'paid'})
    #             print("    => %s" % invoice.state)
        
    #     return super().action_validate_invoice_payment()

