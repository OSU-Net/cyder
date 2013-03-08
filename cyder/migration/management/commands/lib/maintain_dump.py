from utilities import get_cursor


def main():
    """
    Drops the current sandbox database and creates it again by copying
    maintain. The user required is `maintain_sb`, which has read-only access to
    maintain and the ability to drop and create tables in maintain_sb.
    """
    msb = get_cursor("maintain_sb")
    msb.execute("DROP DATABASE maintain_sb")
    msb.execute("CREATE DATABASE maintain_sb")
    msb.execute("SHOW TABLES IN maintain")

    for table, in msb.fetchall():
        if table in ["bandwidth_usage", "session", "host_history"]:
            continue
        print "Creating %s..." % table

        table = "`%s`" % table
        sql = "CREATE TABLE maintain_sb.{0} LIKE maintain.{0}".format(table)
        msb.execute(sql)
        msb.execute("INSERT INTO maintain_sb.{0} "
                    "SELECT * FROM maintain.{0}".format(table))


if __name__ == "__main__":
    main()
