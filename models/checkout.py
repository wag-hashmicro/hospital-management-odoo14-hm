from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError

class HospitalCheckout(models.Model):
    _name = 'hospital.checkout'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Check Out'
    _rec_name = 'checkout_reference'

    checkout_reference = fields.Char(string="Reference", required=True, copy=False, readonly=True, 
                                    default=lambda self: _('New'))
    date_checkout = fields.Date(string="Date", default=date.today(), readonly=True)
    checkin_id = fields.Many2one('hospital.reservation',string='Check In')
    room_id = fields.Many2one(comodel_name='hospital.room', 
                            string='Room', related="checkin_id.room_id")
    room_price = fields.Integer(string='Price/Day', related='checkin_id.room_price')
    patient_id = fields.Many2one('hospital.patient', string='Patient', related="checkin_id.patient_id")
    responsible_id = fields.Many2one('res.partner', string='Responsible', related='checkin_id.responsible_id')
    date_reservation = fields.Date(string="Date", related="checkin_id.date_reservation")
    note = fields.Char(string='Description')
    state =  fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), 
                                ('done', 'Done'), ('cancel', 'Canceled')], 
                                tracking=True, 
                                default='draft', 
                                string='Status')
    stay = fields.Integer(string='Length of Stay')    
    total_price = fields.Integer(compute='_price_compute', string='Total')

    @api.depends('stay', 'room_price')
    def _price_compute(self):
        for record in self:
            record.total_price = record.stay * record.room_price

    @api.model
    def create(self, vals): 
        if not vals.get('note'):
            vals['note'] = "New Check Out"
        if vals.get('checkout_reference', _('New')) == _('New'):
            vals['checkout_reference'] = self.env['ir.sequence'].next_by_code('hospital.checkout') or _('New')
        record = super(HospitalCheckout, self).create(vals)
        if record.date_checkout:
            self.env['hospital.room'].search([('id','=',record.room_id.id)]).write({'available':True})
            self.env['hospital.patient'].search([('id','=',record.patient_id.id)]).write({'state':'done'})
            self.env['hospital.reservation'].search([('id','=',record.checkin_id.id)]).write({'state':'done'})
        return record

    def action_confirm(self):
        self.state = 'confirm'
        
    def action_draft(self):
        self.state = 'draft'
        
    def action_done(self):
        self.state = 'done'
        self.env['hospital.patient'].search([('id','=',self.patient_id.id)]).write({'state':'done'})
        
    def action_cancel(self):
        self.state = 'cancel'
        self.env['hospital.patient'].search([('id','=',self.patient_id.id)]).write({'state':'cancel'})