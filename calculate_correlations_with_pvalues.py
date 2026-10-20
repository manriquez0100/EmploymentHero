from scipy.stats import pearsonr
import pandas as pd
import numpy as np

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

# Ejemplo de uso dentro de tu análisis:
# corr_df, p_df = calculate_correlations_with_pvalues(session_matrix)
# print("P-Values:\n", p_df)