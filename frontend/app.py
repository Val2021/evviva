import os
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components


API_BASE_URL = os.getenv("EVVIVA_API_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Evviva Assistant",
    page_icon="💬",
    layout="wide",
)


def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
            .main {
                background-color: #ffffff;
            }

            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 1.5rem;
                max-width: 1350px;
            }

            h1 {
                font-size: 40px !important;
                line-height: 1.1 !important;
                color: #020617;
            }

            h2 {
                font-size: 26px !important;
                color: #0f172a;
            }

            h3 {
                font-size: 22px !important;
                color: #0f172a;
            }

            p, label, div, span {
                font-size: 15px;
            }

            section[data-testid="stSidebar"] {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }

            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3 {
                color: #0f172a;
            }

            section[data-testid="stSidebar"] h2 {
                font-size: 24px !important;
                line-height: 1.15 !important;
            }

            .stButton > button {
                min-height: 44px;
                font-size: 15px;
                border-radius: 11px;
                padding: 8px 16px;
            }

            .stTextArea textarea {
                font-size: 16px !important;
                min-height: 95px !important;
                border-radius: 14px !important;
            }

            .stSelectbox div[data-baseweb="select"] {
                font-size: 15px;
            }

            .value-card {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 22px;
                min-height: 125px;
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
            }

            .value-card-title {
                font-size: 20px;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 8px;
            }

            .value-card-text {
                font-size: 17px;
                color: #334155;
                line-height: 1.55;
            }

            .answer-card {
                background-color: #ecfdf5;
                border: 1px solid #bbf7d0;
                border-radius: 18px;
                padding: 20px;
                color: #064e3b;
                font-size: 16px;
                line-height: 1.6;
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
            }

            .section-description {
                font-size: 16px;
                color: #475569;
                line-height: 1.5;
                margin-bottom: 18px;
            }

            .example-title {
                font-size: 16px;
                font-weight: 600;
                color: #334155;
                margin-bottom: 10px;
            }

            div[data-testid="stExpander"] {
                border-radius: 14px;
                border: 1px solid #e2e8f0;
                overflow: hidden;
                margin-bottom: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    components.html(
        """
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 50%, #faf5ff 100%);
                    border: 1px solid #e2e8f0;
                    border-radius: 22px;
                    padding: 24px 30px;
                    margin-bottom: 22px;
                    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 28px;">
                <div style="max-width: 560px;">
                    <div style="font-family: Arial, sans-serif;
                                color: #16a34a;
                                font-size: 13px;
                                font-weight: 700;
                                margin-bottom: 8px;">
                        Customer Intelligence powered by AI
                    </div>

                    <h1 style="font-family: Arial, sans-serif;
                               font-size: 34px;
                               line-height: 1.05;
                               margin: 0 0 10px 0;
                               color: #020617;">
                        Evviva Assistant
                    </h1>

                    <p style="font-family: Arial, sans-serif;
                              font-size: 14px;
                              color: #475569;
                              line-height: 1.45;
                              margin: 0;">
                        Turn customer conversations from WhatsApp and email into clear,
                        traceable answers in seconds.
                    </p>
                </div>

                <svg width="330" height="150" viewBox="0 0 620 330" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                            <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.18"/>
                        </filter>
                    </defs>

                    <rect x="38" y="70" width="150" height="145" rx="30" fill="#ffffff" filter="url(#shadow)" />
                    <circle cx="113" cy="125" r="34" fill="#22c55e"/>
                    <text x="92" y="138" font-size="42" font-family="Arial" fill="#ffffff">💬</text>
                    <rect x="74" y="175" width="78" height="13" rx="7" fill="#cbd5e1"/>
                    <rect x="62" y="198" width="100" height="13" rx="7" fill="#e2e8f0"/>
                    <text x="61" y="265" font-size="22" font-family="Arial" fill="#334155">WhatsApp</text>

                    <rect x="235" y="70" width="150" height="145" rx="30" fill="#ffffff" filter="url(#shadow)" />
                    <circle cx="310" cy="125" r="34" fill="#3b82f6"/>
                    <text x="291" y="139" font-size="42" font-family="Arial" fill="#ffffff">✉</text>
                    <rect x="271" y="175" width="78" height="13" rx="7" fill="#cbd5e1"/>
                    <rect x="259" y="198" width="100" height="13" rx="7" fill="#e2e8f0"/>
                    <text x="282" y="265" font-size="22" font-family="Arial" fill="#334155">Email</text>

                    <rect x="432" y="70" width="150" height="145" rx="30" fill="#ffffff" filter="url(#shadow)" />
                    <circle cx="507" cy="125" r="34" fill="#8b5cf6"/>
                    <text x="484" y="137" font-size="34" font-family="Arial" fill="#ffffff">AI</text>
                    <rect x="468" y="175" width="78" height="13" rx="7" fill="#cbd5e1"/>
                    <rect x="456" y="198" width="100" height="13" rx="7" fill="#e2e8f0"/>
                    <text x="507" y="265" font-size="22" font-family="Arial" fill="#334155" text-anchor="middle">Evviva AI</text>

                    <path d="M193 142 C210 142 218 142 230 142" stroke="#64748b" stroke-width="5" stroke-dasharray="8 8"/>
                    <path d="M390 142 C407 142 415 142 427 142" stroke="#64748b" stroke-width="5" stroke-dasharray="8 8"/>
                </svg>
            </div>
        </div>
        """,
        height=190,
    )


def call_rag_api(
    query: str,
    limit: int,
    filter_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/rag",
        json={
            "query": query,
            "limit": limit,
            "filter": filter_payload,
        },
        timeout=120,
    )

    response.raise_for_status()
    return response.json()


def build_filter(
    selected_customer: str,
    selected_source: str,
) -> dict[str, Any] | None:
    filters: dict[str, Any] = {}

    if selected_customer != "All customers":
        filters["contact_name"] = selected_customer

    if selected_source != "All channels":
        filters["source"] = selected_source

    return filters or None


def render_sources(sources: list[dict[str, Any]]) -> None:
    if not sources:
        st.info("No supporting records were returned.")
        return

    for index, source in enumerate(sources, start=1):
        metadata = source.get("metadata", {})
        document_id = metadata.get("document_id", "unknown_document")
        contact_name = metadata.get("contact_name", "unknown_customer")
        channel = metadata.get("channel", metadata.get("source", "unknown_channel"))
        timestamp = metadata.get("timestamp", "unknown_date")
        score = source.get("score", 0)

        title = f"Record {index}: {contact_name} | {channel} | confidence {score:.2f}"

        with st.expander(title):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Customer:** {contact_name}")
                st.write(f"**Channel:** {channel}")
                st.write(f"**Direction:** {metadata.get('direction')}")

            with col2:
                st.write(f"**Record ID:** {document_id}")
                st.write(f"**Date:** {timestamp}")

                subject = metadata.get("subject")
                if subject:
                    st.write(f"**Subject:** {subject}")

            st.write("**Supporting excerpt:**")
            st.code(source.get("text_preview", ""), language="markdown")


apply_custom_css()
render_hero()


with st.sidebar:
    st.header("Assistant controls")

    limit = st.slider(
        "Records to analyze",
        min_value=1,
        max_value=10,
        value=5,
    )

    selected_customer = st.selectbox(
        "Customer scope",
        [
            "All customers",
            "Mariana Costa",
            "João Silva",
            "Ana Ribeiro",
            "Carlos Mendes",
        ],
    )

    selected_source = st.selectbox(
        "Communication channel",
        [
            "All channels",
            "whatsapp",
            "email",
        ],
    )


st.markdown("## Ask a business question")

st.markdown(
    """
    <div class="section-description">
        Ask anything about customer conversations, pending documents, contract signatures,
        duplicated charges, or previous support interactions.
    </div>
    """,
    unsafe_allow_html=True,
)

card_cols = st.columns(3)

with card_cols[0]:
    st.markdown(
        """
        <div class="value-card">
            <div class="value-card-title">Understand customers faster</div>
            <div class="value-card-text">
                Find the right interaction without manually checking messages and emails.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_cols[1]:
    st.markdown(
        """
        <div class="value-card">
            <div class="value-card-title">Answer with traceability</div>
            <div class="value-card-text">
                Every answer includes the records used as supporting evidence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_cols[2]:
    st.markdown(
        """
        <div class="value-card">
            <div class="value-card-title">Reduce operational effort</div>
            <div class="value-card-text">
                Support teams can quickly understand what happened in each case.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="example-title">Try one of these examples or write your own question:</div>',
    unsafe_allow_html=True,
)

example_questions = [
    "What happened with Carlos's contract signature?",
    "Which customer asked about a duplicate charge?",
    "Who needs to resend a proof of address?",
]

cols = st.columns(len(example_questions))

for col, example in zip(cols, example_questions):
    with col:
        if st.button(example, use_container_width=True):
            st.session_state["query"] = example

if "query" not in st.session_state:
    st.session_state["query"] = ""

query = st.text_area(
    "Your question",
    value=st.session_state["query"],
    placeholder="Example: Which customer has a pending document issue?",
    height=95,
)

ask_button = st.button("Ask Evviva Assistant", type="primary")

if ask_button:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        filter_payload = build_filter(
            selected_customer=selected_customer,
            selected_source=selected_source,
        )

        with st.spinner("Analyzing customer conversations..."):
            try:
                result = call_rag_api(
                    query=query,
                    limit=limit,
                    filter_payload=filter_payload,
                )

                st.markdown("## Answer")

                st.markdown(
                    f"""
                    <div class="answer-card">
                        {result.get("answer", "")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("## Supporting records")
                render_sources(result.get("sources", []))

            except requests.exceptions.ConnectionError:
                st.error(
                    "The assistant could not connect to the application service. "
                    "Please check if the backend is running."
                )
            except requests.exceptions.HTTPError as error:
                st.error(f"The application service returned an error: {error}")
                st.code(error.response.text)
            except Exception as error:
                st.error(f"Unexpected error: {error}")
