# -*- coding: utf-8 -*-

import datetime

def prehled():
    '''muzikant int'''
    try:
        return {'problem': '',
                'rozpis': db(db.rozpis.auth_user_id==request.vars.muzikant).select().as_list()}
    except Exception as err:
        return {'problem': err.message}

def vloz():
    '''muzikant int, misto int, zacatek rrrrmmddhhmm'''
    try:
        return {'problem': '', 'id': int(db.rozpis.insert(
                auth_user_id=request.vars.muzikant,
                misto_id=request.vars.misto,
                zacatek=datetime.datetime.strptime(request.vars.zacatek, '%Y%m%d%H%M'),
                ))}
    except Exception as err:
        return {'problem': err.message}

def uprav():
    '''id, (muzikant int), (misto int), (zacatek rrrrmmddhhmm)'''
    zmeny = {}
    if request.vars.muzikant:
        zmeny['auth_user_id'] = request.vars.muzikant
    if request.vars.misto:
        zmeny['misto_id'] = request.vars.misto
    if request.vars.zacatek:
        zmeny['zacatek'] = datetime.datetime.strptime(request.vars.zacatek, '%Y%m%d%H%M')
    try:
        db.rozpis[request.vars.id] = zmeny
        return {'problem': ''}
    except Exception as err:
        return {'problem': err.message}

def zrus():
    '''id'''
    try:
        del db.rozpis[request.vars.id]
        return {'problem': ''}
    except Exception as err:
        return {'problem': err.message}
