from cyder.base.utils import get_cursor


# Set up database connection
cursor, _ = get_cursor('maintain_sb')


def find_or_insert_dname(dname):
    search_sql = "SELECT id FROM domain WHERE name = '%s'" % (dname)
    if cursor.execute(search_sql):
        domain_id, = cursor.fetchone()
        return domain_id

    cursor.execute("INSERT INTO domain (name, master_domain, enabled) "
                   "VALUES ('%s', %s, %s)" % (dname, 0, 1))
    return cursor.lastrowid


def fix_domain(dname):
    if '.' not in dname:
        # Base case
        return find_or_insert_dname(dname)
    else:
        # Make sure I exist
        domain_id = find_or_insert_dname(dname)
        _, parent = dname.split('.', 1)

        # Make sure my parent exists and is correct
        master_domain_id = fix_domain(parent)  # Make sure I'm correct
        cursor.execute("UPDATE domain "
                       "SET master_domain = '%s' "
                       "WHERE id = '%s'" % (master_domain_id, domain_id))
        return domain_id


def main():
    # Fix invalid ranges
    # This is a temporary fix for the wireless range
    # These should be resized in maintain before migration
    print 'Fixing domains...'
    cursor.execute("SELECT name FROM domain")

    for (name,) in cursor.fetchall():
        if '.in-addr.arpa' in name or name in ('', ' ', '.'):
            continue
        fix_domain(name)
