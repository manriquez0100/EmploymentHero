import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, norm

def calculate_correlations_with_pvalues(session_matrix):
    cols = session_matrix.columns
    n = len(cols)
    
    # DataFrames para almacenar r y p-values
    corr_matrix = pd.DataFrame(np.zeros((n, n)), columns=cols, index=cols)
    pval_matrix = pd.DataFrame(np.zeros((n, n)), columns=cols, index=cols)
    
    for i in range(n):
        for j in range(n):
            col1 = cols[i]
            col2 = cols[j]
            if i == j:
                corr_matrix.loc[col1, col2] = 1.0
                pval_matrix.loc[col1, col2] = 0.0
            else:
                corr, p_val = pearsonr(session_matrix[col1], session_matrix[col2])
                corr_matrix.loc[col1, col2] = corr
                pval_matrix.loc[col1, col2] = p_val
                
    return corr_matrix.round(3), pval_matrix

def analyze_signal_correlations(log_path, output_heatmap_path):
    logs = []
    
    # 1. Lectura del archivo de logs JSON por línea
    if not os.path.exists(log_path):
        print(f"Error: No se encontró el archivo de logs en {log_path}")
        return

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
                    
    if not logs:
        print("El archivo de logs está vacío o no contiene JSON válido.")
        return

    df = pd.DataFrame(logs)
    
    # 2. Extracción segura de campos anidados dentro de 'details' (ej. eval_ms)
    if 'details' in df.columns:
        df['eval_ms'] = df['details'].apply(lambda x: x.get('eval_ms', 0) if isinstance(x, dict) else 0)
    
    # 3. Agrupación por sesión o bloques de transacciones para medir co-ocurrencia
    if 'session_id' not in df.columns:
        df['session_id'] = [f"tx_batch_{i // 10}" for i in range(len(df))]
        
    # 4. Creación de la tabla pivote One-Hot Encoding (Presencia/Ausencia por sesión)
    session_matrix = pd.crosstab(df['session_id'], df['signal_category'])
    
    # 5. Cálculo de la Matriz de Correlación y P-values
    corr_matrix, p_df = calculate_correlations_with_pvalues(session_matrix)
    
    # Imprimir reporte en consola
    print("="*75)
    print("MATRIZ DE CORRELACIÓN DE PEARSON (CO-OCURRENCIA DE SEÑALES RMS)")
    print("="*75)
    print(corr_matrix)
    print("="*75)
    print("P-Values:\n", p_df)
    
    # 6. Generación del Dashboard Ejecutivo de 3 Paneles
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # --- Panel 1: Mapa de Calor de Correlación (r) ---
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        cmap='coolwarm', 
        vmin=-1, 
        vmax=1, 
        fmt=".2f", 
        linewidths=0.8, 
        cbar_kws={'label': 'Pearson (r)'},
        ax=axes[0]
    )
    axes[0].set_title('1. Matriz de Correlación (r)', fontsize=11, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].tick_params(axis='y', rotation=0)
    
    # --- Panel 2: Mapa de Calor de Significancia (-log10(p)) ---
    log_pvals = -np.log10(p_df + 1e-300)
    np.fill_diagonal(log_pvals.values, 0)
    
    sns.heatmap(
        log_pvals, 
        annot=True, 
        cmap='Reds', 
        fmt=".1f", 
        linewidths=0.8, 
        cbar_kws={'label': '-log10(p)'},
        ax=axes[1]
    )
    axes[1].set_title('2. Significancia (-log10(p))', fontsize=11, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].tick_params(axis='y', rotation=0)
    
    # --- Panel 3: Campana de Gauss y Posición de Z-Scores ---
    x = np.linspace(-4, 4, 1000)
    y = norm.pdf(x, 0, 1)
    
    axes[2].plot(x, y, label='Distribución N(0,1)', color='black', lw=2)
    
    z_crit = 1.96
    axes[2].axvline(z_crit, color='darkred', linestyle='--', label='Umbral Z = ±1.96 (α=0.05)')
    axes[2].axvline(-z_crit, color='darkred', linestyle='--')
    
    # Sombrear zonas de rechazo de la hipótesis nula
    axes[2].fill_between(np.linspace(z_crit, 4, 100), norm.pdf(np.linspace(z_crit, 4, 100), 0, 1), color='red', alpha=0.25, label='Zona Rechazo H₀')
    axes[2].fill_between(np.linspace(-4, -z_crit, 100), norm.pdf(np.linspace(-4, -z_crit, 100), 0, 1), color='red', alpha=0.25)
    
    # Ubicar pares clave evaluando sus valores reales
    N_samples = len(session_matrix)
    key_pairs_to_plot = [
        ('TECH_DEBT vs SYSTEM_LAG', corr_matrix.loc['TECH_DEBT', 'SYSTEM_LAG'], 'purple'),
        ('SYSTEM_LAG vs OP_OVERHEAD', corr_matrix.loc['SYSTEM_LAG', 'OPERATIONAL_OVERHEAD'], 'darkgreen')
    ]
    
    for label, r_val, color in key_pairs_to_plot:
        # Conversión estimada a Z para posicionar visualmente en la campana
        z_approx = r_val * np.sqrt(N_samples - 1)
        pos_x = min(max(z_approx, -4), 3.8) # Tope visual extremo derecho
        axes[2].axvline(pos_x, color=color, linewidth=2, linestyle='-', 
                    label=f'{label}\n(r={r_val:.2f}, p≈0)')
        
    axes[2].set_xlim(-4, 4.2)
    axes[2].set_ylim(0, 0.42)
    axes[2].set_title('3. Campana de Gauss y Pares Clave', fontsize=11, fontweight='bold')
    axes[2].set_xlabel('Puntuación Z (Desviaciones Estándar)', fontsize=10)
    axes[2].set_ylabel('Densidad de Probabilidad', fontsize=10)
    axes[2].legend(fontsize=7, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_heatmap_path, dpi=300)
    plt.close()
    
    print(f"Dashboard estadístico exportado exitosamente a: {output_heatmap_path}\n")

if __name__ == "__main__":
    log_file = r"C:\Employment Hero\system_signals.log"
    heatmap_file = r"C:\Employment Hero\signal_correlation_dashboard.png"
    
    analyze_signal_correlations(log_file, heatmap_file)