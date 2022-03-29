from odoo import api, models, fields, _
from datetime import datetime

class CreateCheckinWizard(models.TransientModel):
    _name = "create.checkin.wizard"
    _description = "Create Check In Wizard"

    reservation_reference = fields.Char(string="Reservation Reference", required=True, copy=False, readonly=True, 
                                        default=lambda self: _('New'))
    date_reservation = fields.Datetime(string="Date", default=datetime.now(), readonly=True)
    room_id = fields.Many2one(comodel_name='hospital.room', 
                            string='Room', 
                            domain=[('available','=', True)])
    room_price = fields.Integer(string='Price/Day', related='room_id.price')
    checkup_id = fields.Many2one('hospital.checkup', string='Check Up')
    patient_id = fields.Many2one('hospital.patient', string='Patient', related="checkup_id.patient_id")
    responsible_id = fields.Many2one('res.partner', string='Responsible')
    estimated_stay = fields.Integer(string='Estimated Stay')
    total_price = fields.Integer(compute='_price_compute', string='Total')
    note = fields.Char(string='Description')
    state =  fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), 
                                ('done', 'Done'), ('cancel', 'Canceled')], 
                                tracking=True, 
                                default='draft', 
                                string='Status')

    @api.depends('estimated_stay', 'room_price')
    def _price_compute(self):
        for record in self:
            record.total_price = record.estimated_stay * record.room_price

    def action_create_checkin(self):
        vals = {           
            'patient_id' : self.patient_id.id,
            'room_id' : self.room_id.id,
            'checkup_id' : self.checkup_id.id,
            'room_price' : self.room_price,
            'total_price' : self.total_price,
            'estimated_stay' : self.estimated_stay,
            'date_reservation' : self.date_reservation,
            'responsible_id' : self.responsible_id.id,
            'note' : self.note,
        }
        reservation_rec = self.env['hospital.reservation'].create(vals)
        return {
            "name": ("Check In"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "hospital.reservation",
            "res_id": reservation_rec.id,
        }
        
    def action_view_checkin(self):
        #Method-1
        action = self.env.ref('om_hospital.hospital_reservation_action').read()[0]
        return action