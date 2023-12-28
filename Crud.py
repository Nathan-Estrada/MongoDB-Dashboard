from pymongo import MongoClient

#Create CRUD class for database that for simple database manipulation in Dashboard.py
class TransactionData(object):
    def __init__(self):

        connection_string = 'mongodb://localhost:27017/db.transactions'
        DB = 'db'
        COL = 'transactions'

        self.client = MongoClient(connection_string)
        self.db = self.client['%s' % (DB)]
        self.collection = self.db['%s' % (COL)]

    def create(self, data):
            if data is not None:
                self.collection.insert_one(data)
                print("Transaction added")
                return True
            else:
                raise Exception("Data parameter is empty")

    def read(self, searchQuery):
        if searchQuery is not None:
            results = self.collection.find(searchQuery)
            return results
        else:
            print("No data entered")
            return None
        
    def update(self, searchQuery, updateQuery):
        if searchQuery is not None and updateQuery is not None:
            self.collection.update_one(searchQuery, updateQuery)
            print("Transaction updated")
            return self.collection.find(searchQuery)
        else:
            print("No data entered")
            return None
        
    def delete(self, searchQuery):
        if searchQuery is not None:
            x = self.collection.delete_many(searchQuery)
            print(x.deleted_count, "document(s) deleted")
        #Important to prevent an empty query for delete_many to avoid accidentally deleting all documents
        else:
            print("No data entered")
            return None
