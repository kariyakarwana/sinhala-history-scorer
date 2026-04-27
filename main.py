import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import streamlit as st
import json

from core.rag import RAGRetriever
from core.ontology import OntologyChecker
from core.agents import RetrievalAgent, OntologyAgent, ScoringAgent, ConsistencyAgent

st.set_page_config(
    page_title="Sinhala History Answer Scorer",
    layout="wide"
)

@st.cache_resource
def load_system():
    retriever = RAGRetriever("data/knowledge_base.txt")
    ontology_checker = OntologyChecker("data/ontology.json")

    return {
        "retrieval_agent": RetrievalAgent(retriever),
        "ontology_agent": OntologyAgent(ontology_checker),
        "scoring_agent": ScoringAgent()
    }

@st.cache_data
def load_questions():
    with open("data/questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

system = load_system()
questions = load_questions()

st.title("Offline Intelligent Sinhala Open-Ended Answer Scorer")
st.write("History of Sri Lanka — Anuradhapura Period")

selected_question = st.selectbox(
    "Select Question",
    questions,
    format_func=lambda q: q["question"]
)

st.subheader("Question")
st.write(selected_question["question"])

student_answer = st.text_area(
    "Enter Sinhala Answer",
    height=200,
    placeholder="ඔබගේ පිළිතුර මෙහි ඇතුළත් කරන්න..."
)

if st.button("Score Answer"):
    if not student_answer.strip():
        st.warning("Please enter an answer first.")
    else:
        with st.spinner("Scoring answer offline..."):
            evidence = system["retrieval_agent"].run(
                selected_question["question"],
                student_answer
            )

            ontology_matches = system["ontology_agent"].run(student_answer)

            final_output = system["scoring_agent"].run(
                selected_question["question"],
                student_answer,
                selected_question["criteria"],
                evidence,
                ontology_matches
            )

            st.subheader("Final Score and Explanation")

            try:
                import json

                parsed = json.loads(final_output)

                st.success(f"අවසාන ලකුණු: {parsed['final_score']}")

                st.markdown("### ලකුණු විභජනය")
                for item in parsed["criteria_scores"]:
                    st.markdown(f"**{item['criterion']} - {item['marks']}**")
                    st.write(f"හේතුව: {item['reason']}")

                st.markdown("### සමස්ත පැහැදිලි කිරීම")
                st.write(parsed["overall_explanation"])

            except Exception:
                st.markdown(final_output)

        st.subheader("Retrieved Evidence Used by RAG")
        for item in evidence:
            st.info(item)

        st.subheader("Ontology Concepts Found")
        st.write(ontology_matches)