# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountBankStatement(models.Model):
    _name = 'account.bank.statement'
    _inherit = ['account.bank.statement', 'mail.activity.mixin']

    @api.model
    def _default_employee_id(self):
        employee = self.env.user.employee_id
        if not employee and not self.env.user.has_group('hr.group_hr_user'):
            raise ValidationError(_('The current user has no related employee. Please, create one.'))
        return employee

    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee", store=True, readonly=True, tracking=True, default=_default_employee_id)  # noqa: E501

    state = fields.Selection(selection_add=[("to_approve", "Approbation"), ('posted',)], ondelete={'to_approve':'set default'})  # noqa: E501
 
    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, tracking=True)  # noqa: E501

    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for statement in self:
                statement.employee_id = self.env.user.with_company(statement.company_id).employee_id  # noqa: E501

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for sheet in self:
            sheet.user_id = sheet.employee_id.parent_id.user_id

    def button_approbation(self):
        ''' Move the bank statements from 'draft' to 'posted'. '''
        if any(statement.state != 'open' for statement in self):
            raise UserError(_("Only new statements can be posted."))

        self._check_balance_end_real_same_as_computed()

        for statement in self:
            if not statement.name:
                statement._set_next_sequence()

        self.write({'state': 'to_approve'})
        self.activity_update()

        lines_of_moves_to_post = self.line_ids.filtered(lambda line: line.move_id.state != 'posted')  # noqa: E501
        if lines_of_moves_to_post:
            lines_of_moves_to_post.move_id._post(soft=False)

    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']
    
    def activity_update(self):
        for bank_statement in self.filtered(lambda hol: hol.state == 'to_approve'):  # noqa: E501
            self.activity_schedule('approvals_statements.mail_activity_approval', user_id=bank_statement.sudo()._get_responsible_for_approval().id, note='Please approve statement')  # noqa: E501

    def button_post(self):
        self.write({'state': 'posted'})

    def action_cancel(self):
        self.write({'state': 'open'})


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')  # noqa: E501

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')  # noqa: E501
        res['domain'] = [('res_model', '=', 'account.bank.statement.line'), ('res_id', 'in', self.ids)]  # noqa: E501
        res['context'] = {'default_res_model': 'account.bank.statement.line', 'default_res_id': self.id}  # noqa: E501
        return res
        
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'account.bank.statement.line'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])  # noqa: E501
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)  # noqa: E501
        for expense in self:
            expense.attachment_number = attachment.get(expense._origin.id, 0)

    

    
