from django.conf import settings

from utilities import get_cursor


def getexceptions():
    cursor = get_cursor("maintain_sb")
    sql = """SELECT domain.name, nameserver.name
    FROM domain, nameserver
    WHERE nameserver.name NOT LIKE "%ns_.oregonstate.edu%"
    AND nameserver.domain = domain.id"""

    cursor.execute(sql)
    return cursor.fetchall()


def checkone(name, A, B, rdtype, exceptions):
    for dname, nsname in exceptions:
        if rdtype == 'NS' and name == dname:
            if nsname in B:
                B.remove(nsname)
                if "cob-dc82" in nsname and 'cob-dc83.bus.oregonstate.edu' in B:
                    B.remove('cob-dc83.bus.oregonstate.edu')

                for ns in ['ns1.oregonstate.edu', 'ns2.oregonstate.edu']:
                    if ns in B:
                        B.remove(ns)

        elif rdtype == 'NS' and name == "oscs.orst.net":
            if "oscs.orst.net" in B:
                B.remove("oscs.orst.net")

        if rdtype == 'A' and name == nsname and '.in-addr.arpa' in dname:
            dname, _, _ = dname.rsplit('.', 2)
            dname = ".".join(reversed(dname.split('.')))
            for item in list(B):
                if item[:len(dname)] == dname:
                    B.remove(item)

        elif rdtype == 'A' and name == "bx112w38.bus.oregonstate.edu":
            B = set([])

    if B - A or A - B:
        return (rdtype, name, list(A), list(B))


def checkexcept(diffs):
    exceptions = getexceptions()
    total = 0
    unexcused = []
    remove_dot = lambda x: x[:-1] if x[-1] == "." else x
    for rdtype in diffs:
        for name in diffs[rdtype]:
            total += 1
            A = diffs[rdtype][name]['localhost']
            B = diffs[rdtype][name][settings.VERIFICATION_SERVER]

            A = set(map(remove_dot, A))
            B = set(map(remove_dot, B))
            name = remove_dot(name)

            x = checkone(name, A, B, rdtype, exceptions)
            if x:
                unexcused.append(x)

    return total, unexcused
