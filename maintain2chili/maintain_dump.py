from utilities import get_cursor
import pdb

def main():
    msb = get_cursor("maintain_sb")

    msb.execute("drop database maintain_sb")
    msb.execute("create database maintain_sb")
    msb.execute("show tables in maintain")
    for table, in msb.fetchall():
        print "Creating %s..." % table

        '''
        sql = "create table maintain_sb.{0} select * from maintain.{0}".format(table)
        msb.execute(sql)
        '''

        table = "`%s`" % table
        sql = "create table maintain_sb.{0} like maintain.{0}".format(table)
        msb.execute(sql)
        sql = "insert into maintain_sb.{0} select * from maintain.{0}".format(table)
        msb.execute(sql)

if __name__ == "__main__":
    main()
