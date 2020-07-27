# -*- coding: utf-8 -*-

{
    'name': 'ML Cash Discount',
    'summary': 'Cash Discount on Invoices according to Belgian Tax Rules',
    'description': """
        This module is based on original module for Odoo v10 by Noviat nv :
        https://github.com/luc-demeyer/noviat-apps/tree/10.0/l10n_be_cash_discount
    """,
    'version': '0.1',
    'author': 'Marc Lebrun',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/account_payment_term.xml',
        'views/account_payment_view.xml',
        'views/res_company.xml',
        'reports/report_invoice.xml',
    ],
    'installable': True,
}