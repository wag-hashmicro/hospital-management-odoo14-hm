from odoo import api, models, fields, _
from datetime import date
from odoo.exceptions import ValidationError

class CreateChangeRoomWizard(models.TransientModel):
    _name = "create.change.room.wizard"
    _description = "Create Change Room Wizard"

    change_room_reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                                        default=lambda self: _('New'))
    date_change_room = fields.Date(string="Date", default=fields.Date.today(), readonly=True)                     
    checkin_id = fields.Many2one(comodel_name='hospital.reservation', string='Check In ID', readonly=True)
    checkup_id = fields.Many2one('hospital.checkup', string='Check Up', related='checkin_id.checkup_id')
    responsible_id = fields.Many2one('res.partner', string='Responsible', related='checkin_id.responsible_id')
    date_checkin = fields.Date(string='Date Check In', related="checkin_id.date_reservation")
    patient_id = fields.Many2one(comodel_name='hospital.patient', string='Patient', related="checkin_id.patient_id")
    room_id_old = fields.Many2one(comodel_name='hospital.room', string='Room Out', related="checkin_id.room_id")
    room_price_old = fields.Integer(string='Price/Day', related="checkin_id.room_price")
    stay_old = fields.Integer(compute="_stay_compute", string='Stay')
    total_price_old = fields.Integer(compute="_total_price_old_compute", string="Total Check Out")

    room_id_new = fields.Many2one('hospital.room', 
                            string='Room In', 
                            domain=[('available','=', True)])
    room_price_new = fields.Integer(string='Price/Day', related="room_id_new.price")
    note = fields.Char(string='Description')

    @api.depends('stay_old', 'room_price_old')
    def _total_price_old_compute(self):
        for record in self:
            record.total_price_old = record.stay_old * record.room_price_old

    @api.depends('date_checkin', 'date_change_room')
    def _stay_compute(self):
        for record in self:
            if record.date_checkin > record.date_change_room:
                raise ValidationError('Start date should not greater than end date.')
            else:
                length_stay = int((record.date_change_room - record.date_checkin).days)
                if length_stay == 0:
                    length_stay = 1
                record.stay_old = length_stay
    
    def action_create_change_room(self):
        vals = {           
            'checkin_id' : self.checkin_id.id,
            'checkup_id' : self.checkup_id.id,
            'responsible_id' : self.responsible_id,
            'date_checkin' : self.date_checkin,
            'patient_id' : self.patient_id.id,
            'room_id_old' : self.room_id_old.id,
            'room_price_old' : self.room_price_old,
            'stay_old' : self.stay_old,
            'total_price_old' : self.total_price_old,
            'room_id_new' : self.room_id_new.id,
            'room_price_new' : self.room_price_new,
            'note' : self.note
        }
        change_room_rec = self.env['hospital.change.room'].create(vals)
        return {
            "name": ("Change Room"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "hospital.change.room",
            "res_id": change_room_rec.id,
        }
        
    def action_view_change_room(self):
        #Method-1
        action = self.env.ref('wag_hospital.hospital_change_room_action').read()[0]
        return action