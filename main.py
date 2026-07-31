from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI(title="Smart Expense Tracker API")

FILE_NAME = "src/expenses.json"


class Expense(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    date: str


def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []

    with open(FILE_NAME, "r") as f:
        try:
            return json.load(f)
        except:
            return []


def save_expenses(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)


@app.get("/")
def home():
    return {"message": "Expense Tracker API Running"}


@app.post("/expenses")
def add_expense(expense: Expense):
    expenses = load_expenses()

    for e in expenses:
        if e["id"] == expense.id:
            raise HTTPException(status_code=400, detail="Expense ID already exists")

    expenses.append(expense.dict())
    save_expenses(expenses)

    return {"message": "Expense Added Successfully"}


@app.get("/expenses")
def get_expenses():
    return load_expenses()


@app.get("/expenses/category/{category}")
def filter_category(category: str):
    expenses = load_expenses()

    result = [
        e for e in expenses
        if e["category"].lower() == category.lower()
    ]

    return result


@app.get("/expenses/total")
def total_expenses():
    expenses = load_expenses()

    total = sum(e["amount"] for e in expenses)

    category_total = {}

    for e in expenses:
        category_total[e["category"]] = category_total.get(
            e["category"], 0
        ) + e["amount"]

    return {
        "overall_total": total,
        "by_category": category_total
    }


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    expenses = load_expenses()

    new_list = [e for e in expenses if e["id"] != expense_id]

    if len(new_list) == len(expenses):
        raise HTTPException(status_code=404, detail="Expense not found")

    save_expenses(new_list)

    return {"message": "Expense Deleted Successfully"}