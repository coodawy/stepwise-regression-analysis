"""
Stepwise Regression Analysis - Desktop App (Streamlit)

A local web app for running bidirectional stepwise regression with VIF control
on VPCA loadings + spectral library data.

Usage:
    streamlit run app.py

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences
"""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

# Make sure local 'framework' package is importable when running with streamlit
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from framework import VPCAStepwiseAnalysis, __version__  # noqa: E402

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Stepwise Regression Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Stepwise Regression Analysis")
st.caption(
    f"Bidirectional stepwise selection with joint p-value + VIF control | "
    f"v{__version__} | Kent State University"
)

# ---------------------------------------------------------------------------
# Sidebar - configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    p_enter = st.slider(
        "p_enter (add threshold)",
        min_value=0.001, max_value=0.20, value=0.05, step=0.005,
        help="Maximum p-value for ADDING a variable.",
    )
    p_remove = st.slider(
        "p_remove (remove threshold)",
        min_value=0.001, max_value=0.50, value=0.10, step=0.005,
        help="Minimum p-value to REMOVE a selected variable.",
    )
    vif_threshold = st.slider(
        "VIF threshold",
        min_value=1.1, max_value=10.0, value=2.0, step=0.1,
        help="Maximum acceptable VIF for any selected variable.",
    )
    max_iter = st.number_input(
        "Max iterations", min_value=10, max_value=1000, value=100, step=10
    )
    verbose = st.selectbox(
        "Verbosity", options=[0, 1, 2], index=0,
        help="0 = silent, 1 = step-by-step, 2 = detailed (printed to terminal).",
    )

    st.markdown("---")
    st.markdown(
        "**Defaults**\n\n"
        "- `p_enter` = 0.05\n"
        "- `p_remove` = 0.10\n"
        "- `VIF` = 2.0 (strict, recommended for spectral mixing)"
    )

# ---------------------------------------------------------------------------
# Data input
# ---------------------------------------------------------------------------
st.header("1. Data")

source = st.radio(
    "Data source",
    options=["Use bundled test data", "Upload my own files"],
    horizontal=True,
)

loadings_path: str | None = None
library_path: str | None = None

if source == "Use bundled test data":
    test_loadings = REPO_ROOT / "learning" / "test-data" / "test_loadings.csv"
    test_library = REPO_ROOT / "learning" / "test-data" / "test_library.csv"
    if test_loadings.exists() and test_library.exists():
        loadings_path = str(test_loadings)
        library_path = str(test_library)
        st.success(
            f"Using bundled test data:\n"
            f"- Loadings: `{test_loadings.relative_to(REPO_ROOT)}`\n"
            f"- Library: `{test_library.relative_to(REPO_ROOT)}`"
        )
    else:
        st.error("Bundled test data not found. Please upload your own files.")
else:
    col1, col2 = st.columns(2)
    with col1:
        loadings_upload = st.file_uploader(
            "VPCA loadings CSV",
            type=["csv"],
            help="Wavelengths in rows, VPC components in columns.",
        )
    with col2:
        library_upload = st.file_uploader(
            "Spectral library CSV",
            type=["csv"],
            help="Wavelengths in rows, library materials in columns.",
        )

    if loadings_upload and library_upload:
        # Persist uploads to a temp dir so the framework can read them with pd.read_csv
        tmp = tempfile.mkdtemp(prefix="stepwise_")
        loadings_path = str(Path(tmp) / loadings_upload.name)
        library_path = str(Path(tmp) / library_upload.name)
        Path(loadings_path).write_bytes(loadings_upload.getvalue())
        Path(library_path).write_bytes(library_upload.getvalue())
        st.success(f"Saved uploads to temp dir: `{tmp}`")

# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------
st.header("2. Run analysis")

run = st.button(
    "▶ Run stepwise regression",
    type="primary",
    disabled=not (loadings_path and library_path),
)

if run:
    with st.spinner("Loading data..."):
        analyzer = VPCAStepwiseAnalysis(
            p_enter=p_enter,
            p_remove=p_remove,
            vif_threshold=vif_threshold,
            max_iter=int(max_iter),
            verbose=int(verbose),
        )
        try:
            analyzer.load_data(loadings_path, library_path)
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            st.stop()

    with st.spinner("Running bidirectional stepwise per VPC..."):
        try:
            summary, detailed = analyzer.run_analysis()
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    st.session_state["analyzer"] = analyzer
    st.session_state["summary"] = summary
    st.session_state["detailed"] = detailed
    st.success("Analysis complete.")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if "analyzer" in st.session_state:
    analyzer = st.session_state["analyzer"]
    summary = st.session_state["summary"]
    detailed = st.session_state["detailed"]

    st.header("3. Results")

    tab_summary, tab_detail, tab_history, tab_descstats, tab_plots, tab_export = st.tabs(
        ["Summary", "VIF Details", "Iteration History", "Descriptive Stats",
         "Plots", "Export"]
    )

    with tab_summary:
        st.dataframe(summary, use_container_width=True)

    with tab_detail:
        st.dataframe(detailed, use_container_width=True)

    with tab_history:
        hist = analyzer.get_iteration_history_all()
        if hist.empty:
            st.info("No iteration history available.")
        else:
            st.dataframe(hist, use_container_width=True)

    with tab_descstats:
        if analyzer.descriptive_stats_ is not None:
            st.dataframe(analyzer.descriptive_stats_, use_container_width=True)
            n_zscored = (analyzer.descriptive_stats_["Z-scored?"] == "yes").sum()
            n_total = len(analyzer.descriptive_stats_)
            st.caption(
                f"{n_zscored}/{n_total} variables have mean ~ 0 and std ~ 1 "
                f"(z-scored sanity check)."
            )

    with tab_plots:
        components = list(summary["Component"].astype(str))
        if not components:
            st.info("No components to plot.")
        else:
            # Overview
            st.subheader("Overview - all components")
            from framework import plot_all_components

            fig = plot_all_components(analyzer)
            if fig is not None:
                st.pyplot(fig)

            st.markdown("---")

            # Per-component
            comp = st.selectbox("Component", components)
            from framework import (
                plot_component, plot_iteration_history,
                plot_vif, plot_coefficients,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"{comp} - Std Beta & Sig p")
                fig = plot_component(analyzer, comp)
                if fig is not None:
                    st.pyplot(fig)
            with col2:
                st.subheader(f"{comp} - VIF")
                model = analyzer.get_model(comp)
                fig = plot_vif(model)
                if fig is not None:
                    st.pyplot(fig)

            col3, col4 = st.columns(2)
            with col3:
                st.subheader(f"{comp} - Iteration history")
                fig = plot_iteration_history(model)
                if fig is not None:
                    st.pyplot(fig)
            with col4:
                st.subheader(f"{comp} - Coefficients (95% CI)")
                fig = plot_coefficients(model)
                if fig is not None:
                    st.pyplot(fig)

            with st.expander(f"Text summary for {comp}"):
                st.code(model.summary(), language="text")

    with tab_export:
        st.write("Generate the full Excel report (with all SPSS-style sheets):")
        if st.button("Generate Excel report"):
            tmp = Path(tempfile.mkdtemp(prefix="stepwise_export_"))
            files = analyzer.export_results(str(tmp))
            excel_path = files.get("excel")
            csv_path = files.get("csv_summary")
            if excel_path:
                with open(excel_path, "rb") as f:
                    st.download_button(
                        "⬇ Download Excel (.xlsx)",
                        data=f.read(),
                        file_name="stepwise_results_detailed.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            if csv_path:
                with open(csv_path, "rb") as f:
                    st.download_button(
                        "⬇ Download Summary (.csv)",
                        data=f.read(),
                        file_name="stepwise_results_summary.csv",
                        mime="text/csv",
                    )
            st.success(f"Wrote files to `{tmp}`")

else:
    st.info("Configure data and parameters, then click **Run stepwise regression**.")
