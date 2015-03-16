# -*- coding: utf-8 -*-

db.define_table('misto',
    Field('misto', length=50),
    format = '%(misto)s (%(id)s)'
    )

db.define_table('rozpis',
    Field('auth_user_id', db.auth_user),
    Field('misto_id', db.misto),
    Field('zacatek', 'datetime'),            
    )
