def ctnr_delete_session(request, obj):
    if request.session['ctnr'] == obj:
        request.session['ctnr'] = request.session['ctnrs'][1]
    request.session['ctnrs'].remove(obj)
    request.session.modified = True
    return request


def ctnr_create_session(request, ctnr):
    request.session['ctnrs'].append(ctnr)
    request.session.modified = True
    return request
