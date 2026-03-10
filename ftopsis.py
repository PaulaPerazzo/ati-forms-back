import numpy as np
from math import sqrt

def normalize_decision_matrix_fixed(data):
    lv = data["linguistic_variables_alternatives"]
    decision_matrix = data["decision_matrix"]
    criteria_type = data["criteria_type"]

    normalized_matrix = {}
    factors = {}

    for criterion, values in decision_matrix.items():
        fuzzy_values = [lv[val] for val in values]
        fuzzy_array = np.array(fuzzy_values)

        d_star = max(np.max(fuzzy_array[:, 3]), max(f[3] for f in lv.values()))

        if criteria_type[criterion] == "Benefit":
            normalized = np.array([[v / d_star for v in row] for row in fuzzy_array])
            factors[criterion] = {"type": "Benefit", "value": d_star}
        else:
            normalized = np.array([[(d_star - v) / d_star for v in reversed(row)] for row in fuzzy_array])
            factors[criterion] = {"type": "Cost", "value": d_star}

        normalized_matrix[criterion] = normalized.tolist()

    return normalized_matrix, factors

def normalize_profiles(profile_matrix, lv, factors):
    norm_profiles = {}
    
    for prof, criteria in profile_matrix.items():
        norm_profiles[prof] = {}
        
        for crit, label in criteria.items():
            val = np.array(lv[label])
            f = factors[crit]
            d_star = f["value"]

            if f["type"] == "Benefit":
                norm_profiles[prof][crit] = (val / d_star).tolist()
            else:
                norm_profiles[prof][crit] = ((d_star - val[::-1]) / d_star).tolist()
    
    return norm_profiles

def construct_weighted_normalized_matrix(normalized_matrix, weights, linguistic_weights):
    weighted_matrix = {}

    for criterion, norm_values in normalized_matrix.items():
        weight_label = weights[criterion][0]
        w = linguistic_weights[weight_label]
        weighted_rows = []

        for row in norm_values:
            weighted_rows.append([r * w_i for r, w_i in zip(row, w)])

        weighted_matrix[criterion] = weighted_rows

    return weighted_matrix

def get_positive_ideal_solutions(profile_matrix, linguistic_variables):
    return {
        profile: {
            criterion: linguistic_variables[label]
            for criterion, label in criteria.items()
        }

        for profile, criteria in profile_matrix.items()
    }

def fuzzy_distance(a, b):
    return sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)) / 4)

def get_negative_ideal_solutions(profile_matrix, linguistic_variables):
    profiles = list(profile_matrix.keys())

    fuzzy_profiles = {
        profile: {
            criterion: linguistic_variables[label]
            for criterion, label in profile_matrix[profile].items()
        }
        for profile in profiles
    }

    negative_ideal_solutions = {}

    for p in profiles:
        farthest_profile = max(
            (p2 for p2 in profiles if p2 != p),
            key=lambda p2: sum(
                fuzzy_distance(fuzzy_profiles[p][c], fuzzy_profiles[p2][c])
                for c in profile_matrix[p]
            )
        )

        negative_ideal_solutions[p] = fuzzy_profiles[farthest_profile]

    return negative_ideal_solutions

def apply_weights_to_profiles(profile_solutions, weights, linguistic_weights):
    weighted_profiles = {}

    for profile, criteria in profile_solutions.items():
        weighted_profiles[profile] = {}

        for criterion, values in criteria.items():
            weight = linguistic_weights[weights[criterion][0]]
            weighted_profiles[profile][criterion] = [v * w for v, w in zip(values, weight)]

    return weighted_profiles

def calculate_distances_to_ideal_solutions(weighted_matrix, positive_ideal, negative_ideal, alternatives):
    distances = {}

    for profile in positive_ideal:
        distances[profile] = {"positive": {}, "negative": {}}

        for i, alt in enumerate(alternatives):
            d_pos = sum(fuzzy_distance(weighted_matrix[crit][i], positive_ideal[profile][crit]) for crit in weighted_matrix)
            d_neg = sum(fuzzy_distance(weighted_matrix[crit][i], negative_ideal[profile][crit]) for crit in weighted_matrix)
    
            distances[profile]["positive"][alt] = d_pos
            distances[profile]["negative"][alt] = d_neg

    return distances

def calculate_closeness_coefficients(distance_results, alternatives):
    cc = {}

    for profile in distance_results:
        cc[profile] = {}

        for alt in alternatives:
            d_pos = distance_results[profile]["positive"][alt]
            d_neg = distance_results[profile]["negative"][alt]
            cc[profile][alt] = d_neg / (d_pos + d_neg) if d_pos + d_neg != 0 else 0

    return cc

def classify_alternatives(closeness_coeffs):
    classification = {}
    profiles = list(closeness_coeffs.keys())

    for alt in closeness_coeffs[profiles[0]]:
        best_profile = max(profiles, key=lambda p: closeness_coeffs[p][alt])
        classification[alt] = best_profile

    return classification

def run_ftopsis(data):
    normalized_matrix, factors = normalize_decision_matrix_fixed(data)
    weighted_matrix = construct_weighted_normalized_matrix(
        normalized_matrix, data["weights"], data["linguistic_variables_weights"]
    )

    # normalizar os perfis de classe 
    norm_profiles = normalize_profiles(data["profile_matrix"], data["linguistic_variables_alternatives"], factors)

    # obter soluções ideais baseadas nos perfis normalizados
    positive_ideal = {p: {c: v for c, v in crits.items()} for p, crits in norm_profiles.items()}
    
    # o negativo ideal é o perfil mais distante
    negative_ideal = {}
    profiles_list = list(norm_profiles.keys())

    for p in profiles_list:
        farthest = max(
            (p2 for p2 in profiles_list if p2 != p), 
            key=lambda p2: sum(fuzzy_distance(norm_profiles[p][c], 
            norm_profiles[p2][c]) for c in norm_profiles[p])
        )

        negative_ideal[p] = norm_profiles[farthest]

    positive_ideal_weighted = apply_weights_to_profiles(positive_ideal, data["weights"], data["linguistic_variables_weights"])
    negative_ideal_weighted = apply_weights_to_profiles(negative_ideal, data["weights"], data["linguistic_variables_weights"])

    distance_results = calculate_distances_to_ideal_solutions(
        weighted_matrix, positive_ideal_weighted, negative_ideal_weighted, data["alternatives"]
    )

    closeness_coeffs = calculate_closeness_coefficients(distance_results, data["alternatives"])

    classification = classify_alternatives(closeness_coeffs)

    return {
        "method": "FTOPSIS-Class",
        "results": {
            "classification": classification,
            "proximities": {
                alt: {
                    prof: round(closeness_coeffs[prof][alt], 4)
                    for prof in data["profile_matrix"]
                }
                for alt in data["alternatives"]
            },
            "best_class_for_each_alternative": classification
        }
    }
