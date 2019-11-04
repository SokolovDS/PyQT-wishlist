import pymysql


class Database:
    def __init__(self,
                 host='localhost',
                 user='root',
                 db='wishlist'):
        self.connection = pymysql.connect(host=host,
                                          user=user,
                                          db=db)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""  CREATE TABLE IF NOT EXISTS wishes(
                            ID INT NOT NULL AUTO_INCREMENT,
                            Name TEXT,
                            Cost INT,
                            Link TEXT,
                            Note TEXT,
                            PRIMARY KEY(ID))""")

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            self.connection.rollback()

    def query(self, query):
        cursor = self.cursor
        cursor.execute(query)

        return cursor.fetchall()

    def __del__(self):
        self.connection.close()


class Wishes(Database):
    def __init__(self):
        Database.__init__(self)


if __name__ == "__main__":

    db = Database()

    # Data Insert into the table
    insert_query = """
        INSERT INTO wishes
        (Name, Cost, Link, Note)
        VALUES ('Car', 1000, NULL, 'MyCar')
        """

    insert_query1 = """
        INSERT INTO wishes
        (Name, Cost, Link, Note)
        VALUES ('{0:s}', {1:d}, '{2}', '{3:s}')
        """.format('Car', 1000, None, 'MyCar')

    # db.query(query)
    # db.insert(insert_query)
    # db.insert(insert_query1)

    # Data retrieved from the table
    select_query = """SELECT * FROM wishes"""

    wishes = db.query(select_query)

    for wish in wishes:
        print(wish)
