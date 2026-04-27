import copy
from ftopsis import run_ftopsis

# Basic FTOPSIS Configuration
base_data = {
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
    }
}

# The 5 Profiles developed in the previous step
test_alternatives = {
    "P1 (Unicornio)": ["VeryHigh", "VeryHigh", "VeryHigh", "VeryHigh", "VeryHigh", "VeryHigh", "VeryHigh"],
    "P2 (Baixo Valor)": ["VeryLow", "VeryLow", "VeryLow", "VeryLow", "VeryLow", "VeryLow", "VeryLow"],
    "P3 (Acao Social)": ["Low", "VeryHigh", "VeryLow", "High", "Low", "Low", "Medium"],
    "P4 (Obrigacao Legal)": ["Medium", "Low", "VeryLow", "Medium", "Low", "VeryHigh", "Low"],
    "P5 (Ferramenta Interna)": ["High", "VeryLow", "High", "Low", "VeryHigh", "Medium", "VeryHigh"]
}

criteria_keys = [
    "projectMaturity", "impact", "costReduction", 
    "extEfficiency", "intEfficiency", "legalRequirements", "frequency"
]

decision_matrix = {k: [] for k in criteria_keys}
alternatives = list(test_alternatives.keys())

for idx, alt in enumerate(alternatives):
    values = test_alternatives[alt]
    for i, key in enumerate(criteria_keys):
        decision_matrix[key].append(values[i])

# Define Weight Scenarios
scenarios = {
    "Baseline (Current)": {
        "projectMaturity": ["Low"],
        "impact": ["VeryHigh"],
        "costReduction": ["VeryHigh"],
        "extEfficiency": ["VeryHigh"],
        "intEfficiency": ["VeryHigh"],
        "legalRequirements": ["Low"],
        "frequency": ["Medium"]
    },
    "Equally Weighted": {
        "projectMaturity": ["Medium"],
        "impact": ["Medium"],
        "costReduction": ["Medium"],
        "extEfficiency": ["Medium"],
        "intEfficiency": ["Medium"],
        "legalRequirements": ["Medium"],
        "frequency": ["Medium"]
    },
    "Compliance Heavy": {
        "projectMaturity": ["VeryLow"],
        "impact": ["Medium"],
        "costReduction": ["Medium"],
        "extEfficiency": ["VeryLow"],
        "intEfficiency": ["VeryLow"],
        "legalRequirements": ["VeryHigh"],
        "frequency": ["VeryLow"]
    },
    "Social Impact Focus": {
        "projectMaturity": ["Medium"],
        "impact": ["VeryHigh"],
        "costReduction": ["VeryLow"],
        "extEfficiency": ["High"],
        "intEfficiency": ["Low"],
        "legalRequirements": ["Low"],
        "frequency": ["Medium"]
    }
}


def run_experiments():
    print("=== TESTE DE SENSIBILIDADE FTOPSIS-CLASS ===")
    print("Avaliando como diferentes pesos de criterios impactam a priorizacao final.")
    print("Alternativas de Teste:", alternatives)
    print("--------------------------------------------------\n")

    for scenario_name, weights in scenarios.items():
        print(f"--- Cenario: {scenario_name} ---")
        data = copy.deepcopy(base_data)
        data["weights"] = weights
        data["decision_matrix"] = decision_matrix
        data["alternatives"] = alternatives
        
        results = run_ftopsis(data)
        classification = results["results"]["classification"]
        proximities = results["results"]["proximities"]
        
        for alt in alternatives:
            c = classification[alt]
            p_A = proximities[alt].get('Classe A (Maior Prioridade)', 0)
            print(f"{alt:<25} -> {c:<30} (Prox. A: {p_A:.3f})")
        print()

if __name__ == "__main__":
    run_experiments()
