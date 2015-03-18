# -*- coding: utf-8 -*-

plugin_manage_groups_LIMIT_HIDE_USERS = 3
plugin_manage_groups_LIMIT_DENSE_ROWS = 2

plugin_manage_groups_table_user = auth.table_user()
plugin_manage_groups_table_group = auth.table_group()
plugin_manage_groups_table_membership = auth.table_membership()

def index():
    if not plugin_manage_groups_ADMIN_GROUP:
        return T('use syntax: plugin_manage_groups/group/<groupname> --or-- set plugin_manage_groups_ADMIN_GROUP in models/plugin_manage_groups.py')
    redirect(URL('group', args=plugin_manage_groups_ADMIN_GROUP))

@auth.requires_membership(plugin_manage_groups_ADMIN_GROUP)
def group():
    if 1<=len(request.args)<=2:   # 2 reserved for description
        groups = db(plugin_manage_groups_table_group.role==request.args[0]).select()
        if groups:
            group_id = groups.first().id
        else:
            group_id = plugin_manage_groups_table_group.insert(role=request.args[0])
            db.commit()

        groups = db(plugin_manage_groups_table_group).select(orderby=plugin_manage_groups_table_group.role)
        member_counts = {}
        count = plugin_manage_groups_table_membership.group_id.count()
        member_counts_db = db(plugin_manage_groups_table_membership).select(
                plugin_manage_groups_table_membership.group_id, count,
                orderby=plugin_manage_groups_table_membership.group_id,
                groupby=plugin_manage_groups_table_membership.group_id
                )
        for membership in member_counts_db:
            member_counts[membership.auth_membership.group_id] = membership[count]

        order_users = plugin_manage_groups_table_user.username if auth.settings.use_username else plugin_manage_groups_table_user.email
        users = db(plugin_manage_groups_table_user).select(orderby=order_users, limitby=(0, plugin_manage_groups_LIMIT_HIDE_USERS))
        member_fields = [plugin_manage_groups_table_user.username, plugin_manage_groups_table_user.email] if auth.settings.use_username else [plugin_manage_groups_table_user.email]
        members = db((plugin_manage_groups_table_membership.group_id==group_id) & (plugin_manage_groups_table_user.id==plugin_manage_groups_table_membership.user_id)).select(
                plugin_manage_groups_table_user.id, *member_fields, orderby=order_users)
        if len(users)>=plugin_manage_groups_LIMIT_HIDE_USERS:
            large = SQLFORM.factory(
                    Field('candidate', label=(T("User") if auth.settings.use_username else T("E-mail"))),
                    submit_button=T("Find and add the user"))
            if large.process().accepted:
                if form.vars.candidate:
                    pattern = form.vars.candidate.lower()
                    new_member = db(plugin_manage_groups_table_user.email.lower()==pattern).select().first() if ('@' in pattern) else None
                    if not new_member:
                        if auth.settings.use_username:
                            new_member = db(plugin_manage_groups_table_user.username.lower()==pattern).select().first()
                    if not new_member:
                        candidates = db(plugin_manage_groups_table_user.email.lower().like(pattern+'%')).select()
                        if auth.settings.use_username:
                            candidates = candidates | db(plugin_manage_groups_table_user.username.lower().like(pattern+'%')).select()
                        first_candidate = candidates.first()
                        if first_candidate:
                            if len(candidates)==1:
                                new_member = first_candidate
                            else:
                                session.flash = T("Ambiguous candidate user.")
                        else:
                            session.flash = T("Cannot find the user.")
                    if new_member:
                        __addms(group_id, new_member.id)
                redirect(URL(args=request.args)) # re-read
            cnt_candidates = 'many' # must be non empty
        else:
            large = None
            cnt_candidates = 0
            for user in users:
                user_id = user.id
                for member in members:
                    if member.id==user_id:
                        user.is_member = True
                        break
                else:
                    user.is_member = False
                    cnt_candidates += 1

        return {'groups': groups, 'member_counts': member_counts, 'users': users, 'members': members,
                'large': large, 'limit_dense': plugin_manage_groups_LIMIT_DENSE_ROWS, 'cnt_candidates': cnt_candidates,
                'group_id': group_id, 'manage_me': request.args[0]!=plugin_manage_groups_ADMIN_GROUP}
    else:
        return T('use syntax: plugin_manage_groups/group/<groupname>')

@auth.requires_membership(plugin_manage_groups_ADMIN_GROUP)
def delgroup():
    if len(request.args)==1:
        del plugin_manage_groups_table_group[request.args[0]]
        db(plugin_manage_groups_table_membership.group_id==request.args[0]).delete()  # called for empty group only - but be sure - maybe somebody has changed this?
    if plugin_manage_groups_ADMIN_GROUP:
        redirect(URL('group', args=plugin_manage_groups_ADMIN_GROUP))
    else:
        redirect(URL('default', 'index'))

@auth.requires_membership(plugin_manage_groups_ADMIN_GROUP)
def addms():
    if len(request.args)==2:
        __addms(request.args[0], request.args[1])
    __reload_group(request.args[0])

def __addms(group_id, user_id):
    if not db((plugin_manage_groups_table_membership.group_id==group_id) & (plugin_manage_groups_table_membership.user_id==user_id)).select():
        plugin_manage_groups_table_membership.insert(group_id=group_id, user_id=user_id)

@auth.requires_membership(plugin_manage_groups_ADMIN_GROUP)
def delms():
    if len(request.args)==2:
        db((plugin_manage_groups_table_membership.group_id==request.args[0]) & (plugin_manage_groups_table_membership.user_id==request.args[1])).delete()
    __reload_group(request.args[0])

def __reload_group(group_id):
    redirect(URL('group', args=db(plugin_manage_groups_table_group.id==group_id).select(plugin_manage_groups_table_group.role).first().role))