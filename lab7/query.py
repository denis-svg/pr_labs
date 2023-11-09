from tinydb import TinyDB, Query
db = TinyDB('db.json')
User = Query()

print(db.search(User.today == '7'))