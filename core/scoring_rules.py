def calculate_rule_based_score(answer, criteria):
    answer = answer.strip()
    results = []
    total_score = 0

    for criterion in criteria:
        keywords = criterion.get("keywords", [])
        max_marks = criterion["marks"]

        matched_keywords = [word for word in keywords if word in answer]
        match_count = len(matched_keywords)

        if match_count >= 4:
            awarded = max_marks
        elif match_count == 3:
            awarded = max_marks - 1
        elif match_count == 2:
            awarded = max_marks - 2
        elif match_count == 1:
            awarded = 2
        else:
            awarded = 0

        total_score += awarded

        results.append({
            "criterion": criterion["name"],
            "max_marks": max_marks,
            "awarded": awarded,
            "expected": criterion["expected"],
            "matched_keywords": matched_keywords
        })

    return total_score, results