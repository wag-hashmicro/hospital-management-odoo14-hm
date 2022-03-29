from odoo import api, fields, models, _


class HospitalRoom(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'hospital.room'
    _description = 'Hospital Room'
    _rec_name = 'room_name'

    room_reference = fields.Char(string="Room Reference", 
									required=True, copy=False, readonly=True,
									default=lambda self: _('New'))
    room_name = fields.Char(string='Name', required=True)    
    type = fields.Selection(string='Type', 
        selection=[
            ('vvip_a', 'VVIP A'),
            ('vvip_b', 'VVIP B'),
            ('vvip_c', 'VVIP C'),
            ('vip_a', 'VIP A'),
            ('vip_b', 'VIP B'),
            ('vip_c', 'VIP C'),
            ('class_a', 'Class A'),
            ('class_b', 'Class B'),
            ('class_c', 'Class C'),
            ], required=True)
    price = fields.Integer(string='Price', required=True)
    note = fields.Char(string='Description')
    image = fields.Binary(string='Image Room')
    available = fields.Boolean(string='Available', default=True)
    

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "New Room"
        if vals.get('room_reference', _('New')) == _('New'):
            vals['room_reference'] = self.env['ir.sequence'].next_by_code('hospital.room') or _('New')
        res = super(HospitalRoom, self).create(vals)
        return res

    
    
    
    
