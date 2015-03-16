# -*- coding: utf-8 -*-

ADMIN_GROUP = 'admin'

if ADMIN_GROUP and "auth" in locals() and auth.user_id:
    if not auth.id_group(ADMIN_GROUP):
        auth.add_membership(auth.add_group(ADMIN_GROUP), auth.user_id)
