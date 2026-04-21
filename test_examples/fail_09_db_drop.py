def clean_db(self):
    cursor.execute('DROP TABLE users;') # TODO fix this hack
