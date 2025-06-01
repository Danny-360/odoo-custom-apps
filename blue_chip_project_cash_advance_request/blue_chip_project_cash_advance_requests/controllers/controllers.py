# -*- coding: utf-8 -*-
# from odoo import http


# class Blue-chip-cash-advance(http.Controller):
#     @http.route('/blue-chip-cash-advance/blue-chip-cash-advance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/blue-chip-cash-advance/blue-chip-cash-advance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('blue-chip-cash-advance.listing', {
#             'root': '/blue-chip-cash-advance/blue-chip-cash-advance',
#             'objects': http.request.env['blue-chip-cash-advance.blue-chip-cash-advance'].search([]),
#         })

#     @http.route('/blue-chip-cash-advance/blue-chip-cash-advance/objects/<model("blue-chip-cash-advance.blue-chip-cash-advance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('blue-chip-cash-advance.object', {
#             'object': obj
#         })
