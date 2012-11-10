from utilities import get_cursor
import pdb

def main():
    """
    Drops the current sandbox database and creates it again by copying maintain.
    The user required is `maintain_sb`, which has read-only access to maintain and
    the ability to drop and create tables in maintain_sb.
    """
    msb = get_cursor("maintain_sb")

    msb.execute("DROP DATABASE maintain_sb")
    msb.execute("CREATE DATABASE maintain_sb")
    msb.execute("SHOW TABLES IN maintain")
    for table, in msb.fetchall():
        print "Creating %s..." % table

        table = "`%s`" % table
        sql = "CREATE TABLE maintain_sb.{0} LIKE maintain.{0}".format(table)
        msb.execute(sql)
        sql = "INSERT INTO maintain_sb.{0} SELECT * FROM maintain.{0}".format(table)
        msb.execute(sql)

if __name__ == "__main__":
    main()
