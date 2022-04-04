from odoo import api, fields, models, _
from datetime import date


class HospitalChangeRoom(models.Model):
    _name = 'hospital.change.room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Change Room'
    _rec_name = 'change_room_reference'

    change_room_reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                                        default=lambda self: _('New'))
    date_change_room = fields.Date(string="Date", default=fields.Date.today(), readonly=True)                     
    checkin_id = fields.Many2one(comodel_name='hospital.reservation', string='Check In ID')
    checkup_id = fields.Many2one('hospital.checkup', string='Check Up', related='checkin_id.checkup_id')
    responsible_id = fields.Many2one('res.partner', string='Responsible', related='checkin_id.responsible_id')
    date_checkin = fields.Date(string='Date Check In', related="checkin_id.date_reservation")
    patient_id = fields.Many2one(comodel_name='hospital.patient', string='Patient', related="checkin_id.patient_id")
    room_id_old = fields.Many2one(comodel_name='hospital.room', string='Room Out', related="checkin_id.room_id")
    room_price_old = fields.Integer(string='Price/Day', related="checkin_id.room_price")
    stay_old = fields.Integer(string='Stay')
    total_price_old = fields.Integer(compute="_total_price_old_compute", string="Total Check Out")

    room_id_new = fields.Many2one('hospital.room', 
                            string='Room In', 
                            domain=[('available','=', True)])
    room_price_new = fields.Integer(string='Price/Day', related="room_id_new.price")
    note = fields.Char(string='Description')
    state =  fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), 
                                ('done', 'Done'), ('cancel', 'Canceled')], 
                                tracking=True, 
                                default='draft', 
                                string='Status')

    @api.model
    def create(self, vals): 
        if not vals.get('note'):
            vals['note'] = "New Change Room"
        if vals.get('change_room_reference', _('New')) == _('New'):
            vals['change_room_reference'] = self.env['ir.sequence'].next_by_code('hospital.change.room') or _('New')
        record = super(HospitalChangeRoom, self).create(vals)
        if record.date_change_room:
            vals_checkin = {
            'checkup_id' : record.checkup_id.id,
            'room_id' : record.room_id_new.id,
            'room_price' : record.room_price_new,
            'patient_id' : record.patient_id.id,
            'responsible_id' : record.responsible_id.id,
            'note' : record.note
            }
            vals_checkout = {
            'checkin_id' : record.checkin_id.id,
            'room_id' : record.room_id_old.id,
            'room_price' : record.room_price_old,
            'patient_id' : record.patient_id.id,
            'responsible_id' : record.responsible_id.id,
            'date_reservation' : record.date_checkin,
            'stay' : record.stay_old,
            'total_price' : record.total_price_old,
            'note' : record.note
            }
            self.env['hospital.reservation'].create(vals_checkin)
            self.env['hospital.checkout'].create(vals_checkout)
            self.env['hospital.room'].search([('id','=',record.room_id_old.id)]).write({'available':True})
            self.env['hospital.room'].search([('id','=',record.room_id_new.id)]).write({'available':False})
            self.env['hospital.patient'].search([('id','=',record.patient_id.id)]).write({'state':'checkin'})
            self.env['hospital.checkup'].search([('id','=',record.checkup_id.id)]).write({'state':'done'})
        return record

    @api.depends('stay_old', 'room_price_old')
    def _total_price_old_compute(self):
        for record in self:
            record.total_price_old = record.stay_old * record.room_price_old

    def action_confirm(self):
        self.state = 'confirm'
        
    def action_draft(self):
        self.state = 'draft'
        
    def action_done(self):
        self.state = 'done'
        
    def action_cancel(self):
        self.state = 'cancel'