import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="roger891016"
)

my_cursor = mydb.cursor() # Like a robot which will do comment for you

my_cursor.execute("CREATE DATABASE our_users")
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)