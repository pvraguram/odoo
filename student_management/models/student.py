from odoo import models, fields

class Student(models.Model):
    _name = "student.management"
    _description = "Student"

    name = fields.Char(string="Student Name", required=True)