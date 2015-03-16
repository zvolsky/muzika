# -*- coding: utf-8 -*-

ROZPIS_HEADERS = {
                'rozpis.id': 'id',
                'rozpis.auth_user_id': 'muzikant',
                'rozpis.misto_id': 'misto',
                'rozpis.zacatek': 'zacatek',
            }

@auth.requires_login()
def index():
    response.view = 'default/rozpis.html'
    return dict(grid=SQLFORM.grid(db.rozpis.auth_user_id==auth.user_id,
            orderby=db.rozpis.zacatek,
            showbuttontext=False,
            create=False,
            editable=False,
            deletable=False,
            searchable=False,
            headers=ROZPIS_HEADERS
            ))

#@auth.requires_membership('rozpis')
def rozpis():
    return dict(grid=SQLFORM.grid(db.rozpis,
            orderby=db.rozpis.zacatek,
            showbuttontext=False,
            searchable=False,
            headers=ROZPIS_HEADERS
            ))

@auth.requires_membership('admin')
def mista():
    response.view = 'default/ciselnik.html'
    return dict(grid=SQLFORM.grid(db.misto,
            showbuttontext=False,
            searchable=False
            ))

@auth.requires_membership('admin')
def muzikanti():
    response.view = 'default/ciselnik.html'
    return dict(grid=SQLFORM.grid(db.auth_user,
            showbuttontext=False,
            searchable=False
            ))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
