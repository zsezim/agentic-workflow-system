from fastapi import FastAPI
from src.models.schemas import ProductionOrder
from src.graph.workflow import process_order

app = FastAPI(title="Agentic Workflow Orchestrator")


@app.post("/orders/process")
def process_production_order(order: ProductionOrder):
    return process_order(order)