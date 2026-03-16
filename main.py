from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from google_sheets import append_to_sheet, get_all_data, update_project_status, update_project_priority
from ftopsis import run_ftopsis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/submit")
async def submit_form(request: Request):
    try:
        data = await request.json()

        fields_to_process = ['llmModel', 'sizeModel', 'frameworks']

        for field in fields_to_process:
            if field in data and data[field]:
                cleaned_values = [v.strip().lower() for v in str(data[field]).split(',') if v.strip()]
                data[field] = ",".join(cleaned_values)

        if 'status' not in data:
            data['status'] = "Não iniciado"
            
        append_to_sheet(data)
        
        return {"message": "Requisição submetida com sucesso!"}
    
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        return {"error": "Erro no servidor ao processar a requisição.", "details": str(e)}

@app.patch("/api/projects/{row_index}/status")
async def update_status(row_index: int, request: Request):
    try:
        data = await request.json()
        new_status = data.get("status")
        
        if not new_status:
            return {"error": "Status não fornecido."}
        
        update_project_status(row_index, new_status)
        
        return {"message": "Status atualizado com sucesso!"}
    
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        return {"error": "Erro ao atualizar status.", "details": str(e)}

@app.patch("/api/projects/{row_index}/priority")
async def update_priority(row_index: int, request: Request):
    try:
        data = await request.json()
        new_priority = data.get("manual_priority")
        
        if not new_priority:
            return {"error": "Prioridade não fornecida."}
        
        update_project_priority(row_index, new_priority)
        
        return {"message": "Prioridade atualizada com sucesso!"}
    
    except Exception as e:
        print(f"Erro ao atualizar prioridade: {e}")
        return {"error": "Erro ao atualizar prioridade.", "details": str(e)}

@app.get("/api/priorities")
async def calculate_priorities():
    try:
        records = get_all_data()
        
        if not records:
            return {"message": "No data found."}

        valid_records = []
    
        for r in records:
            if r.get('projectTitle') and r.get('status') != "Finalizado":
                valid_records.append(r)
        
        if not valid_records:
            return [
                {
                    "projectTitle": r.get("projectTitle"),
                    "responsibleName": r.get("clientName"),
                    "email": r.get("email"),
                    "responsibleBody": r.get("organization"),
                    "status": r.get("status", "Não iniciado"),
                    "row_index": r.get("row_index"),
                    "priority_class": "N/A",
                    "proximity_to_a": 0,
                    "full_data": r
                } for r in records
            ]

        alternatives = [str(r.get("projectTitle")) for r in valid_records]
        
        # init decision matrix for each criteria
        criteria_keys = [
            "projectMaturity", "impact", "costReduction", 
            "extEfficiency", "intEfficiency", "legalRequirements", "frequency"
        ]

        valid_fuzzy_labels = ["VeryLow", "Low", "Medium", "High", "VeryHigh"]
        
        decision_matrix = {k: [] for k in criteria_keys}
        
        for r in valid_records:
            for k in criteria_keys:
                val = str(r.get(k, "Medium"))

                if val not in valid_fuzzy_labels:
                    val = "Medium" # fallback 

                decision_matrix[k].append(val)
        
        data_ftopsis = {
            "linguistic_variables_alternatives": {
                "VeryLow": [0, 0, 1, 2],
                "Low": [1, 2, 2, 3],
                "Medium": [2, 3, 4, 5],
                "High": [4, 5, 5, 6],
                "VeryHigh": [5, 6, 7, 7]
            },
            "linguistic_variables_weights": {
                "VeryLow": [0, 0, 0.1, 0.2],
                "Low": [0.1, 0.2, 0.2, 0.3],
                "Medium": [0.2, 0.3, 0.4, 0.5],
                "High": [0.4, 0.5, 0.5, 0.6],
                "VeryHigh": [0.5, 0.6, 0.7, 0.7]
            },
            "weights": {
                "projectMaturity": ["Low"],
                "impact": ["VeryHigh"],
                "costReduction": ["VeryHigh"],
                "extEfficiency": ["VeryHigh"],
                "intEfficiency": ["VeryHigh"],
                "legalRequirements": ["Low"],
                "frequency": ["Medium"]
            },
            "criteria_type": {
                "projectMaturity": "Benefit",
                "impact": "Benefit",
                "costReduction": "Benefit",
                "extEfficiency": "Benefit",
                "intEfficiency": "Benefit",
                "legalRequirements": "Cost",
                "frequency": "Cost"
            },
            "profile_matrix": {
                "Classe A (Maior Prioridade)": {
                    "projectMaturity": "VeryHigh",
                    "impact": "VeryHigh",
                    "costReduction": "VeryHigh",
                    "extEfficiency": "VeryHigh",
                    "intEfficiency": "VeryHigh",
                    "legalRequirements": "VeryHigh",
                    "frequency": "VeryHigh"
                },
                "Classe B (Media Prioridade)": {
                    "projectMaturity": "Medium",
                    "impact": "Medium",
                    "costReduction": "Medium",
                    "extEfficiency": "Medium",
                    "intEfficiency": "Medium",
                    "legalRequirements": "Medium",
                    "frequency": "Medium"
                },
                "Classe C (Baixa Prioridade)": {
                    "projectMaturity": "VeryLow",
                    "impact": "VeryLow",
                    "costReduction": "VeryLow",
                    "extEfficiency": "VeryLow",
                    "intEfficiency": "VeryLow",
                    "legalRequirements": "VeryLow",
                    "frequency": "VeryLow"
                }
            },
            "decision_matrix": decision_matrix,
            "alternatives": alternatives
        }
        
        ftopsis_results = run_ftopsis(data_ftopsis)
        classification = ftopsis_results["results"]["classification"]

        final_response = []

        for r in records:
            title = r.get("projectTitle")
            
            p_class = classification.get(title, "Finalizado" if r.get("status") == "Finalizado" else "S/Classificação")
            
            # proximidade com a Classe A para ordenação
            proximities = ftopsis_results["results"]["proximities"].get(title, {})
            proximity_to_a = proximities.get("Classe A (Maior Prioridade)", 0)
            
            manual_priority = r.get("manual_priority", "")
            is_manual_priority = False

            if manual_priority and manual_priority != "Automático":
                p_class = manual_priority
                proximity_to_a = 2.0  # Force it to go the top
                is_manual_priority = True

            final_response.append({
                "projectTitle": title,
                "responsibleName": r.get("clientName"),
                "email": r.get("email"),
                "responsibleBody": r.get("organization"),
                "status": r.get("status", "Não iniciado"),
                "row_index": r.get("row_index"),
                "priority_class": p_class,
                "proximity_to_a": proximity_to_a,
                "is_manual_priority": is_manual_priority,
                "full_data": r
            })
        
        return final_response

    except Exception as e:
        print(f"Erro ao calcular prioridades: {e}")
        return {"error": "Erro no servidor ao calcular as prioridades.", "details": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)
