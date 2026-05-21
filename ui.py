from contextlib import contextmanager

import streamlit as st


@contextmanager
def section_card(title: str, subtitle: str = None):
    header = f"<div class='section-card'><div class='section-card-header'><h2>{title}</h2>"
    if subtitle:
        header += f"<p>{subtitle}</p>"
    header += '</div>'
    st.markdown(header, unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown('</div>', unsafe_allow_html=True)
