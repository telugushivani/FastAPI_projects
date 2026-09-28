from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel,Field
from datetime import date
from bson import ObjectId


app=FastAPI()


client=MongoClient("mongodb://localhost:27017/")
db=client["expense_tracker"]
collection=db["expense"]


class expense(BaseModel):
    amount:float=Field(gt=0)
    category:str=Field(min_length=1)
    description:str | None=None
    date:date


@app.post("/expenses")
def create_expense(expense:expense):
    expense_date = expense.model_dump()#model_dump() converts that Pydantic object into a Python dictionary:
    expense_date["date"] = expense.date.isoformat() #Get the date value from the dictionary expense_date["date"]
    #expense.date=Get the date from the Pydantic object. .isoformat()=converts the Python date into a string.
    result = collection.insert_one(expense_date)#
    

  
    return {
        "message":"expense created sucessfully",
        "id":str(result.inserted_id)
    }


@app.get("/expenses")
def get_expense():
    expenses = list(collection.find()) #collection.find() → gets all documents from MongoDB.
    #list() → converts the MongoDB cursor into a Python list.
    for expense in expenses:
        expense["_id"] = str(expense["_id"])
    return expenses    


@app.get("/expenses/{id}")
def get_expense(id):
    expenses=collection.find_one(
        {"_id": ObjectId(id)},  # filter: WHERE _id equals this ObjectId
        {
            "_id": 1,
            "amount":1,
            "category":1,
            "description":1,
            "date":1,
                    
        },
    )
    if expenses:
            expenses["_id"] = str(expenses["_id"])
            return {"expenses": expenses, "message": "found"}
    else:
            return {"message": "not found"}


@app.put("/expenses/{id}")
def update_expense(id: str, expense: expense):

    object_id = ObjectId(id)

    expense_data = expense.model_dump()

    expense_data["date"] = expense.date.isoformat()

    result = collection.update_one(
        {"_id": object_id},
        {
            "$set": expense_data
        }
    )

    return {
        "message": "Expense updated successfully"
    }


@app.delete("/expenses/{id}")
def delete_expense(id: str):

    object_id = ObjectId(id)

    result = collection.delete_one(
        {"_id": object_id}
    )
    if result.deleted_count > 0:
        return {"message": "Expense deleted successfully"}
    else:
        return {"message":"Failed to delete expense"}
     
