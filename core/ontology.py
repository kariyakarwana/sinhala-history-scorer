import json

class OntologyChecker:
    def __init__(self, ontology_path):
        with open(ontology_path, "r", encoding="utf-8") as file:
            self.ontology = json.load(file)

    def find_related_concepts(self, answer):
        matched = []

        for concept, data in self.ontology.items():
            if concept.lower() in answer.lower():
                matched.append(concept)

            if isinstance(data, dict):
                examples = data.get("examples", [])
                for example in examples:
                    if example in answer:
                        matched.append(example)

        return list(set(matched))