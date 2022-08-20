import pymongo
import funcs

# TODO: clean this up
# There is unneeded stuff both here and in funcs.py

class db_handler:
    def __init__(self):
        self.running = 0

        dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = dbclient["stormbotdb"]
        self.users = db["users"]
        r = self.users.find({}, {"_id": 0})
        # if(r is not None):
            # for user in r:
                # print(user)

    def create_account(self, id):
        # print(f"Creating account {id}")
        r = self.users.find_one({"id": id})
        # print(f"r: {r}")
        if(r is None):
            # print(f"Created account {id}")
            self.users.insert_one({"id": id, "credits": 100, "workcd": 0})
        else:
            pass
            # print(f"Account exists: {id}")
            # print(r)

    def delete_account(self, ctx):
        # print(f"Deleting account {str(ctx.author.name)} {str(ctx.author.id)}")
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
