# -*- coding: utf-8 -*-

LIMIT_HIDE_USERS = 251
LIMIT_DENSE_ROWS = 11

table_user = auth.table_user()
table_group = auth.table_group()
table_membership = auth.table_membership()

def index():
    if not ADMIN_GROUP:
        return T('use syntax: plugin_manage_groups/group/<groupname> --or-- set ADMIN_GROUP in models/plugin_manage_groups_sure_admin')
    redirect(URL('group', args=ADMIN_GROUP))

@auth.requires_membership(ADMIN_GROUP)
def group():
    if 1<=len(request.args)<=2:   # 2 reserved for description
        groups = db(table_group.role==request.args[0]).select()
        if groups:
            group_id = groups.first().id
        else:
            group_id = table_group.insert(role=request.args[0])
            db.commit()

        groups = db(table_group).select(orderby=table_group.role)
        member_counts = {}
        count = table_membership.group_id.count()
        member_counts_db = db(table_membership).select(
                table_membership.group_id, count,
                orderby=table_membership.group_id,
                groupby=table_membership.group_id
                )
        for membership in member_counts_db:
            member_counts[membership.auth_membership.group_id] = membership[count]

        order_users = table_user.username if auth.settings.use_username else table_user.email
        users = db(table_user).select(orderby=order_users, limitby=(0, LIMIT_HIDE_USERS))
        member_fields = [table_user.username, table_user.email] if auth.settings.use_username else [table_user.email]
        members = db((table_membership.group_id==group_id) & (table_user.id==table_membership.user_id)).select(
                table_user.id, *member_fields, orderby=order_users)
        if len(users)>=LIMIT_HIDE_USERS:
            large = SQLFORM.factory(Field('candidate'), label=T("Add user:"))
            if large.process().accepted:
                session.flash(T("Cannot find the user."))
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
                'large': large, 'limit_dense': LIMIT_DENSE_ROWS, 'cnt_candidates': cnt_candidates,
                'group_id': group_id, 'manage_me': request.args[0]!=ADMIN_GROUP}
    else:
        return T('use syntax: plugin_manage_groups/group/<groupname>')

@auth.requires_membership(ADMIN_GROUP)
def delgroup():
    if len(request.args)==1:
        del table_group[request.args[0]]
        db(table_membership.group_id==request.args[0]).delete()  # called for empty group only - but be sure - maybe somebody has changed this?
    if ADMIN_GROUP:
        redirect(URL('group', args=ADMIN_GROUP))
    else:
        redirect(URL('default', 'index'))

@auth.requires_membership(ADMIN_GROUP)
def addms():
    if len(request.args)==2 and not db((table_membership.group_id==request.args[0]) & (table_membership.user_id==request.args[1])).select():
        table_membership.insert(group_id=request.args[0], user_id=request.args[1])
    __reload_group(request.args[0])

@auth.requires_membership(ADMIN_GROUP)
def delms():
    if len(request.args)==2:
        db((table_membership.group_id==request.args[0]) & (table_membership.user_id==request.args[1])).delete()
    __reload_group(request.args[0])

def __reload_group(group_id):
    redirect(URL('group', args=db(table_group.id==group_id).select(table_group.role).first().role))