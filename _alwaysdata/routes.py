#!/usr/bin/python
# -*- coding: utf-8 -*-

default_application = 'muzika'    # ordinarily set in base routes.py
default_controller = 'default'  # ordinarily set in app-specific routes.py
default_function = 'index'      # ordinarily set in app-specific routes.py

routes_in = (
  ('/$anything', '/muzika/$anything'),
  ('*./favicon.ico', '/muzika/static/images/favicon.ico'),
  ('*./favicon.png', '/muzika/static/images/favicon.png'),
  ('*./robots.txt', '/muzika/static/robots.txt'),
  )

routes_out = [(x, y) for (y, x) in routes_in[:-3]]
