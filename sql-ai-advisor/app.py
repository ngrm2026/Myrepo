"""Streamlit UI:  streamlit run app.py"""
from datetime import datetime

import streamlit as st

import advisor
import config
import db

st.set_page_config(page_title="SQL AI Query Advisor", layout="wide")
st.title("SQL AI Query Advisor")
st.caption("Read-only: collects Query Store / DMV data, asks an LLM to explain it. Nothing is changed on the server.")

with st.sidebar:
    st.subheader("Connection")
    server = st.text_input("Server", config.SQL_SERVER)
    database = st.text_input("Database", config.SQL_DATABASE)
    hours = st.number_input("Look-back hours", 1, 24 * 30, config.LOOKBACK_HOURS)
    top_n = st.number_input("Top N queries", 1, 50, config.TOP_N)
    st.write(f"LLM: **{config.LLM_PROVIDER}** {config.LLM_MODEL}")
    st.write(f"Mask literals: **{config.MASK_LITERALS}**")
    load = st.button("Load top queries", type="primary")

config.SQL_SERVER = server


@st.cache_resource(show_spinner=False)
def get_conn(server_name: str, database_name: str):
    return db.connect(database_name)


tab_queries, tab_waits = st.tabs(["Top queries", "Wait stats"])

with tab_queries:
    if load:
        try:
            conn = get_conn(server, database)
            df, source = db.top_queries(conn, int(hours), int(top_n))
            st.session_state["top"] = df
            st.session_state["source"] = source
        except Exception as exc:  # show connection/permission errors plainly
            st.error(f"Could not load queries: {exc}")

    df = st.session_state.get("top")
    if df is None:
        st.info("Set the connection in the sidebar and click **Load top queries**.")
    elif df.empty:
        st.warning("No queries found for this window.")
    else:
        st.write(f"Source: **{st.session_state['source']}** — ranked by total CPU")
        view = df.drop(columns=["query_plan"]).copy()
        view["query_sql_text"] = view["query_sql_text"].str.slice(0, 120)
        st.dataframe(view, use_container_width=True, hide_index=False)

        idx = st.selectbox(
            "Pick a query to diagnose",
            df.index,
            format_func=lambda i: f"#{i}  avg CPU {float(df.loc[i, 'avg_cpu_ms'] or 0):,.1f} ms — "
                                  f"{(df.loc[i, 'query_sql_text'] or '')[:90]}",
        )
        if st.button("Diagnose with AI"):
            row = df.loc[idx]
            with st.spinner("Collecting table/index details and asking the LLM..."):
                try:
                    conn = get_conn(server, database)
                    evidence, answer = advisor.diagnose(conn, row)
                except Exception as exc:
                    st.error(f"Diagnosis failed: {exc}")
                    st.stop()
            st.markdown(answer)
            with st.expander("Evidence sent to the LLM"):
                st.markdown(evidence)

            config.REPORT_DIR.mkdir(exist_ok=True)
            name = f"diagnosis_{datetime.now():%Y%m%d_%H%M%S}.md"
            (config.REPORT_DIR / name).write_text(
                f"# Diagnosis {datetime.now():%Y-%m-%d %H:%M}\n\n{answer}\n\n---\n\n{evidence}", encoding="utf-8"
            )
            st.success(f"Saved to reports/{name}")

with tab_waits:
    if st.button("Load wait stats"):
        try:
            st.session_state["waits"] = db.wait_stats(get_conn(server, database))
        except Exception as exc:
            st.error(f"Could not load wait stats (needs VIEW SERVER STATE): {exc}")
    waits = st.session_state.get("waits")
    if waits is not None:
        st.dataframe(waits, use_container_width=True, hide_index=True)
        if st.button("Explain waits with AI"):
            with st.spinner("Asking the LLM..."):
                try:
                    st.markdown(advisor.explain_waits(waits))
                except Exception as exc:
                    st.error(f"LLM call failed: {exc}")
