# -*- coding: utf-8 -*-

{
    'name': "Approvals Statement",
    'version': '1.3',
    'depends': ['account_accountant', 'sale_stock'],
    'author': "Sebastien Buhl",
    'website': "http://www.buhl.be",
    'license': 'LGPL-3',
    'application': True,
    'category': 'Customizations',
    'summary': 'Statements Approvals',
    'description': """
        Add an approval field on the bank statement
            note that the field is only informative
        Add a group Sales Level
        Only Store Manager can approve Bank Statement
    """,
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/activity.xml',
        'data/discount_settings.xml',
        'views/account_approval_request_inherited_tree.xml',
        'views/sale_order_views.xml',
    ],
}
