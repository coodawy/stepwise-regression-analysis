"""
VPCAStepwiseAnalysis: end-to-end VPCA + spectral-library stepwise workflow.

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

Workflow:
    1. Load VPCA loadings + spectral library, auto-detect wavelength columns,
       align wavelengths.
    2. Treat data as already z-scored (matches the v3 working flow).
    3. Run StepwiseVIFRegression for every VPC component.
    4. Produce a multi-sheet Excel report with SPSS-style incremental tables.
"""

from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .stepwise_vif import StepwiseVIFRegression
from .regression_tables import build_regression_tables


class VPCAStepwiseAnalysis:
    """End-to-end VPCA + spectral-library stepwise analysis."""

    def __init__(self, p_enter: float = 0.05, p_remove: float = 0.10,
                 vif_threshold: float = 2.0, max_iter: int = 100, verbose: int = 1):
        self.p_enter = p_enter
        self.p_remove = p_remove
        self.vif_threshold = vif_threshold
        self.max_iter = max_iter
        self.verbose = verbose

        self.z_loadings_: Optional[pd.DataFrame] = None
        self.z_library_: Optional[pd.DataFrame] = None
        self.summary_results_: Optional[pd.DataFrame] = None
        self.detailed_results_: Optional[pd.DataFrame] = None
        self.descriptive_stats_: Optional[pd.DataFrame] = None
        self.models_: Dict[str, StepwiseVIFRegression] = {}
        self.regression_tables_: Dict[str, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]] = {}

    # --- data loading ---
    def load_data(self, loadings_file: str, library_file: str
                  ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and align VPCA loadings + spectral library (assumed pre-z-scored)."""

        # Loadings
        loadings = pd.read_csv(loadings_file)
        wav_col = next(
            (c for c in loadings.columns
             if "centre_nm" in c or "wavelength" in c.lower()),
            loadings.columns[0],
        )
        loadings = loadings.set_index(wav_col)
        loadings = loadings.drop(
            ["Eigenvalues", "Frac Var", "Extracted Frac Var"], errors="ignore"
        )
        loadings = loadings[[c for c in loadings.columns if c.startswith("VPC")]]
        loadings = loadings.apply(pd.to_numeric, errors="coerce")
        loadings.index = pd.to_numeric(loadings.index, errors="coerce")
        loadings = loadings[loadings.index.notna()]

        # Library
        library = pd.read_csv(library_file)
        wav_col = next(
            (c for c in library.columns
             if "centre_nm" in c or "wavelength" in c.lower()),
            library.columns[0],
        )
        library = library.set_index(wav_col)
        library.index = pd.to_numeric(library.index, errors="coerce")
        library = library[library.index.notna()]
        library = library.apply(pd.to_numeric, errors="coerce")
        library = library.dropna(axis=1, how="all")
        library.columns = [
            c.replace("_Zdrdl", "").replace(" Zdrdl", "").strip()
            for c in library.columns
        ]
        drop_cols = [
            c for c in library.columns
            if "VPC" in c or c.startswith("IRL") or c == "Band" or "centre_nm" in c
        ]
        library = library.drop(columns=drop_cols, errors="ignore")

        # Align wavelengths
        loadings.index = pd.Index(np.round(loadings.index.values, 1))
        library.index = pd.Index(np.round(library.index.values, 1))
        common = sorted(set(loadings.index) & set(library.index))
        if not common:
            raise ValueError("No common wavelengths between loadings and library.")
        loadings = loadings.loc[common]
        library = library.loc[common]

        # Rename VPC columns -> VPCA_Z1, VPCA_Z2, ...
        loadings.columns = [f"VPCA_Z{i + 1}" for i in range(loadings.shape[1])]

        self.z_loadings_ = loadings
        self.z_library_ = library

        # Descriptive stats (sanity check that data is actually z-scored)
        all_z = pd.concat([loadings, library], axis=1)
        rows = []
        for col in all_z.columns:
            mean = float(all_z[col].mean())
            std = float(all_z[col].std(ddof=0))
            rows.append({
                "Variable": col,
                "N": len(all_z),
                "Mean": round(mean, 6),
                "Std Dev": round(std, 6),
                "Z-scored?": "yes" if abs(mean) < 1e-6 and abs(std - 1.0) < 1e-6 else "no",
            })
        self.descriptive_stats_ = pd.DataFrame(rows)

        if self.verbose > 0:
            print(
                f"Loaded {loadings.shape[1]} VPC components, "
                f"{library.shape[1]} library materials, "
                f"{len(common)} common wavelengths."
            )
            n_zscored = (self.descriptive_stats_["Z-scored?"] == "yes").sum()
            n_total = len(self.descriptive_stats_)
            print(
                f"Descriptive stats: {n_zscored}/{n_total} variables look z-scored "
                f"(mean~0, std~1)."
            )

        return loadings, library

    # --- analysis ---
    def run_analysis(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Run stepwise selection for every VPC component and build all tables."""
        if self.z_loadings_ is None or self.z_library_ is None:
            raise ValueError("Call load_data(...) first.")

        summary_rows, detailed_rows = [], []
        self.models_ = {}
        self.regression_tables_ = {}

        for vpc in self.z_loadings_.columns:
            if self.verbose > 0:
                print("\n" + "=" * 70)
                print(f"Analyzing {vpc}")
                print("=" * 70)

            sel = StepwiseVIFRegression(
                p_enter=self.p_enter,
                p_remove=self.p_remove,
                vif_threshold=self.vif_threshold,
                max_iter=self.max_iter,
                verbose=self.verbose,
            ).fit(self.z_library_, self.z_loadings_[vpc])
            self.models_[vpc] = sel

            selected = sel.selected_features_
            if selected:
                m = sel.model_
                r2 = float(m.rsquared)
                adj = float(m.rsquared_adj)
                vif_df = sel.get_vif()
                entry_p = sel.get_entry_pvalues()
                std_b = sel.get_standardized_coefs()

                for var in selected:
                    vif_val = (
                        float(vif_df.loc[vif_df["Variable"] == var, "VIF"].values[0])
                        if not vif_df.empty else np.nan
                    )
                    detailed_rows.append({
                        "Component": vpc,
                        "Material": var,
                        "VIF": round(vif_val, 2),
                        "R_squared": round(r2, 4),
                        "Adj_R_squared": round(adj, 4),
                        "Sig_p": (
                            round(float(entry_p.get(var, np.nan)), 4)
                            if var in entry_p.index else np.nan
                        ),
                        "Std_Beta": (
                            round(float(std_b.get(var, np.nan)), 4)
                            if var in std_b.index else np.nan
                        ),
                    })

                vif_details = (
                    ", ".join(
                        f"{r['Variable']}({r['VIF']:.2f})"
                        for _, r in vif_df.iterrows()
                    )
                    if not vif_df.empty else "N/A"
                )
                summary_rows.append({
                    "Component": vpc,
                    "N_Materials": len(selected),
                    "Materials": ", ".join(selected),
                    "R_squared": round(r2, 4),
                    "Adj_R_squared": round(adj, 4),
                    "Max_VIF": (
                        round(float(vif_df["VIF"].max()), 2)
                        if not vif_df.empty else np.nan
                    ),
                    "VIF_Details": vif_details,
                })

                # SPSS-style tables
                self.regression_tables_[vpc] = build_regression_tables(
                    vpc_name=vpc,
                    y=self.z_loadings_[vpc],
                    X=self.z_library_,
                    selected=selected,
                    history=sel.iteration_history_,
                )
            else:
                summary_rows.append({
                    "Component": vpc,
                    "N_Materials": 0,
                    "Materials": "None",
                    "R_squared": 0.0,
                    "Adj_R_squared": 0.0,
                    "Max_VIF": np.nan,
                    "VIF_Details": "N/A",
                })

        self.summary_results_ = pd.DataFrame(summary_rows)
        self.detailed_results_ = pd.DataFrame(detailed_rows)
        return self.summary_results_, self.detailed_results_

    def get_iteration_history_all(self) -> pd.DataFrame:
        """Combined iteration history across all components."""
        rows = []
        for vpc, m in self.models_.items():
            h = m.get_iteration_history()
            if not h.empty:
                h = h.copy()
                h.insert(0, "Component", vpc)
                rows.append(h)
        return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

    # --- export ---
    def export_results(self, output_dir: str,
                       base_filename: str = "stepwise_results") -> Dict[str, str]:
        """Write a complete Excel report.

        Sheets:
            - Summary, VIF_Details, IterationHistory, Descriptive_Stats, Settings
            - Per-VPC sheet with Model_Summary / ANOVA / Coefficients (SPSS-style)
        """
        os.makedirs(output_dir, exist_ok=True)
        out: Dict[str, str] = {}

        # CSV summary (quick-look)
        csv_path = os.path.join(output_dir, f"{base_filename}_summary.csv")
        if self.summary_results_ is not None:
            self.summary_results_.to_csv(csv_path, index=False)
            out["csv_summary"] = csv_path

        excel_path = os.path.join(output_dir, f"{base_filename}_detailed.xlsx")
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            if self.summary_results_ is not None:
                self.summary_results_.to_excel(
                    writer, sheet_name="Summary", index=False
                )

            if self.detailed_results_ is not None and not self.detailed_results_.empty:
                cols = ["Component", "Material", "VIF", "R_squared",
                        "Adj_R_squared", "Sig_p", "Std_Beta"]
                self.detailed_results_[cols].to_excel(
                    writer, sheet_name="VIF_Details", index=False
                )

            hist_all = self.get_iteration_history_all()
            if not hist_all.empty:
                hist_all.to_excel(writer, sheet_name="IterationHistory", index=False)

            if self.descriptive_stats_ is not None:
                self.descriptive_stats_.to_excel(
                    writer, sheet_name="Descriptive_Stats", index=False
                )

            # Per-VPC SPSS-style tables on individual sheets
            for vpc, (ms_df, anova_df, coef_df) in self.regression_tables_.items():
                sheet = vpc[:31]  # Excel sheet names <= 31 chars
                row = 0
                ms_df.to_excel(writer, sheet_name=sheet, startrow=row, index=False)
                row += len(ms_df) + 3
                anova_df.to_excel(writer, sheet_name=sheet, startrow=row, index=False)
                row += len(anova_df) + 3
                coef_df.to_excel(writer, sheet_name=sheet, startrow=row, index=False)

            settings_df = pd.DataFrame({
                "Parameter": ["p_enter", "p_remove", "vif_threshold", "max_iter", "method"],
                "Value": [self.p_enter, self.p_remove, self.vif_threshold,
                          self.max_iter, "bidirectional"],
                "Description": [
                    "p-value threshold to ADD variable",
                    "p-value threshold to REMOVE variable",
                    "Maximum VIF allowed",
                    "Max bidirectional iterations",
                    "Selection method",
                ],
            })
            settings_df.to_excel(writer, sheet_name="Settings", index=False)

        out["excel"] = excel_path
        if self.verbose > 0:
            print(f"\nWrote: {csv_path}")
            print(f"Wrote: {excel_path}")
        return out

    # --- accessors / plotting helpers ---
    def get_model(self, component: str) -> StepwiseVIFRegression:
        return self.models_[component]


def run_vpca_stepwise(
    z_loadings: pd.DataFrame,
    z_library: pd.DataFrame,
    p_enter: float = 0.05,
    p_remove: float = 0.10,
    vif_threshold: float = 2.0,
    max_iter: int = 100,
    verbose: int = 1,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, StepwiseVIFRegression]]:
    """Functional shortcut: run bidirectional stepwise per VPC.

    Returns
    -------
    (summary_df, detailed_df, models_dict)
    """
    summary_rows, detailed_rows, models = [], [], {}

    for vpc in z_loadings.columns:
        if verbose > 0:
            print(f"\n=== {vpc} ===")
        sel = StepwiseVIFRegression(
            p_enter=p_enter, p_remove=p_remove,
            vif_threshold=vif_threshold, max_iter=max_iter, verbose=verbose,
        ).fit(z_library, z_loadings[vpc])
        models[vpc] = sel
        chosen = sel.selected_features_

        if chosen:
            m = sel.model_
            r2 = float(m.rsquared)
            adj = float(m.rsquared_adj)
            vif_df = sel.get_vif()
            ep = sel.get_entry_pvalues()
            std_b = sel.get_standardized_coefs()
            for v in chosen:
                vif_val = (
                    float(vif_df.loc[vif_df["Variable"] == v, "VIF"].values[0])
                    if not vif_df.empty else np.nan
                )
                detailed_rows.append({
                    "Component": vpc,
                    "Material": v,
                    "VIF": round(vif_val, 2),
                    "R_squared": round(r2, 4),
                    "Adj_R_squared": round(adj, 4),
                    "Sig_p": round(float(ep.get(v, np.nan)), 4) if v in ep.index else np.nan,
                    "Std_Beta": round(float(std_b.get(v, np.nan)), 4) if v in std_b.index else np.nan,
                })
            summary_rows.append({
                "Component": vpc,
                "N_Materials": len(chosen),
                "Materials": ", ".join(chosen),
                "R_squared": round(r2, 4),
                "Adj_R_squared": round(adj, 4),
                "Max_VIF": round(float(vif_df["VIF"].max()), 2) if not vif_df.empty else np.nan,
                "VIF_Details": (
                    ", ".join(
                        f"{r['Variable']}({r['VIF']:.2f})"
                        for _, r in vif_df.iterrows()
                    ) if not vif_df.empty else "N/A"
                ),
            })
        else:
            summary_rows.append({
                "Component": vpc, "N_Materials": 0, "Materials": "None",
                "R_squared": 0.0, "Adj_R_squared": 0.0,
                "Max_VIF": np.nan, "VIF_Details": "N/A",
            })

    return pd.DataFrame(summary_rows), pd.DataFrame(detailed_rows), models
