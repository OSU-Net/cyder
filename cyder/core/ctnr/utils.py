def ctnr_delete_session(request, ctnr):
    if request.session['ctnr'].pk == ctnr.pk:
        request.session['ctnr'] = request.session['ctnrs'][1]

    for session_ctnr in request.session['ctnrs']:
        if ctnr.pk == session_ctnr.pk:
            request.session['ctnrs'].remove(session_ctnr)

    request.session.modified = True
    return request


def ctnr_update_session(request, ctnr):
    modified = False
    for session_ctnr in request.session['ctnrs']:
        if ctnr.pk == session_ctnr.pk:
            session_ctnr.name = ctnr.name
            modified = True

    if not modified:
        request.session['ctnrs'].append(ctnr)

    if request.session['ctnr'].pk == ctnr.pk:
        request.session['ctnr'].name = ctnr.name

    request.session.modified = True
    return request
