# Digital Twin

## Overview

`digitaltwin` is a Python framework for building and analyzing a digital twin of compressor systems.  
It provides end‑to‑end functionality for:

- Ingesting maintenance/intervention data from SAP  
- Preprocessing and cleaning time‑series data  
- Exploratory data analysis & visualization  
- Thermodynamic modeling (equations of state)  
- Compressor efficiency and power calculations  

## Project Structure

- **0_funcoes_base** (`2_modelagem/0_funcoes_base`)  
  Core utilities, e.g.  
  - `read_sap_intervencoes.py` – load and parse SAP intervention files  
- **1_preprocessamento** (`2_modelagem/1_preprocessamento`)  
  Jupyter notebooks for data cleaning & feature engineering  
- **2_exploracao_e_visualizacao** (`2_modelagem/2_exploracao_e_visualizacao`)  
  Notebooks for exploratory analysis and plots  
- **3_Modelo_Temp** (`2_modelagem/3_Modelo_Temp`)  
  Temperature‑behavior modeling, including a linear model example in `1_Modelo_Linear/`  
- **4_calc_eficiencia** (`2_modelagem/4_calc_eficiencia`)  
  Python routines for thermodynamic calculations and efficiency:  
  - [`funcoes_eficiencia.py`](2_modelagem/4_calc_eficiencia/funcoes_eficiencia.py)  

## Requirements

- conda  
- pip (via environment.yml)

Instale e ative o ambiente:

```bash
conda env create -f environment.yml
conda activate compressor_env
```