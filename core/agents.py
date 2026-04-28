import json
from core.ollama_client import ask_ollama
from core.scoring_rules import calculate_rule_based_score
from core.sinhala_polish import polish_sinhala

class RetrievalAgent:
    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, question, answer):
        query = question + "\n" + answer
        return self.retriever.retrieve(query)


class OntologyAgent:
    def __init__(self, ontology_checker):
        self.ontology_checker = ontology_checker

    def run(self, answer):
        return self.ontology_checker.find_related_concepts(answer)


class ScoringAgent:
    def run(self, question, answer, criteria, evidence, ontology_matches):
        total_score, breakdown = calculate_rule_based_score(answer, criteria)

        ontology_summary = self.format_ontology_matches(ontology_matches)

        prompt = f"""
ඔබ ශ්‍රී ලංකා ඉතිහාසය පිළිබඳ සිංහල පිළිතුරු ඇගයීම කරන ගුරුවරයෙකි.

නීති:
- ලබාදී ඇති ලකුණු වෙනස් නොකරන්න.
- criteria 4ම අනිවාර්යයෙන් සම්පූර්ණ කරන්න.
- සිංහලෙන් පමණක් ලියන්න.
- කෙටි සහ පැහැදිලි හේතු දෙන්න.
- JSON පමණක් ලබා දෙන්න.
- JSON වලින් පිටත කිසිම වචනයක් ලියන්න එපා.
- හේතු ලිවීමේදී RAG සාක්ෂි සහ Ontology සංකල්ප භාවිතා කරන්න.
- අවම වශයෙන් ontology සංකල්ප 2ක් සමස්ත පැහැදිලි කිරීම තුළ සඳහන් කරන්න.

ප්‍රශ්නය:
{question}

ශිෂ්‍ය පිළිතුර:
{answer}

නිවැරදි ලකුණු:
{total_score}/20

ලකුණු විභජනය:
{json.dumps(breakdown, ensure_ascii=False)}

RAG සාක්ෂි:
{json.dumps(evidence[:2], ensure_ascii=False)}

Ontology සංකල්ප:
{json.dumps(ontology_matches[:10], ensure_ascii=False)}

Output JSON format:
{{
  "final_score": "{total_score}/20",
  "ontology_used": "{ontology_summary}",
  "criteria_scores": [
    {{
      "criterion": "නිර්ණායක නම",
      "marks": "ලකුණු/උපරිම ලකුණු",
      "reason": "RAG සාක්ෂි සහ ontology සංකල්ප භාවිතා කර කෙටි හේතුව"
    }}
  ],
  "overall_explanation": "RAG සාක්ෂි සහ ontology සංකල්ප සඳහන් කරමින් කෙටි සමස්ත පැහැදිලි කිරීම"
}}
END_JSON
"""

        llm_output = ask_ollama(prompt)

        if not llm_output:
            return self.generate_fallback(total_score, breakdown, ontology_matches)

        if not self.is_complete(llm_output):
            return self.generate_fallback(total_score, breakdown, ontology_matches)

        return polish_sinhala(llm_output)

    def format_ontology_matches(self, ontology_matches):
        if not ontology_matches:
            return "Ontology සංකල්ප හඳුනාගෙන නොමැත."

        concepts = []

        for item in ontology_matches[:8]:
            if isinstance(item, dict):
                concepts.append(item.get("concept", ""))
            else:
                concepts.append(str(item))

        concepts = [c for c in concepts if c]

        if not concepts:
            return "Ontology සංකල්ප හඳුනාගෙන නොමැත."

        return ", ".join(concepts)

    def is_complete(self, output):
        return (
            "final_score" in output
            and "criteria_scores" in output
            and "ontology_used" in output
            and output.count("criterion") >= 4
        )

    def generate_fallback(self, total_score, breakdown, ontology_matches):
        ontology_summary = self.format_ontology_matches(ontology_matches)

        text = f"අවසාන ලකුණු: {total_score}/20\n\n"
        text += f"භාවිතා කළ ontology සංකල්ප: {ontology_summary}\n\n"
        text += "ලකුණු විභජනය:\n\n"

        for i, item in enumerate(breakdown, 1):
            matched_keywords = item.get("matched_keywords", [])

            if item["awarded"] == item["max_marks"]:
                reason = "මෙම කරුණ සම්පූර්ණයෙන් නිවැරදිව සඳහන් කර ඇත."
            elif item["awarded"] > 0:
                reason = "මෙම කරුණ අර්ධ වශයෙන් සඳහන් කර ඇත."
            else:
                reason = "මෙම කරුණ පිළිතුර තුළ සඳහන් කර නොමැත."

            if matched_keywords:
                reason += f" හඳුනාගත් කරුණු: {', '.join(matched_keywords[:5])}."

            text += f"{i}. {item['criterion']} - {item['awarded']}/{item['max_marks']}\n"
            text += f"   හේතුව: {reason}\n\n"

        text += "සමස්ත පැහැදිලි කිරීම:\n"
        text += (
            "ශිෂ්‍ය පිළිතුර marking criteria, RAG සාක්ෂි සහ ontology සංකල්ප "
            "සලකා බලමින් පරීක්ෂා කර ලකුණු ලබා දී ඇත."
        )

        return polish_sinhala(text)


class ConsistencyAgent:
    def run(self, scoring_output):
        prompt = f"""
Check this marking output for consistency.

Marking Output:
{scoring_output}

Check:
1. Do criterion marks add up correctly?
2. Is the final score out of 20?
3. Is the explanation clear?
4. If there is an issue, correct it.

Return the corrected final version in Sinhala.
"""
        return ask_ollama(prompt)