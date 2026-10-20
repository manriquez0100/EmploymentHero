import json
import os
import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# ============================================================
# CONFIGURACIÓN DE ESCENARIO
# ============================================================

CONFIG = {

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    "total_sessions": 3000,

    "simulation_days": 25,

    "random_seed": 22,

    # --------------------------------------------------------
    # TECH DEBT
    # --------------------------------------------------------

    "tech_debt": {
        "probability": 0.05,

        "severity": [
            "ERROR",
            "WARN"
        ],

        "component": "WorkflowEngine",

        "rule": "EnterpriseCustomApprovalRule_Acme",

        "eval_ms": {
            "min": 2000,
            "max": 6000
        },

        "issue": "hardcoded_rule_bottleneck"
    },

    # --------------------------------------------------------
    # SYSTEM LAG
    # --------------------------------------------------------

    "system_lag": {

        # Probabilidad de que TECH_DEBT produzca SYSTEM_LAG
        "probability_from_tech_debt": 0.60,

        "delay_seconds": {
            "min": 1,
            "max": 4
        },

        "endpoint": "/api/v1/candidates/search",

        "action": "candidate_search",

        "latency_ms": {
            "min": 3500,
            "max": 11000
        },

        "status": 504,

        "severity": [
            "ERROR",
            "WARN"
        ]
    },

    # --------------------------------------------------------
    # OPERATIONAL OVERHEAD
    # --------------------------------------------------------

    "operational_overhead": {

        # Probabilidad de ticket después de SYSTEM_LAG
        "probability_from_lag": 0.10,

        "delay_seconds": {
            "min": 10,
            "max": 60
        },

        "ticket_id": {
            "prefix": "SUP",
            "min": 1000,
            "max": 9999
        },

        "type": "candidate_search_timeout",

        "impact": "high",

        "severity": "ERROR"
    },

    # --------------------------------------------------------
    # FEATURE PRESSURE
    # --------------------------------------------------------

    "feature_pressure": {

        "probability": 0.70,

        "delay_seconds": {
            "min": 5,
            "max": 30
        },

        "severity": "INFO",

        "client_segment": "Enterprise",

        "features": [
            "automated_cv_screening",
            "interview_scheduling_bot"
        ],

        "contract_value_at_risk": [
            "high"
        ]
    },

    # --------------------------------------------------------
    # LOW ADOPTION
    # --------------------------------------------------------

    "low_adoption": {

        "probability": 0.20,#original .15

        "delay_seconds": {
            "min": 5,
            "max": 30
        },

        "severity": "INFO",

        "features": [
            "candidate_feedback_form"
        ],

        "actions": [
            "form_abandoned"
        ],

        "reasons": [
            "user_preferred_slack"
        ]
    }
}


# ============================================================
# HELPERS
# ============================================================

def random_int(config):
    return random.randint(
        config["min"],
        config["max"]
    )


def random_delay(config):
    return timedelta(
        seconds=random_int(config)
    )


def random_choice(values):
    return random.choice(values)


# ============================================================
# GENERACIÓN DE LOGS
# ============================================================

def generate_correlated_logs(log_path, config):

    print("Generando trazas de telemetría...")

    # --------------------------------------------------------
    # Random seed
    # --------------------------------------------------------

    random.seed(config["random_seed"])
    np.random.seed(config["random_seed"])

    # --------------------------------------------------------
    # Tiempo inicial
    # --------------------------------------------------------

    start_time = (
        datetime.now()
        - timedelta(days=config["simulation_days"])
    )

    logs = []

    total_sessions = config["total_sessions"]

    # --------------------------------------------------------
    # Sesiones
    # --------------------------------------------------------

    for _ in range(total_sessions):

        session_id = (
            f"sess_{random.randint(10000, 99999)}"
        )

        base_time = (
            start_time
            + timedelta(
                seconds=random.randint(
                    0,
                    config["simulation_days"] * 24 * 3600
                )
            )
        )

        # ====================================================
        # TECH DEBT
        # ====================================================

        tech_debt_config = config["tech_debt"]

        has_tech_debt = (
            random.random()
            < tech_debt_config["probability"]
        )

        if has_tech_debt:

            logs.append({
                "timestamp": base_time.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ),

                "session_id": session_id,

                "signal_category": "TECH_DEBT",

                "severity": random_choice(
                    tech_debt_config["severity"]
                ),

                "details": {

                    "component":
                        tech_debt_config["component"],

                    "rule":
                        tech_debt_config["rule"],

                    "eval_ms":
                        random_int(
                            tech_debt_config["eval_ms"]
                        ),

                    "issue":
                        tech_debt_config["issue"]
                }
            })

            # =================================================
            # SYSTEM LAG
            # =================================================

            lag_config = config["system_lag"]

            has_system_lag = (
                random.random()
                < lag_config["probability_from_tech_debt"]
            )

            if has_system_lag:

                lag_time = (
                    base_time
                    + random_delay(
                        lag_config["delay_seconds"]
                    )
                )

                logs.append({
                    "timestamp": lag_time.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),

                    "session_id": session_id,

                    "signal_category": "SYSTEM_LAG",

                    "severity": random_choice(
                        lag_config["severity"]
                    ),

                    "details": {

                        "endpoint":
                            lag_config["endpoint"],

                        "action":
                            lag_config["action"],

                        "latency_ms":
                            random_int(
                                lag_config["latency_ms"]
                            ),

                        "status":
                            lag_config["status"]
                    }
                })

                # =============================================
                # OPERATIONAL OVERHEAD
                # =============================================

                overhead_config = (
                    config["operational_overhead"]
                )

                has_ticket = (
                    random.random()
                    < overhead_config[
                        "probability_from_lag"
                    ]
                )

                if has_ticket:

                    ticket_time = (
                        lag_time
                        + random_delay(
                            overhead_config["delay_seconds"]
                        )
                    )

                    ticket_prefix = (
                        overhead_config["ticket_id"]["prefix"]
                    )

                    ticket_number = random_int(
                        overhead_config["ticket_id"]
                    )

                    logs.append({
                        "timestamp":
                            ticket_time.strftime(
                                "%Y-%m-%dT%H:%M:%S.%fZ"
                            ),

                        "session_id":
                            session_id,

                        "signal_category":
                            "OPERATIONAL_OVERHEAD",

                        "severity":
                            overhead_config["severity"],

                        "details": {

                            "ticket_id":
                                f"{ticket_prefix}-{ticket_number}",

                            "type":
                                overhead_config["type"],

                            "impact":
                                overhead_config["impact"]
                        }
                    })

        # ====================================================
        # FEATURE PRESSURE
        # ====================================================

        fp_config = config["feature_pressure"]

        has_feature_pressure = (
            random.random()
            < fp_config["probability"]
        )

        if has_feature_pressure:

            fp_time = (
                base_time
                + random_delay(
                    fp_config["delay_seconds"]
                )
            )

            logs.append({
                "timestamp":
                    fp_time.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),

                "session_id":
                    session_id,

                "signal_category":
                    "FEATURE_PRESSURE",

                "severity":
                    fp_config["severity"],

                "details": {

                    "client_segment":
                        fp_config["client_segment"],

                    "feature_requested":
                        random_choice(
                            fp_config["features"]
                        ),

                    "contract_value_at_risk":
                        random_choice(
                            fp_config[
                                "contract_value_at_risk"
                            ]
                        )
                }
            })

        # ====================================================
        # LOW ADOPTION
        # ====================================================

        la_config = config["low_adoption"]

        has_low_adoption = (
            random.random()
            < la_config["probability"]
        )

        if has_low_adoption:

            la_time = (
                base_time
                + random_delay(
                    la_config["delay_seconds"]
                )
            )

            logs.append({
                "timestamp":
                    la_time.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),

                "session_id":
                    session_id,

                "signal_category":
                    "LOW_ADOPTION",

                "severity":
                    la_config["severity"],

                "details": {

                    "feature":
                        random_choice(
                            la_config["features"]
                        ),

                    "action":
                        random_choice(
                            la_config["actions"]
                        ),

                    "reason":
                        random_choice(
                            la_config["reasons"]
                        )
                }
            })

    # ========================================================
    # ORDENAR
    # ========================================================

    logs.sort(
        key=lambda x: x["timestamp"]
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ) as f:

        for log in logs:

            f.write(
                json.dumps(log)
                + "\n"
            )

    print(
        f"Generados {len(logs)} registros "
        f"de telemetría en: {log_path}\n"
    )


# ============================================================
# ANÁLISIS
# ============================================================

def analyze_signal_correlations(
    log_path,
    output_heatmap_path
):

    logs = []

    if not os.path.exists(log_path):

        print(
            f"Error: No se encontró "
            f"el archivo {log_path}"
        )

        return

    with open(
        log_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():

                logs.append(
                    json.loads(
                        line.strip()
                    )
                )

    df = pd.DataFrame(logs)

    # --------------------------------------------------------
    # Validar session_id
    # --------------------------------------------------------

    if "session_id" not in df.columns:

        df["session_id"] = [
            f"tx_{i % 100}"
            for i in range(len(df))
        ]

    # --------------------------------------------------------
    # One-Hot por sesión
    # --------------------------------------------------------

    session_matrix = pd.crosstab(
        df["session_id"],
        df["signal_category"]
    )

    # --------------------------------------------------------
    # Pearson
    # --------------------------------------------------------

    corr_matrix = (
        session_matrix.corr()
    )

    print("=" * 75)

    print(
        "MATRIZ DE CORRELACIÓN DE PEARSON "
        "(CAUSALIDAD TÉCNICO-OPERATIVA)"
    )

    print("=" * 75)

    print(
        corr_matrix.round(3)
    )

    print("=" * 75)

    # --------------------------------------------------------
    # Heatmap
    # --------------------------------------------------------

    plt.style.use(
        "seaborn-v0_8-whitegrid"
        if "seaborn-v0_8-whitegrid"
        in plt.style.available
        else "default"
    )

    fig, ax = plt.subplots(
        figsize=(9, 7)
    )

    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        fmt=".2f",
        linewidths=0.8,
        cbar_kws={
            "label":
                "Coeficiente de Pearson (r)"
        },
        ax=ax
    )

    ax.set_title(
        "Employment Hero RMS - "
        "Causal Signal Correlation Heatmap",
        fontsize=12,
        fontweight="bold",
        pad=15
    )

    ax.set_xlabel(
        "Signal Categories",
        fontsize=11,
        labelpad=10
    )

    ax.set_ylabel(
        "Signal Categories",
        fontsize=11,
        labelpad=10
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.yticks(
        rotation=0
    )

    plt.tight_layout()

    plt.savefig(
        output_heatmap_path,
        dpi=300
    )

    plt.close()

    print(
        "Mapa de correlación exportado "
        f"exitosamente a: "
        f"{output_heatmap_path}\n"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    log_file = (
        r"C:\Employment Hero\system_signals.log"
    )

    heatmap_file = (
        r"C:\Employment Hero"
        r"\signal_correlation_heatmap.png"
    )

    generate_correlated_logs(
        log_file,
        CONFIG
    )

    analyze_signal_correlations(
        log_file,
        heatmap_file
    )