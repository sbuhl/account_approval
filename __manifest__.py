# -*- coding: utf-8 -*-

{
    'name': "Approvals Statement",
    'version': '1.3',
    'depends': ['account_accountant'],
    'author': "Sebastien Buhl",
    'website': "http://www.buhl.be",
    'license': 'LGPL-3',
    'application': True,
    'category': 'Customizations',
    'summary': 'Statements Approvals',
    'description': """
        Add an approval step on the bank statement
    """,
    'data': [
        'data/activity.xml',
        'views/account_approval_request_inherited_tree.xml',
    ],
}
