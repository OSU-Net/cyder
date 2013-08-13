def ctnr_delete_session(request, obj):

    if request.session['ctnr'].name == obj.name:
        request.session['ctnr'] = request.session['ctnrs'][1]

    for ctnr in request.session['ctnrs']:
        if obj.name == ctnr.name:
            request.session['ctnrs'].remove(ctnr)

    request.session.modified = True
    return request


def ctnr_create_session(request, ctnr):
    request.session['ctnrs'].append(ctnr)
    request.session.modified = True
    return request
