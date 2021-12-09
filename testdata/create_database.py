import sqlite3

conn = sqlite3.connect('database.db')
print ("Opened database successfully")

conn.execute('CREATE TABLE studentsInfo (id TEXT, name TEXT, sex TEXT, date TEXT, nation TEXT, height TEXT, idCard TEXT, PhoneNumber TEXT, address TEXT, teacher TEXT, hobbies TEXT)')
print ("Table created successfully")
conn.close()
