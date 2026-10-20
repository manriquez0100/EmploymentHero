import json
import os
import pandas as pd
import matplotlib.pyplot as plt

def analyze_telemetry_signals(log_path, output_chart_path, max_logs=None):
    logs = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line.strip()))
                # Parametrización: Detener lectura si se alcanza el límite máximo especificado
                if max_logs is not None and len(logs) >= max_logs:
                    break
                
    df = pd.DataFrame(logs)
    
    # 1. Definir pesos de severidad para el Weighted Incident Score
    severity_weights = {'ERROR': 10, 'WARN': 3, 'INFO': 1}
    df['risk_weight'] = df['severity'].map(severity_weights).fillna(1)
    
    # 2. Análisis por categoría: Conteo y Score Ponderado
    signal_counts = df['signal_category'].value_counts()
    severity_breakdown = pd.crosstab(df['signal_category'], df['severity'])
    
    # Calcular el Risk Score total por categoría
    risk_scores = df.groupby('signal_category')['risk_weight'].sum()
    
    # Ordenar las categorías de mayor a menor basándose en el Risk Score (Criticidad real)
    sorted_categories = risk_scores.sort_values(ascending=False).index.tolist()
    
    # Friendly labels for chart and table
    label_map = {
        "SYSTEM_LAG": "System Lag (Search & Bulk Actions)",
        "OPERATIONAL_OVERHEAD": "Operational Overhead (+30% Tickets)",
        "TECH_DEBT": "Tech Debt (Hardcoded Custom Workflows)",
        "FEATURE_PRESSURE": "Feature Pressure (CV & Scheduling)",
        "LOW_ADOPTION": "Low Adoption (Feedback Feature)"
    }
    
    friendly_labels = [label_map.get(cat, cat) for cat in sorted_categories]
    scores = [risk_scores[cat] for cat in sorted_categories]
    counts = [signal_counts[cat] for cat in sorted_categories]
    
    # Print quantitative summary table with Risk Score
    print("="*85)
    print("TELEMETRY SIGNAL QUANTITATIVE & WEIGHTED RISK ANALYSIS REPORT")
    print("="*85)
    print(f"{'Signal Category':<42} | {'Count':<6} | {'Share':<7} | {'ERROR':<5} | {'WARN':<5} | {'INFO':<5} | {'Risk Score':<10}")
    print("-" * 85)
    
    total_logs = len(df)
    total_pct = 0.0
    total_errors = 0
    total_warns = 0
    total_infos = 0
    total_risk_score = 0
    
    for cat in sorted_categories:
        count = signal_counts[cat]
        pct = (count / total_logs) * 100
        total_pct += pct
        
        err = severity_breakdown.loc[cat, 'ERROR'] if 'ERROR' in severity_breakdown.columns and cat in severity_breakdown.index else 0
        warn = severity_breakdown.loc[cat, 'WARN'] if 'WARN' in severity_breakdown.columns and cat in severity_breakdown.index else 0
        info = severity_breakdown.loc[cat, 'INFO'] if 'INFO' in severity_breakdown.columns and cat in severity_breakdown.index else 0
        score = risk_scores[cat]
        
        total_errors += err
        total_warns += warn
        total_infos += info
        total_risk_score += score
        
        print(f"{label_map.get(cat, cat):<42} | {count:<6} | {pct:>5.1f}% | {err:<5} | {warn:<5} | {info:<5} | {score:<10}")
        
    # Fila de Totales
    print("-" * 85)
    print(f"{'TOTAL':<42} | {total_logs:<6} | {total_pct:>5.1f}% | {total_errors:<5} | {total_warns:<5} | {total_infos:<5} | {total_risk_score:<10}")
    print("="*85)
    print(f"Total Telemetry Logs Processed: {total_logs}\n")
    
    # Generate Matplotlib Chart based on Weighted Risk Score
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(11, 6))
    
    colors = ['#d9534f', '#f0ad4e', '#5bc0de', '#0275d8', '#5cb85c']
    bars = ax.barh(friendly_labels[::-1], scores[::-1], color=colors, edgecolor='black', alpha=0.85)
    
    # Add value labels to bars (Showing Weighted Risk Score)
    for bar, count in zip(bars, counts[::-1]):
        width = bar.get_width()
        ax.text(width + 5, bar.get_y() + bar.get_height()/2, f'Score: {int(width)} (n={count})',
                va='center', ha='left', fontsize=10, fontweight='bold', color='#333333')
        
    ax.set_title('Employment Hero RMS - Weighted Incident Risk Analysis (Impact-Driven Ranking)', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Weighted Incident Risk Score (ERROR=10, WARN=3, INFO=1)', fontsize=11, labelpad=10)
    ax.set_xlim(0, max(scores) * 1.25)
    
    plt.tight_layout()
    plt.savefig(output_chart_path, dpi=300)
    plt.close()
    
    print(f"Weighted analysis chart successfully exported to: {output_chart_path}")

if __name__ == "__main__":
    log_file = r"C:\Employment Hero\system_signals.log"
    chart_file = r"C:\Employment Hero\signal_analysis_chart.png"
    
    # Ejemplo procesando todos los logs (max_logs=None) o limitando la muestra
    analyze_telemetry_signals(log_file, chart_file, max_logs=None)