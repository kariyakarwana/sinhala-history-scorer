import json


class OntologyChecker:
    def __init__(self, ontology_path):
        with open(ontology_path, "r", encoding="utf-8") as file:
            self.ontology = json.load(file)

        self.search_terms = []
        self._extract_terms(self.ontology)

    def _extract_terms(self, obj, parent_key=""):
        """
        Recursively extracts Sinhala ontology terms from nested ontology.json.
        Works with dictionaries, lists, and strings.
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(key, str):
                    self.search_terms.append({
                        "term": key,
                        "category": parent_key or "Ontology"
                    })
                self._extract_terms(value, key)

        elif isinstance(obj, list):
            for item in obj:
                self._extract_terms(item, parent_key)

        elif isinstance(obj, str):
            # Add Sinhala/English string values from ontology
            self.search_terms.append({
                "term": obj,
                "category": parent_key or "Ontology"
            })

    def find_related_concepts(self, answer):
        matched = []
        answer_text = answer.lower()

        for item in self.search_terms:
            term = item["term"]

            if not isinstance(term, str):
                continue

            term_clean = term.strip()

            # Ignore very short English technical keys
            if len(term_clean) < 2:
                continue

            if term_clean.lower() in answer_text:
                matched.append({
                    "concept": term_clean,
                    "category": item["category"]
                })

        # Remove duplicates
        unique = []
        seen = set()

        for item in matched:
            key = item["concept"]
            if key not in seen:
                unique.append(item)
                seen.add(key)

        return unique[:15]