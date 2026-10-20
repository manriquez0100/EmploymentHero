import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import pearsonr


# ============================================================
# CONFIGURACIÓN
# ============================================================

LOG_PATH = "system_signals.log"
OUTPUT_DIR = "results"

TABLES_OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "tables_results.dm"
)

CORRELATION_IMAGE_PATH = os.path.join(
    OUTPUT_DIR,
    "signal_correlation_matrix.png"
)

PVALUES_IMAGE_PATH = os.path.join(
    OUTPUT_DIR,
    "signal_pvalues_matrix.png"
)

DASHBOARD_IMAGE_PATH = os.path.join(
    OUTPUT_DIR,
    "signal_correlation_dashboard.png"
)

SIGNAL_COUNTS_IMAGE_PATH = os.path.join(
    OUTPUT_DIR,
    "signal_frequency.png"
)

SEVERITY_COUNTS_IMAGE_PATH = os.path.join(
    OUTPUT_DIR,
    "severity_frequency.png"
)

# Puntuaciones operativas heurísticas por severidad.
SEVERITY_WEIGHTS = {
    "ERROR": 5,
    "WARN": 10,
    "WARNING": 3,
    "INFO": 1
}


# ============================================================
# UTILIDADES PARA GUARDAR TABLAS
# ============================================================


from pathlib import Path

def initialize_table_results(output_path=TABLES_OUTPUT_PATH):
    """
    Copia el contenido de prompt.dm al inicio de tables_results.dm.
    Ambos archivos se encuentran en la estructura del proyecto.
    """
    # Carpeta donde está este archivo Python.
    base_dir = Path(__file__).resolve().parent

    # prompt.dm está en la misma carpeta que el código.
    prompt_path = base_dir / "prompt.dm"

    # Ruta absoluta del archivo de salida.
    output_path = Path(output_path)
    if not output_path.is_absolute():
        output_path = base_dir / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"No se encontró el prompt: {prompt_path}"
        )

    prompt = prompt_path.read_text(encoding="utf-8")

    if not prompt.strip():
        raise ValueError(f"El archivo está vacío: {prompt_path}")

    with output_path.open("w", encoding="utf-8", newline="") as file:
        file.write(prompt)
        file.write("\n\n---\n\n")
        file.write("# Resultados del análisis de telemetría\n\n")
        file.write(
            "Archivo generado automáticamente por el script de análisis.\n\n"
        )

    print(f"Prompt leído desde: {prompt_path}")
    print(f"Caracteres copiados: {len(prompt)}")
    print(f"Archivo de salida: {output_path.resolve()}")


def save_table_to_dm(
    table,
    table_name,
    output_path=TABLES_OUTPUT_PATH,
    index=True
):
    """
    Guarda un DataFrame o Series como tabla Markdown dentro del archivo .dm.
    """
    if isinstance(table, pd.Series):
        table = table.to_frame()

    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)

    with open(output_path, "a", encoding="utf-8") as file:
        file.write(f"## {table_name}\n\n")
        file.write(table.to_markdown(index=index, tablefmt="pipe"))
        file.write("\n\n---\n\n")


def save_table_as_image(
    table,
    output_path,
    title,
    decimals=3,
    index=True
):
    """
    Genera una imagen independiente de una tabla.
    """
    display_table = table.copy()

    if isinstance(display_table, pd.Series):
        display_table = display_table.to_frame()

    for column in display_table.select_dtypes(
        include=["number"]
    ).columns:
        display_table[column] = display_table[column].round(decimals)

    row_count = len(display_table)
    col_count = len(display_table.columns)

    fig, ax = plt.subplots(
        figsize=(
            max(8, col_count * 1.6),
            max(3, row_count * 0.5 + 1.5)
        )
    )

    ax.axis("off")
    ax.set_title(title, fontsize=13, pad=16)

    row_labels = (
        display_table.index.astype(str).tolist()
        if index else None
    )

    table_artist = ax.table(
        cellText=display_table.values,
        rowLabels=row_labels,
        colLabels=display_table.columns.astype(str),
        cellLoc="center",
        loc="center"
    )

    table_artist.auto_set_font_size(False)
    table_artist.set_fontsize(9)
    table_artist.scale(1, 1.4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ============================================================
# CARGA DE LOGS
# ============================================================

def load_logs(log_path, max_logs=None):
    """
    Lee logs en formato JSON Lines.
    Cada línea debe contener un objeto JSON.
    Las líneas con JSON inválido se ignoran.
    """
    records = []
    invalid_lines = 0

    if not os.path.exists(log_path):
        raise FileNotFoundError(
            f"No se encontró el archivo de logs: {log_path}"
        )

    with open(log_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

                if isinstance(record, dict):
                    records.append(record)
                else:
                    invalid_lines += 1

            except json.JSONDecodeError:
                invalid_lines += 1
                print(
                    f"Advertencia: JSON inválido en línea {line_number}."
                )

            if max_logs is not None and len(records) >= max_logs:
                break

    if not records:
        raise ValueError(
            "No se encontraron registros JSON válidos en el archivo."
        )

    df = pd.DataFrame(records)

    print(f"Logs cargados: {len(df)}")
    print(f"Líneas inválidas o descartadas: {invalid_lines}")

    print("Total de entradas:", len(df))
    print("Session IDs únicos:", df["session_id"].nunique())
    print("Entradas sin session_id:", df["session_id"].isna().sum())

    print("\nEventos por sesión:")
    print(df.groupby("session_id").size().describe())

    print("\nSesiones con más eventos:")
    print(df.groupby("session_id").size().sort_values(ascending=False).head(10))

    return df


# ============================================================
# PREPROCESAMIENTO
# ============================================================

def extract_eval_ms(details):
    """
    Extrae eval_ms del campo details, cuando está disponible.
    """
    if isinstance(details, dict):
        value = details.get("eval_ms")

    elif isinstance(details, str):
        try:
            parsed = json.loads(details)
            value = (
                parsed.get("eval_ms")
                if isinstance(parsed, dict)
                else None
            )
        except json.JSONDecodeError:
            value = None

    else:
        value = None

    try:
        return float(value) if value is not None else np.nan
    except (TypeError, ValueError):
        return np.nan


def preprocess_dataframe(df):
    """
    Normaliza los campos requeridos para el análisis.
    """
    df = df.copy()

    required_columns = [
        "session_id",
        "signal_category"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Faltan columnas requeridas: {missing_columns}"
        )

    df["session_id"] = df["session_id"].astype("string").str.strip()
    df["signal_category"] = (
        df["signal_category"].astype("string").str.strip()
    )

    df = df.dropna(
        subset=["session_id", "signal_category"]
    )

    df = df[
        (df["session_id"] != "") &
        (df["signal_category"] != "")
    ].copy()

    if df.empty:
        raise ValueError(
            "No quedan registros válidos después del preprocesamiento."
        )

    if "severity" not in df.columns:
        df["severity"] = "INFO"

    df["severity"] = (
        df["severity"]
        .fillna("INFO")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df.loc[df["severity"] == "", "severity"] = "INFO"

    if "details" in df.columns:
        df["eval_ms"] = df["details"].apply(extract_eval_ms)
    else:
        df["eval_ms"] = np.nan

    return df


# ============================================================
# MATRIZ BINARIA POR SESIÓN
# ============================================================

def build_session_matrix(df):
    """
    Cada fila representa una sesión.
    Cada columna representa una categoría de señal.
    El valor es 1 si la sesión contiene la señal y 0 si no.
    """
    session_matrix = (
        pd.crosstab(
            df["session_id"],
            df["signal_category"]
        ) > 0
    ).astype(int)

    session_matrix = session_matrix.sort_index(axis=1)

    return session_matrix


# ============================================================
# CORRELACIONES DE PEARSON Y VALORES P
# ============================================================

def calculate_correlations_with_pvalues(session_matrix):
    """
    Calcula la correlación de Pearson y el valor p para cada
    par de columnas.

    Si una columna es constante, la correlación correspondiente
    se deja como NaN.

    Los valores p de la diagonal se dejan como NaN porque una
    prueba de significación de una variable consigo misma no
    aporta una inferencia útil.
    """
    cols = session_matrix.columns
    n_cols = len(cols)

    corr_matrix = pd.DataFrame(
        np.nan,
        index=cols,
        columns=cols,
        dtype=float
    )

    pval_matrix = pd.DataFrame(
        np.nan,
        index=cols,
        columns=cols,
        dtype=float
    )

    for i in range(n_cols):
        x = session_matrix.iloc[:, i].to_numpy(dtype=float)

        # La correlación de una variable no constante consigo
        # misma es 1.
        if np.unique(x).size >= 2:
            corr_matrix.iloc[i, i] = 1.0

        for j in range(i + 1, n_cols):
            y = session_matrix.iloc[:, j].to_numpy(dtype=float)

            # Pearson no está definido si una de las variables
            # no presenta variabilidad.
            if np.unique(x).size < 2 or np.unique(y).size < 2:
                continue

            r, p_value = pearsonr(x, y)

            corr_matrix.iloc[i, j] = r
            corr_matrix.iloc[j, i] = r

            pval_matrix.iloc[i, j] = p_value
            pval_matrix.iloc[j, i] = p_value

    return corr_matrix.round(3), pval_matrix


# ============================================================
# GRÁFICAS DE MATRICES
# ============================================================

def create_correlation_heatmap(corr_matrix, output_path):
    """
    Guarda una imagen que muestra únicamente las correlaciones.
    """
    fig_width = max(8, len(corr_matrix.columns) * 1.2)
    fig_height = max(6, len(corr_matrix.index) * 0.9)

    fig, ax = plt.subplots(
        figsize=(fig_width, fig_height)
    )

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        center=0,
        linewidths=0.5,
        square=True,
        mask=corr_matrix.isna(),
        ax=ax
    )

    ax.set_title("Matriz de correlaciones de Pearson")
    ax.set_xlabel("Categoría de señal")
    ax.set_ylabel("Categoría de señal")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def create_pvalues_heatmap(pval_matrix, output_path):
    """
    Guarda una imagen independiente de los valores p.

    La escala visual representa -log10(p):
    un valor más alto indica un valor p más pequeño.
    """
    log_pvals = -np.log10(
        pval_matrix.clip(lower=1e-300)
    )

    # Mantener la diagonal vacía.
    np.fill_diagonal(log_pvals.values, np.nan)

    fig_width = max(8, len(log_pvals.columns) * 1.2)
    fig_height = max(6, len(log_pvals.index) * 0.9)

    fig, ax = plt.subplots(
        figsize=(fig_width, fig_height)
    )

    sns.heatmap(
        log_pvals,
        annot=pval_matrix,
        fmt=".4f",
        cmap="viridis",
        linewidths=0.5,
        mask=log_pvals.isna(),
        square=True,
        ax=ax,
        cbar_kws={"label": "-log10(p)"}
    )

    ax.set_title("Valores p de las correlaciones de Pearson")
    ax.set_xlabel("Categoría de señal")
    ax.set_ylabel("Categoría de señal")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def create_combined_dashboard(
    corr_matrix,
    pval_matrix,
    output_path
):
    """
    Genera el dashboard original con ambas matrices.
    """
    log_pvals = -np.log10(
        pval_matrix.clip(lower=1e-300)
    )

    np.fill_diagonal(log_pvals.values, np.nan)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(
            max(14, len(corr_matrix.columns) * 2.4),
            max(6, len(corr_matrix.index) * 0.9)
        )
    )

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        center=0,
        linewidths=0.5,
        square=True,
        mask=corr_matrix.isna(),
        ax=axes[0]
    )

    axes[0].set_title("Correlación de Pearson")
    axes[0].set_xlabel("Categoría de señal")
    axes[0].set_ylabel("Categoría de señal")

    sns.heatmap(
        log_pvals,
        annot=pval_matrix,
        fmt=".4f",
        cmap="viridis",
        linewidths=0.5,
        mask=log_pvals.isna(),
        square=True,
        ax=axes[1],
        cbar_kws={"label": "-log10(p)"}
    )

    axes[1].set_title("Valores p")
    axes[1].set_xlabel("Categoría de señal")
    axes[1].set_ylabel("Categoría de señal")

    fig.suptitle(
        "Dashboard de correlaciones de señales",
        fontsize=15
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ============================================================
# ANÁLISIS DE CORRELACIONES
# ============================================================

def analyze_signal_correlations(df):
    """
    Construye la matriz binaria por sesión, calcula Pearson
    y guarda todas las tablas y las imágenes de correlación.
    """
    session_matrix = build_session_matrix(df)

    if len(session_matrix) < 2:
        raise ValueError(
            "Se requieren al menos dos sesiones para calcular "
            "correlaciones."
        )

    if len(session_matrix.columns) < 2:
        raise ValueError(
            "Se requieren al menos dos categorías de señal."
        )

    corr_matrix, pval_matrix = (
        calculate_correlations_with_pvalues(session_matrix)
    )

    print("\n=== MATRIZ DE CORRELACIONES DE PEARSON ===")
    print(corr_matrix)

    print("\n=== MATRIZ DE VALORES P ===")
    print(pval_matrix.round(6))

    # Guardar tablas. apendices
    #save_table_to_dm(
    #    session_matrix,
    #    "Matriz binaria de señales por sesión"
    #)

    save_table_to_dm(
        corr_matrix,
        "Matriz de correlaciones de Pearson"
    )

    save_table_to_dm(
        pval_matrix,#se quitan los round.
        "Matriz de valores p"
    )

    # Guardar imágenes independientes.
    create_correlation_heatmap(
        corr_matrix,
        CORRELATION_IMAGE_PATH
    )

    create_pvalues_heatmap(
        pval_matrix,
        PVALUES_IMAGE_PATH
    )

    # Guardar dashboard combinado.
    create_combined_dashboard(
        corr_matrix,
        pval_matrix,
        DASHBOARD_IMAGE_PATH
    )

    return session_matrix, corr_matrix, pval_matrix


# ============================================================
# ANÁLISIS DE FRECUENCIAS Y SEVERIDAD
# ============================================================

def analyze_telemetry_signals(df):
    """
    Genera tablas de frecuencia de señales y severidades,
    así como puntuaciones operativas ponderadas.
    """

    # --------------------------------------------------------
    # 1. Frecuencia por categoría
    # --------------------------------------------------------

    signal_counts = (
        df["signal_category"]
        .value_counts()
        .rename_axis("signal_category")
        .to_frame(name="event_count")
    )

    signal_counts["percentage"] = (
        signal_counts["event_count"] /
        signal_counts["event_count"].sum() * 100
    ).round(2)

    print("\n=== FRECUENCIA POR CATEGORÍA ===")
    print(signal_counts)

    save_table_to_dm(
        signal_counts,
        "Frecuencia por categoría de señal"
    )

    # Gráfica de frecuencia por categoría.
    fig, ax = plt.subplots(
        figsize=(max(9, len(signal_counts) * 1.1), 5)
    )

    signal_counts["event_count"].plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Frecuencia por categoría de señal")
    ax.set_xlabel("Categoría")
    ax.set_ylabel("Número de eventos")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(
        SIGNAL_COUNTS_IMAGE_PATH,
        dpi=200,
        bbox_inches="tight"
    )
    plt.close(fig)

    # --------------------------------------------------------
    # 2. Frecuencia por severidad
    # --------------------------------------------------------

    severity_counts = (
        df["severity"]
        .value_counts()
        .rename_axis("severity")
        .to_frame(name="event_count")
    )

    severity_counts["percentage"] = (
        severity_counts["event_count"] /
        severity_counts["event_count"].sum() * 100
    ).round(2)

    print("\n=== FRECUENCIA POR SEVERIDAD ===")
    print(severity_counts)

    save_table_to_dm(
        severity_counts,
        "Frecuencia por severidad"
    )

    # Gráfica de frecuencia por severidad.
    fig, ax = plt.subplots(figsize=(8, 5))

    severity_counts["event_count"].plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Frecuencia por severidad")
    ax.set_xlabel("Severidad")
    ax.set_ylabel("Número de eventos")
    ax.tick_params(axis="x", rotation=0)

    fig.tight_layout()
    fig.savefig(
        SEVERITY_COUNTS_IMAGE_PATH,
        dpi=200,
        bbox_inches="tight"
    )
    plt.close(fig)

    # --------------------------------------------------------
    # 3. Puntuación ponderada por evento
    # --------------------------------------------------------

    df_scored = df.copy()

    df_scored["severity_weight"] = (
        df_scored["severity"]
        .map(SEVERITY_WEIGHTS)
        .fillna(0)
    )

    unknown_severities = sorted(
        set(df_scored["severity"]) -
        set(SEVERITY_WEIGHTS)
    )

    if unknown_severities:
        print(
            "\nAdvertencia: estas severidades no tienen peso "
            f"configurado y reciben 0: {unknown_severities}"
        )

    # Puntuación acumulada por categoría de señal.
    score_by_signal = (
        df_scored.groupby("signal_category")["severity_weight"]
        .agg(["count", "sum", "mean"])
        .rename(columns={
            "count": "event_count",
            "sum": "weighted_score",
            "mean": "mean_weight_per_event"
        })
        .sort_values("weighted_score", ascending=False)
        .round(3)
    )

    print("\n=== PUNTUACIÓN PONDERADA POR CATEGORÍA ===")
    print(score_by_signal)

    save_table_to_dm(
        score_by_signal,
        "Puntuación ponderada por categoría de señal"
    )

    # Puntuación acumulada por sesión.
    score_by_session = (
        df_scored.groupby("session_id")
        .agg(
            event_count=("signal_category", "size"),
            weighted_score=("severity_weight", "sum"),
            distinct_signals=("signal_category", "nunique")
        )
        .sort_values("weighted_score", ascending=False)
    )

    #print("\n=== PUNTUACIÓN PONDERADA POR SESIÓN ===")
    #print(score_by_session.head(20))

    #save_table_to_dm(
    #    score_by_session,
    #    "Puntuación ponderada por sesión"
    #)

    # --------------------------------------------------------
    # 4. Resumen descriptivo de las sesiones y los eventos
    # --------------------------------------------------------

    summary = pd.DataFrame({
        "metric": [
            "total_events",
            "total_sessions",
            "distinct_signal_categories",
            "distinct_severities",
            "total_weighted_score",
            "mean_events_per_session",
            "mean_eval_ms",
            "median_eval_ms"
        ],
        "value": [
            len(df_scored),
            df_scored["session_id"].nunique(),
            df_scored["signal_category"].nunique(),
            df_scored["severity"].nunique(),
            df_scored["severity_weight"].sum(),
            df_scored.groupby("session_id").size().mean(),
            df_scored["eval_ms"].mean(),
            df_scored["eval_ms"].median()
        ]
    })

    print("\n=== RESUMEN DESCRIPTIVO ===")
    print(summary)

    save_table_to_dm(
        summary,
        "Resumen descriptivo del conjunto de datos",
        index=False
    )

    # --------------------------------------------------------
    # 5. Resumen por severidad y categoría
    # --------------------------------------------------------

    severity_by_signal = pd.crosstab(
        df_scored["signal_category"],
        df_scored["severity"]
    )

    print("\n=== SEVERIDAD POR CATEGORÍA ===")
    print(severity_by_signal)

    save_table_to_dm(
        severity_by_signal,
        "Tabla cruzada de categoría y severidad"
    )

    # --------------------------------------------------------
    # 6. Estadísticas de eval_ms, si hay datos disponibles
    # --------------------------------------------------------

    eval_data = df_scored["eval_ms"].dropna()

    if not eval_data.empty:
        eval_summary = eval_data.describe().to_frame(
            name="eval_ms"
        )

        print("\n=== ESTADÍSTICAS DE eval_ms ===")
        print(eval_summary)

        save_table_to_dm(
            eval_summary,
            "Estadísticas descriptivas de eval_ms"
        )

        eval_by_signal = (
            df_scored.groupby("signal_category")["eval_ms"]
            .agg(["count", "mean", "median", "std", "min", "max"])
            .round(3)
        )

        print("\n=== eval_ms POR CATEGORÍA ===")
        print(eval_by_signal)

        save_table_to_dm(
            eval_by_signal,
            "Estadísticas de eval_ms por categoría"
        )


# ============================================================
# PROBABILIDADES CONDICIONALES OPCIONALES
# ============================================================

def calculate_conditional_probabilities(session_matrix):
    """
    Calcula probabilidades condicionales entre señales.

    P(B | A) = sesiones con A y B / sesiones con A.

    Estas probabilidades son distintas de la correlación de Pearson.
    """
    columns = session_matrix.columns
    results = []

    for signal_a in columns:
        mask_a = session_matrix[signal_a] == 1
        count_a = int(mask_a.sum())

        for signal_b in columns:
            if signal_a == signal_b:
                continue

            count_b_given_a = int(
                (
                    mask_a &
                    (session_matrix[signal_b] == 1)
                ).sum()
            )

            probability = (
                count_b_given_a / count_a
                if count_a > 0
                else np.nan
            )

            results.append({
                "signal_A": signal_a,
                "signal_B": signal_b,
                "sessions_with_A": count_a,
                "sessions_with_A_and_B": count_b_given_a,
                "P_B_given_A": probability
            })

    conditional_df = pd.DataFrame(results)

    save_table_to_dm(
        conditional_df.round(6),
        "Probabilidades condicionales entre señales",
        index=False
    )

    print("\n=== PROBABILIDADES CONDICIONALES ===")
    print(conditional_df.round(4))

    return conditional_df


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Reiniciar el archivo tabular al comienzo de cada ejecución.
    initialize_table_results(TABLES_OUTPUT_PATH)

    print("Cargando logs...")
    df = load_logs(LOG_PATH)

    print("\nPreprocesando datos...")
    df = preprocess_dataframe(df)

    print("\nGenerando tablas de frecuencia y severidad...")
    analyze_telemetry_signals(df)

    print("\nCalculando correlaciones...")
    session_matrix, corr_matrix, pval_matrix = (
        analyze_signal_correlations(df)
    )

    print("\nCalculando probabilidades condicionales...")
    conditional_df = calculate_conditional_probabilities(
        session_matrix
    )

    print("\n=== ARCHIVOS GENERADOS ===")
    print(f"Tablas consolidadas: {TABLES_OUTPUT_PATH}")
    print(f"Matriz de correlación: {CORRELATION_IMAGE_PATH}")
    print(f"Matriz de valores p: {PVALUES_IMAGE_PATH}")
    print(f"Dashboard combinado: {DASHBOARD_IMAGE_PATH}")
    print(f"Frecuencia por categoría: {SIGNAL_COUNTS_IMAGE_PATH}")
    print(f"Frecuencia por severidad: {SEVERITY_COUNTS_IMAGE_PATH}")

    print("\nAnálisis finalizado.")


if __name__ == "__main__":
    main()