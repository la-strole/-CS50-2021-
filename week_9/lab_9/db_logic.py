import sqlite3


class DataBase:

    def __init__(self, db_source):
        self.db_source = db_source

    def get_name_date(self):
        """
        get name - date from all rows in birthdays.db
        :return: list of tuples like [(name, m/d), ...] where m - month, d- day
        """
        connection = sqlite3.connect(self.db_source)
        connection.row_factory = sqlite3.Row
        with connection:
            cur = connection.cursor()
            # look at table with birthdays
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchone()
            if 'birthdays' in tables:
                table_name = "birthdays"
            else:
                raise ValueError(f"birthdays table not in database tables {tables}")

            cur.execute(f"SELECT * FROM {table_name}")
            result = []

            for row in cur:
                result.append((row["name"], f'{row["month"]}/{row["day"]}'))

        connection.close()
        return result

    def insert_name_date(self, name, month, day):
        """
        insert new row to database values are name, month, day
        :return: None
        """
        assert isinstance(name, str)
        assert isinstance(month, int)
        assert isinstance(day, int)
        assert 1 <= day <= 31
        assert 1 <= month <= 12

        connection = sqlite3.connect(self.db_source)
        try:
            with connection:
                cur = connection.cursor()
                # look at table with birthdays
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cur.fetchone()
                if 'birthdays' in tables:
                    table_name = "birthdays"
                else:
                    raise ValueError(f"birthdays table not in database tables {tables}")

                # looking for max id in database
                cur.execute(f"SELECT MAX(id) FROM {table_name}")
                index = cur.fetchone()[0]
                if not index:
                    raise ValueError(f"Can not get max private key id from {table_name}")
                # add user data to db
                cur.execute(f"INSERT INTO {table_name} (id, name, month, day) VALUES (?, ?, ?, ?)",
                            (index + 1, name, month, day))
        except sqlite3.IntegrityError:
            print(f"can not add ({name},{day},{month}) to database {self.db_source} table {table_name}")
        connection.close()


if __name__ == "__main__":
    print(DataBase("birthdays.db").get_name_date())
