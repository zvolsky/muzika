# -*- coding: utf-8 -*-

plugin_manage_groups_FIRST_ADMIN = True
plugin_manage_groups_ADMIN_GROUP = 'admin'

if plugin_manage_groups_FIRST_ADMIN and plugin_manage_groups_ADMIN_GROUP and "auth" in locals() and auth.user_id:
    if not auth.id_group(plugin_manage_groups_ADMIN_GROUP):
        auth.add_membership(auth.add_group(plugin_manage_groups_ADMIN_GROUP), auth.user_id)
