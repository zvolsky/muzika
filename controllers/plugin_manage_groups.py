# -*- coding: utf-8 -*-

def index():
    if not ADMIN_GROUP:
        return T('use syntax: plugin_manage_groups/group/<groupname> --or-- set ADMIN_GROUP in models/plugin_manage_groups_sure_admin')
    redirect(URL('group', args=ADMIN_GROUP))

@auth.requires_membership(ADMIN_GROUP)
def group():
    if 1<=len(request.args)<=2:   # 2 reserved for description
        groups = db(db.auth_group.role==request.args[0]).select()
        if groups:
            selected_id = groups.first().id
        else:
            selected_id = db.auth_group.insert(role=request.args[0])
            db.commit()

        groups = db(db.auth_group).select(orderby=db.auth_group.role)
        member_counts = {}
        count = db.auth_membership.group_id.count()
        member_counts_db = db(db.auth_membership).select(
                db.auth_membership.group_id, count,
                orderby=db.auth_membership.group_id,
                groupby=db.auth_membership.group_id
                )
        for membership in member_counts_db:
            member_counts[membership.auth_membership.group_id] = membership[count]

        order_users = db.auth_user.username if auth.settings.use_username else db.auth_user.email
        users = db(db.auth_user).select(orderby=order_users)
        members = db((db.auth_membership.id==selected_id) & (db.auth_user.id==db.auth_membership.user_id)).select(db.auth_user.id)
        for user in users:
            user_id = user.id
            for member in members:
                if member.id==user_id:
                    user.is_member = True
                    break
            else:
                user.is_member = False

        return {'groups': groups, 'member_counts': member_counts, 'users': users, 'members': members}
    else:
        return T('use syntax: plugin_manage_groups/group/<groupname>')

@auth.requires_membership(ADMIN_GROUP)
def delgroup():
    if len(request.args)==1:
        del db.auth_group[request.args[0]]
        db(db.auth_membership.group_id==request.args[0]).delete()  # called for empty group only - but be sure - maybe somebody has changed this?

    if ADMIN_GROUP:
        redirect(URL('group', args=ADMIN_GROUP))
    else:
        redirect(URL('default', 'index'))
