from odoo import fields, models


class Student(models.Model):
    _name = 'student.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Student Name', required=True, tracking=True)
    student_id = fields.Char(string='Student ID', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth')
    email = fields.Char(string='Email')
