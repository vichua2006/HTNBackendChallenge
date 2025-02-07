import sqlite3

sqliteConnection = sqlite3.connect("hackers.db")

cursor = sqliteConnection.cursor()

command = "SELECT sqlite_version()"
cursor.execute(command)

# Fetch and output result
result = cursor.fetchall()
print(f'SQLite Version is {result}')

command = '''Drop TABLE hackers'''

cursor.execute(command)

sqliteConnection.commit()

# Close the cursor
cursor.close()
sqliteConnection.close()