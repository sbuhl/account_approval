{
    'name': "Approvals Statement",
    'version': '1.0',
    'depends': ['base', 'hr_contract', 'account_accountant'],
    'author': "Sebastien Buhl",
    'application': True,
    'category': 'Category',
    'description': """
        Description text
    """,
    'data': [
        'security/account_approval_security.xml',
        'security/ir.model.access.csv',
        'views/account_approval_request_inherited_tree.xml',
        'data/activity.xml'
    ],

}
