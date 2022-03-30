from odoo import api, fields, models, _
from datetime import date

class HospitalReservation(models.Model):
    _name = 'hospital.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Reservation Room'
    _rec_name = 'reservation_reference'

    reservation_reference = fields.Char(string="Reservation Reference", required=True, copy=False, readonly=True, 
                                        default=lambda self: _('New'))
    date_reservation = fields.Date(string="Date", default=date.today(), readonly=True)
    room_id = fields.Many2one('hospital.room', 
                            string='Room', 
                            domain=[('available','=', True)])
    checkup_id = fields.Many2one('hospital.checkup', string='Check Up')
    room_price = fields.Integer(string='Price/Day', related='room_id.price')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    responsible_id = fields.Many2one('res.partner', string='Responsible', related='patient_id.responsible_id')
    estimated_stay = fields.Integer(string='Estimated Stay')
    total_price = fields.Integer(compute='_price_compute', string='Total')
    note = fields.Char(string='Description')
    state =  fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), 
                                ('done', 'Done'), ('cancel', 'Canceled')], 
                                tracking=True, 
                                default='draft', 
                                string='Status')
    
    def action_show_create_checkout(self):
        return {
            "name": ("Create Check Out"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "create.checkout.wizard",
            "target": "new",
            "views": [[self.env.ref('om_hospital.view_create_checkout_form').id, "form"]],
        }

    @api.model
    def create(self, vals): 
        if not vals.get('note'):
            vals['note'] = "New Reservation"
        if vals.get('reservation_reference', _('New')) == _('New'):
            vals['reservation_reference'] = self.env['ir.sequence'].next_by_code('hospital.reservation') or _('New')
        record = super(HospitalReservation, self).create(vals)
        if record.date_reservation:
            self.env['hospital.room'].search([('id','=',record.room_id.id)]).write({'available':False})
            self.env['hospital.patient'].search([('id','=',record.patient_id.id)]).write({'state':'checkin'})
            self.env['hospital.checkup'].search([('id','=',record.checkup_id.id)]).write({'state':'done'})
        return record

    def unlink(self):
        for record in self:
            self.env['hospital.room'].search([('id','=',record.room_id.id)]).write({'available':True})
            self.env['hospital.patient'].search([('id','=',record.patient_id.id)]).write({'state':'done'})
        record = super(HospitalReservation, self).unlink()

    @api.depends('estimated_stay', 'room_price')
    def _price_compute(self):
        for record in self:
            record.total_price = record.estimated_stay * record.room_price

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