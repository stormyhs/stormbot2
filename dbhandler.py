import pymongo
import funcs

class db_handler:
    def __init__(self):
        dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = dbclient["stormbotdb"]
        self.users = db["users"]
        r = self.users.find({}, {"_id": 0})

    def create_account(self, id):
        r = self.users.find_one({"id": id})
        if(r is None):
            self.users.insert_one({"id": id, "credits": 100, "workcd": 0})
        else:
            pass

    def delete_account(self, ctx):
        self.users.remove_one({"id": ctx.author.id})

    def account_exists(self, id):
        r = self.users.find_one({"id": id})
        if(r is None):
            return False
        return True

    def get_value(self, id, value):
        self.create_account(id)
        r = self.users.find_one({"id": id})
        try:
            return r[value]
        except:
            return False

    def set_value(self, id, key, value):
        self.create_account(id)
        self.users.update_one({"id": id}, {"$set": {key: value}})

    def add_credits(self, id, value):
        r = self.users.find_one({"id": id})
        if(r is None):
            self.create_account(id)
            r = self.users.find_one({"id": id})
        self.users.update_one({"id": id}, {"$set": {"credits": r["credits"] + value}})

    def cool_balance(self, id):
        self.create_account(id)
        r = self.users.find_one({"id": id})
        return f"**◈{funcs.dotnumbers(r['credits'])}**"
