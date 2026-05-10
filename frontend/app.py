import os
from html import escape
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components


API_BASE_URL = os.getenv("EVVIVA_API_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Evviva Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_custom_css() -> None:
    st.markdown(
        """
<style>
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
    }

    .main {
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 1rem;
        max-width: 1180px;
    }

    h1 {
        font-size: 32px !important;
        line-height: 1.05 !important;
        color: #020617;
    }

    h2 {
        font-size: 20px !important;
        color: #0f172a;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        font-size: 18px !important;
        color: #0f172a;
    }

    p, label, div, span {
        font-size: 14px;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    div[data-testid="collapsedControl"] {
        display: none !important;
    }

    .evviva-navbar {
        width: 100vw;
        margin-left: calc(50% - 50vw);
        margin-right: calc(50% - 50vw);
        margin-top: 0;
        margin-bottom: 14px;
        background: #dcfce7;
        border-bottom: 1px solid #86efac;
        padding: 0 24px;
        box-sizing: border-box;
    }

    .evviva-navbar-content {
        width: 100%;
        max-width: 980px;
        min-height: 48px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 34px;
        box-sizing: border-box;
    }

    .evviva-navbar-brand {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px !important;
        font-weight: 900 !important;
        color: #15803d !important;
        line-height: 1.1 !important;
        white-space: nowrap;
    }

    .evviva-navbar-links {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 26px;
        flex-wrap: nowrap;
    }

    .evviva-navbar-link {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.1 !important;
        white-space: nowrap;
        text-decoration: none;
    }

    .stTextArea {
        margin-top: 0 !important;
    }

    .stTextArea textarea {
        font-size: 15px !important;
        min-height: 76px !important;
        border-radius: 12px !important;
        background-color: #ecfdf5 !important;
    }

    .stTextArea label {
        font-size: 16px !important;
        font-weight: 900;
        color: #0f172a;
    }

    div[data-testid="stTextArea"] label p {
        font-size: 16px !important;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 4px !important;
    }

    .stButton > button {
        min-height: 40px;
        font-size: 14px;
        border-radius: 10px;
        padding: 7px 14px;
    }

    .answer-card {
        background-color: #ecfdf5;
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 16px;
        color: #064e3b;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
        white-space: pre-wrap;
    }

    .supporting-excerpt {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 16px;
        color: #0f172a;
        font-size: 15px;
        line-height: 1.55;
        white-space: pre-wrap;
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
        margin-bottom: 6px;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    iframe[title="streamlit.components.v1.html"] {
        display: block;
        margin-bottom: 0 !important;
    }

    @media (max-width: 900px) {
        .evviva-navbar-content {
            gap: 20px;
        }

        .evviva-navbar-links {
            gap: 16px;
        }

        .evviva-navbar-brand {
            font-size: 15px !important;
        }

        .evviva-navbar-link {
            font-size: 12px !important;
        }
    }
</style>
        """,
        unsafe_allow_html=True,
    )


def render_navbar() -> None:
    st.markdown(
        """
<div class="evviva-navbar">
    <div class="evviva-navbar-content">
        <div class="evviva-navbar-brand">Evviva AI</div>
        <div class="evviva-navbar-links">
            <span class="evviva-navbar-link">Assistant</span>
            <span class="evviva-navbar-link">Customer Intelligence</span>
            <span class="evviva-navbar-link">Email Insights</span>
            <span class="evviva-navbar-link">RAG Search</span>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    components.html(
        """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background: transparent;
        overflow: hidden;
    }

    .evviva-hero {
        background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 50%, #faf5ff 100%);
        border: 1px solid #dbeafe;
        padding: 18px 28px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        min-height: 132px;
        box-sizing: border-box;
    }

    .evviva-hero-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }

    .evviva-hero-copy {
        max-width: 560px;
    }

    .evviva-hero-kicker {
        color: #16a34a;
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .evviva-hero-title {
        font-size: 32px;
        line-height: 1.05;
        margin: 0 0 8px 0;
        color: #020617;
        font-weight: 900;
    }

    .evviva-hero-text {
        font-size: 14px;
        color: #475569;
        line-height: 1.4;
        margin: 0;
    }

    .evviva-hero svg {
        width: 280px;
        height: 126px;
        flex-shrink: 0;
    }
</style>
</head>
<body>
<div class="evviva-hero">
    <div class="evviva-hero-content">
        <div class="evviva-hero-copy">
            <div class="evviva-hero-kicker">Customer Intelligence powered by AI</div>
            <div class="evviva-hero-title">Evviva Assistant</div>
            <p class="evviva-hero-text">
                Turn customer conversations from WhatsApp and email into clear,
                traceable answers in seconds.
            </p>
        </div>

        <svg viewBox="0 0 620 330" xmlns="http://www.w3.org/2000/svg">
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
            <text x="61" y="265" font-size="30" font-family="Arial" fill="#334155">WhatsApp</text>

            <rect x="235" y="70" width="150" height="145" rx="30" fill="#ffffff" filter="url(#shadow)" />
            <circle cx="310" cy="125" r="34" fill="#3b82f6"/>
            <text x="291" y="139" font-size="42" font-family="Arial" fill="#ffffff">✉</text>
            <rect x="271" y="175" width="78" height="13" rx="7" fill="#cbd5e1"/>
            <rect x="259" y="198" width="100" height="13" rx="7" fill="#e2e8f0"/>
            <text x="282" y="265" font-size="30" font-family="Arial" fill="#334155">Email</text>

            <rect x="432" y="70" width="150" height="145" rx="30" fill="#ffffff" filter="url(#shadow)" />
            <circle cx="507" cy="125" r="34" fill="#8b5cf6"/>
            <text x="484" y="137" font-size="34" font-family="Arial" fill="#ffffff">AI</text>
            <rect x="468" y="175" width="78" height="13" rx="7" fill="#cbd5e1"/>
            <rect x="456" y="198" width="100" height="13" rx="7" fill="#e2e8f0"/>
            <text x="507" y="265" font-size="30" font-family="Arial" fill="#334155" text-anchor="middle">Evviva AI</text>

            <path d="M193 142 C210 142 218 142 230 142" stroke="#64748b" stroke-width="5" stroke-dasharray="8 8"/>
            <path d="M390 142 C407 142 415 142 427 142" stroke="#64748b" stroke-width="5" stroke-dasharray="8 8"/>
        </svg>
    </div>
</div>
</body>
</html>
        """,
        height=150,
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


def clean_supporting_excerpt(text: str, metadata: dict[str, Any]) -> str:
    if not text:
        return ""

    cleaned_text = text.strip()

    if "### Message" in cleaned_text:
        cleaned_text = cleaned_text.split("### Message", 1)[1].strip()
    elif "Email body:" in cleaned_text:
        cleaned_text = cleaned_text.split("Email body:", 1)[1].strip()

    cleaned_text = cleaned_text.replace("**", "")
    cleaned_text = cleaned_text.replace("##", "")
    cleaned_text = cleaned_text.replace("###", "")
    cleaned_text = cleaned_text.strip()

    if cleaned_text:
        return cleaned_text

    subject = metadata.get("subject")
    if subject:
        return f"Subject: {subject}"

    return "No readable excerpt available."


def render_sources(sources: list[dict[str, Any]]) -> None:
    if not sources:
        st.info("No supporting records were returned.")
        return

    for index, source in enumerate(sources, start=1):
        metadata = source.get("metadata", {})
        document_id = metadata.get("document_id", "unknown_document")
        contact_name = (
            metadata.get("contact_name")
            or metadata.get("sender_name")
            or metadata.get("sender_email")
            or "unknown_customer"
        )
        channel = metadata.get("channel", metadata.get("source", "unknown_channel"))
        timestamp = metadata.get("timestamp") or metadata.get("date") or "unknown_date"
        score = source.get("score", 0)

        title = f"Record {index}: {contact_name} | {channel} | confidence {score:.2f}"

        with st.expander(title):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Customer:** {contact_name}")
                st.write(f"**Channel:** {channel}")

                direction = metadata.get("direction")
                if direction:
                    st.write(f"**Direction:** {direction}")

            with col2:
                st.write(f"**Record ID:** {document_id}")
                st.write(f"**Date:** {timestamp}")

                subject = metadata.get("subject")
                if subject:
                    st.write(f"**Subject:** {subject}")

            excerpt = clean_supporting_excerpt(
                text=source.get("text") or source.get("text_preview") or "",
                metadata=metadata,
            )

            st.write("**Supporting excerpt:**")
            st.markdown(
                f"""
                <div class="supporting-excerpt">
                    {escape(excerpt)}
                </div>
                """,
                unsafe_allow_html=True,
            )


apply_custom_css()
render_navbar()
render_hero()


limit = 5
selected_customer = "All customers"
selected_source = "All channels"


if "query" not in st.session_state:
    st.session_state["query"] = ""

query = st.text_area(
    "Type your question here:",
    value=st.session_state["query"],
    placeholder="Example: What did Marco want to confirm?",
    height=90,
)

ask_button = st.button(
    "Ask Evviva Assistant",
    type="primary",
    key="ask_evviva_assistant_button",
)

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

                answer = escape(result.get("answer", ""))
                st.markdown(
                    f"""
                    <div class="answer-card">
                        {answer}
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
