import streamlit as st
import requests
import json

st.title("Agentic Workflow Orchestrator")

st.header("Submit Production Order")

order = {
    "order_id": st.text_input("Order ID", "ORD-1001"),
    "product_type": st.text_input("Product Type", "custom cabinet doors"),
    "material": st.selectbox("Material", ["oak", "pine", "maple", "walnut"]),
    "size": st.selectbox("Size", ["small", "medium", "large"]),
    "quantity": st.number_input("Quantity", 1, 100, 20),
    "due_date": st.text_input("Due Date", "2026-05-10"),
    "priority": st.selectbox("Priority", ["low", "normal", "high"]),
}

if st.button("Process Order"):
    response = requests.post(
        "http://127.0.0.1:8000/orders/process-agentic",
        json=order,
    )

    result = response.json()

    st.success("Order Processed!")

    st.subheader("Final Summary")
    st.write(result["final_summary"])

    st.subheader("Workflow Steps")
    for step in result["workflow_steps"]:
        st.write(f"• {step}")

    st.subheader("Decision Log")
    for decision in result["decision_log"]:
        with st.expander(decision["step"]):
            st.write("**Decision:**", decision["decision"])
            st.write("**Reason:**", decision["reason"])
            st.write("**Inputs:**")
            st.json(decision["inputs"])
            st.write("**Outputs:**")
            st.json(decision["outputs"])

    st.subheader("Key Outputs")
    st.json({
        "inventory": result["inventory"],
        "defect_risk": result["defect_risk"],
        "machine": result["machine"],
        "schedule": result["schedule"],
    })
