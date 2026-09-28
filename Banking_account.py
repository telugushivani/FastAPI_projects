from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel,Field
from bson import ObjectId




app=FastAPI()

cilent=MongoClient("mongodb://localhost:27017/")
db=cilent["bank_account"]
collection=db["account"]


class account(BaseModel):
    account_holder: str
    account_number: str
    balance: int=Field(default=0)


@app.post("/accounts")    
def create_account(account:account):
    account_data=account.model_dump()
    result = collection.insert_one(account_data)

    return {
            "message":"account created sucessfully",
            "id":str(result.inserted_id)
        }
    

@app.get("/accounts")
def get_account():
    accounts=list(collection.find())
    for account in accounts:
        account["_id"] = str(account["_id"])
    return accounts


@app.get("/accounts/{id}")
def get_account(id):
    accounts=collection.find_one(
        {"_id": ObjectId(id)},  # filter: WHERE _id equals this ObjectId
        {
            "_id": 1,
            "account_holder":1,
            "account_number":1,
            "balance":1,
                        
        },
    )
    if accounts:
        accounts["_id"] = str(accounts["_id"])
        return {"accounts": accounts, "message": "found"}
    else:
        return {"message": "not found"}


@app.put("/accounts/{id}")
def update_account(id:str,update_account: account):
    object_id = ObjectId(id)
    account_data =update_account.model_dump()
    result = collection.update_one(
            {"_id": object_id},
            {
                "$set": account_data
            }
        )
    return {
            "message": "account updated successfully"
        }


@app.delete("/accounts/{id}")
def delete_expense(id: str):

    object_id = ObjectId(id)

    result = collection.delete_one(
        {"_id": object_id}
    )
    if result.deleted_count > 0:
        return {"message": "account deleted successfully"}
    else:
        return {"message":"Failed to delete account"}
    
@app.delete("/accounts")
def delete_all_accounts():

    result = collection.delete_many({})

    return {
        "message": "All accounts deleted successfully",
        "deleted_count": result.deleted_count
    }
