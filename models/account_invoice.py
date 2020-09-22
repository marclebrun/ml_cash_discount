# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # escompte sur la facture en €
    amount_cd = fields.Monetary(
        string  = 'Amount of Cash Discount',
        compute = '_compute_amount_cd',
        store   = True,
        help    = "Amount of Cash Discount"
    )

    # nouveau total une fois l'escompte soustrait
    total_cd = fields.Monetary(
        string  = 'Total including Cash Discount',
        compute = '_compute_amount_cd',
        store   = True,
        help    = "New total to pay if Cash Discount applied"
    )

    # date de validité de l'escompte
    date_cd = fields.Date(
        string  = 'Cash Discount validity date',
        compute = '_compute_date_cd',
        store   = True,
        help    = "Due Date for Cash Discount Conditions"
    )

    # bloc cash discount visible sous le total de facture
    show_cd = fields.Boolean(
        string  = 'Cash Discount visible',
        compute = '_compute_show_cd'
    )

    # calcule si le bloc "cash discount" doit être visible selon le payment term sélectionné
    @api.multi
    @api.depends('payment_term_id')
    def _compute_show_cd(self):
        for inv in self:
            # vrai si payment term est défini, et % d'escompte non null
            inv.show_cd = (inv.payment_term_id and inv.payment_term_id.cd_percent)

    # calcule le montant de l'escompte à chaque modification du total de la facture
    @api.multi
    @api.depends('payment_term_id', 'amount_total', 'amount_tax')
    def _compute_amount_cd(self):
        for inv in self:
            inv.amount_cd = 0.0
            inv.total_cd  = 0.0

            # si payment term est défini, et % d'escompte non null
            if inv.payment_term_id and inv.payment_term_id.cd_percent:
                if inv.payment_term_id.cd_include_tax == "untaxed":
                    inv.amount_cd = inv.amount_untaxed * inv.payment_term_id.cd_percent / 100
                if inv.payment_term_id.cd_include_tax == "total":
                    inv.amount_cd = inv.amount_total * inv.payment_term_id.cd_percent / 100
                inv.total_cd  = inv.amount_total - inv.amount_cd

    # calcule la date de validité de l'escompte lorsqu'on change le
    # payment term ou la date de facture
    @api.multi
    @api.depends('payment_term_id', 'date_invoice')
    def _compute_date_cd(self):
        for inv in self:
            inv.date_cd = False
            # si facture de vente, et payment term est défini, et % d'escompte non nul
            if inv.type == 'out_invoice' and inv.payment_term_id and inv.payment_term_id.cd_percent:
                cd_delay = inv.payment_term_id.cd_delay

                # à partir de la date de facture, ou de la date du jour
                if inv.date_invoice:
                    date_invoice = inv.date_invoice
                else:
                    # lire la date du jour vers une chaîne
                    date_invoice = time.strftime('%Y-%m-%d')
                    # retransformer cette chaîne en date
                    date_invoice = datetime.strptime(date_invoice, '%Y-%m-%d').date()

                # ajouter à la date de facture le nombre de
                # jours de validité de l'escompte
                date_cd = date_invoice + timedelta(cd_delay)

                # assigner la date résultante au champ date_cd de la
                # facture (chaîne au format YYYY-MM-DD)
                inv.date_cd = date_cd.isoformat()

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """
        :param move_lines: a list of lines prepared from
                           method 'action_move_create' in model 'account.invoice'
        :return: the updated list of lines
        """
        print("FINALIZE_INVOICE_MOVE_LINES")

        for invoice in self:
            print("BEFORE:")
            self.print_move_lines(move_lines)

            # si facture de vente ou note de crédit de vente
            if invoice.type in ['out_invoice', 'out_refund']:

                # si payment term est défini
                if invoice.payment_term_id:
                    pct = invoice.payment_term_id.cd_percent

                    # si le pourcentage de discount est non null
                    if pct:
                        cd_account = invoice.company_id.out_inv_cd_account_id
                        if not cd_account:
                            raise UserError(_("No account defined for Cash Discount."))

                        multiplier = 1 - pct / 100
                        cd_line = False
                        cd_vals = {
                            'name'       : _('Cash Discount'),
                            'account_id' : cd_account.id,
                            'partner_id' : invoice.partner_id.id,
                            'currency_id': False, # only EUR
                        }
                        cc_round = invoice.company_id.currency_id.round
                        amount_cd = 0.0
                        for line in move_lines:
                            vals = line[2]
                            if vals.get('tax_ids'):
                                cd_line = True
                                if vals.get('debit'):
                                    debit = cc_round(vals['debit'])
                                    vals['debit'] = cc_round(debit * multiplier)
                                    amount_cd += debit - vals['debit']
                                if vals.get('credit'):
                                    credit = cc_round(vals['credit'])
                                    vals['credit'] = cc_round(credit * multiplier)
                                    amount_cd -= credit - vals['credit']
                        if cd_line:
                            if amount_cd > 0:
                                cd_vals['debit'] = amount_cd
                            else:
                                cd_vals['credit'] = -amount_cd
                            move_lines.append((0, 0, cd_vals))
            print("AFTER:")
            self.print_move_lines(move_lines)
        raise UserError("\"finalize_invoice_move_lines\" finished")
        return move_lines

    def print_move_lines(self, lines):
        print("  | %-40s | %10s | %10s | %10s | %s " % ('NAME', 'ACCOUNT', 'DEBIT', 'CREDIT', 'TAX_IDS'))
        for line in lines:
            values = line[2]

            account = self.env['account.account'].search([('id', '=', values['account_id'])])[0]

            # The 'tax_ids' element is either a boolean False, or a list of tuples
            # Each tuple has the form (4, tax_id, None) => the 2dn element is the tax id.
            # s_taxes = ""
            # tax_ids = values['tax_ids']
            # print("TAX IDS = ", tax_ids)
            # if tax_ids:
            #     for tax_id_tuple in tax_ids:
            #         tax_id = tax_id_tuple[1]
            #         print("  => tax_id = ", tax_id)
            #         tax = self.env['account.tax'].search([ ('id', '=', tax_id)])[0]
            #         s_taxes += "(%d) %s " % (tax.id, tax.name)

            print("  | %-40s | %10s | %10.2f | %10.2f | %s" % (
                values['name'][:39],
                account.code,
                values['debit']   if 'debit'   in values else 0.0,
                values['credit']  if 'credit'  in values else 0.0,
                values['tax_ids'] if 'tax_ids' in values else "",
            ))

        print("-" * 120)
