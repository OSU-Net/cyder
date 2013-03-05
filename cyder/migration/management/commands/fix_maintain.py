from utilities import get_cursor


# Set up database connection
cursor = get_cursor('maintain_sb')


def find_or_insert_dname(dname):
    search_sql = "SELECT id FROM domain WHERE name = '%s'" % (dname)
    if cursor.execute(search_sql):
        domain_id, = cursor.fetchone()
        return domain_id

    cursor.execute("INSERT INTO domain (name, master_domain, enabled) "
                   "VALUES ('%s', %s, %s)" % (dname, 0, 1))
    return cursor.lastrowid


def update_master_domain(domain_id, parent_id):
    cursor.execute("UPDATE domain "
                   "SET master_domain = '%s' "
                   "WHERE id = '%s'" % (parent_id, domain_id))
    return cursor.lastrowid


def is_valid(dname):
    if '.' not in dname:
        return True
    else:
        return False


def fix_domain(dname):
    if is_valid(dname):
        # Base case
        return find_or_insert_dname(dname)

    else:
        # Make sure I exist
        domain_id = find_or_insert_dname(dname)
        _, parent = dname.split('.', 1)

        # Make sure my parent exists and is correct
        master_domain_id = fix_domain(parent)  # Make sure I'm correct
        update_master_domain(domain_id, master_domain_id)

        return domain_id


def main():
    # Fix invalid ranges
    # This is a temporary fix for the wireless range
    # These should be resized in maintain before migration
    print 'Fixing domains...'
    cursor.execute("SELECT * FROM domain")

    for _, domain, _, _ in cursor.fetchall():
        if '.in-addr.arpa' in domain or domain in ('', ' ', '.'):
            continue
        fix_domain(domain)


if __name__ == '__main__':
    main()
