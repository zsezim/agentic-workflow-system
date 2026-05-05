from fastapi import FastAPI
from src.models.schemas import ProductionOrder
from src.graph.workflow import process_order
from src.graph.langgraph_workflow import process_order_with_langgraph

app = FastAPI(title="Agentic Workflow Orchestrator")


@app.post("/orders/process")
def process_production_order(order: ProductionOrder):
    return process_order(order)


@app.post("/orders/process-agentic")
def process_production_order_agentic(order: ProductionOrder):
    return process_order_with_langgraph(order)