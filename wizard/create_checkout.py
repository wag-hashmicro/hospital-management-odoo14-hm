from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import date

class CreateCheckoutWizard(models.TransientModel):
    _name = "create.checkout.wizard"
    _description = "Create Check Out Wizard"

    checkout_reference = fields.Char(string="Reference", required=True, copy=False, readonly=True, 
                                    default=lambda self: _('New'))
    date_checkout = fields.Date(string="Date", default=fields.Date.today(), readonly=True, force_save=True)
    checkin_id = fields.Many2one('hospital.reservation',string='Check In')
    room_id = fields.Many2one(comodel_name='hospital.room', 
                            string='Room', related="checkin_id.room_id")
    room_price = fields.Integer(string='Price/Day', related='checkin_id.room_price')
    patient_id = fields.Many2one('hospital.patient', string='Patient', related="checkin_id.patient_id")
    responsible_id = fields.Many2one('res.partner', string='Responsible', related='checkin_id.responsible_id')
    date_reservation = fields.Date(string="Date Check In", readonly=True)
    note = fields.Char(string='Description')
    
    stay = fields.Integer(compute='_stay_compute', string='Length of Stay')    
    total_price = fields.Integer(compute='_price_compute', string='Total')

    @api.depends('stay', 'room_price')
    def _price_compute(self):
        for record in self:
            record.total_price = record.stay * record.room_price

    @api.depends('date_reservation', 'date_checkout')
    def _stay_compute(self):
        for record in self:
            if record.date_reservation < record.date_checkout:
                raise ValidationError('Start date should not greater than end date.')
            else:
                length_stay = int((record.date_checkout - record.date_reservation).days)
                if length_stay == 0:
                    length_stay = 1
                record.stay = length_stay

    def action_create_checkout(self):
        vals = {           
            'patient_id' : self.patient_id.id,
            'room_id' : self.room_id.id,
            'checkin_id' : self.checkin_id.id,
            'room_price' : self.room_price,
            'total_price' : self.total_price,
            'date_reservation' : self.date_reservation,
            'date_checkout' : self.date_checkout,
            'responsible_id' : self.responsible_id.id,
            'stay' : self.stay,
            'note' : self.note,
        }
        checkout_rec = self.env['hospital.checkout'].create(vals)
        return {
            "name": ("Check Out"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "hospital.checkout",
            "res_id": checkout_rec.id,
        }
        
    def action_view_checkout(self):
        #Method-1
        action = self.env.ref('wag_hospital.hospital_checkout_action').read()[0]
        return action