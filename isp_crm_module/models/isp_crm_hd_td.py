# -*- coding: utf-8 -*-

from odoo import api, fields, models
from . import isp_crm_hd_ticket_history
import datetime

AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]
AVAILABLE_RATINGS = [
    ('-2', 'Worst'),
    ('-1', 'Bad'),
    ('0', 'Neutral'),
    ('1', 'Good'),
    ('2', 'Excellent'),
]
AVAILABLE_STAGES = [
    ('0', 'New'),
    ('1', 'Doing'),
    ('2', 'Done'),
    ('3', 'Cancel'),
]
CANCEL_REQUEST_SD = [
    ('0', 'False'),
    ('1', 'True'),
]


class HelpdeskTD(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_td"
    _description = "Helpdesk Technical Department"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Request Name', required=True, index=True, copy=False, default='New')
    problem = fields.Many2one('isp_crm_module.helpdesk_td_problem',string="Problem", required=True, translate=True, ondelete='set null',help='Ticket Problem.')
    type = fields.Many2one('isp_crm_module.helpdesk_td_type', string='Type', ondelete='set null',
                                  help='Ticket Type.')
    helpdesk_ticket = fields.Many2one('isp_crm_module.helpdesk',string="Helpdesk Ticket", required=True, translate=True, ondelete='set null',help='Helpdesk Ticket.')
    description = fields.Text('Description')
    stage = fields.Many2one('isp_crm_module.helpdesk_td_stage', string='Stage', ondelete='set null',
                           help='Stage of the ticket.')
    default_stages = fields.Selection(AVAILABLE_STAGES, string="Stages",group_expand='_default_stages')
    assigned_to = fields.Many2one('hr.employee', string='Assigned To', ondelete='set null',
                                  help='Person assigned to complete the task.',track_visibility='onchange')
    team = fields.Many2one('hr.department', string='Department', store=True)
    team_leader = fields.Many2one('hr.employee', string='Team Leader', store=True)

    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange')
    customer_email = fields.Char(related='customer.email', store=True)
    customer_mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    customer_phone = fields.Char(string="Phone", related='customer.phone', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    customer_address = fields.Char(string="Address", track_visibility='onchange')
    complexity = fields.Many2one('isp_crm_module.helpdesk_td_ticket_complexity', string='Complexity', ondelete='set null',
                                  help='Complexity level of the ticket.')
    solution_ids = fields.One2many('isp_crm_module.helpdesk_td_tasks', 'problem', string="Solutions", copy=True,
                                   auto_join=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    customer_rating = fields.Selection(AVAILABLE_RATINGS, string="Rating")
    customer_feedback = fields.Text('Feedback')
    color = fields.Integer()
    cancel_request_from_sd = fields.Selection(CANCEL_REQUEST_SD, string="Cancel Request from SD")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.helpdesk_td') or '/'
            vals['default_stages'] = '0'
            # self.team_leader = self.assigned_to and self.assigned_to.parent_id
            # self.team = self.assigned_to.department_id
            # self.customer_address = self.get_customer_address_str(customer=self.customer)
        newrecord = super(HelpdeskTD, self).create(vals)
        self.env['isp_crm_module.helpdesk_td_ticket_history'].create(
            {
                'type': vals.get('type'),
                'assigned_to': vals.get('assigned_to'),
                'ticket_id': newrecord.id
            }
        )

        return newrecord

    def _default_stages(self, stages, domain, order):
        stage_ids = self._fields['default_stages'].get_values(self.env)
        return stage_ids

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.team_leader = self.assigned_to and self.assigned_to.parent_id
        self.team = self.assigned_to.department_id

    def get_customer_address_str(self, customer):
        address_str = ""
        if len(customer) > 0:
            address_str = ", ".join([
                customer.street or '',
                customer.street2 or '',
                customer.city or '',
                customer.state_id.name or '',
                customer.zip or '',
                customer.country_id.name or '',
            ])
        return address_str

    @api.onchange('customer')
    def _onchange_customer(self):
        self.customer_address = self.get_customer_address_str(customer=self.customer)

    @api.multi
    def action_mark_done_ticket_td(self):
        for helpdesk_ticket_td in self:
            helpdesk_ticket_td.update({
                'default_stages': '2',
            })

            helpdesk_ticket = helpdesk_ticket_td.env['isp_crm_module.helpdesk'].search(
                [('name', '=', helpdesk_ticket_td.helpdesk_ticket.name)])
            if helpdesk_ticket:
                pass
            else:
                helpdesk_td_problem = helpdesk_ticket.update(

                    {

                        'td_flags': '2',

                    }

                )

        return True

    @api.multi
    def action_cancel_ticket_td(self):
        for helpdesk_ticket in self:
            if helpdesk_ticket.td_flags == '1':
                helpdesk_ticket.update({
                    'default_stages': '3',
                })
        return True