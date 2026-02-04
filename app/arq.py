import os
import pandas as pd
import numpy as np
import html5lib
from pathlib import Path
from datetime import datetime

def processar_excel(caminho_arquivo: str) -> str:
    caminho_arquivo = Path(caminho_arquivo)

    ext = caminho_arquivo.suffix.replace(".", "").lower()

    if ext == "xlsx":
        df = pd.read_excel(caminho_arquivo, engine="openpyxl")
        print("Arquivo Excel processado com sucesso")

    elif ext == "xls":
        df = pd.concat(pd.read_html(caminho_arquivo))
        print("Arquivo Excel processado com sucesso(pd.read_html)")

    else:
        raise ValueError("Formato de arquivo não suportado")

    def converter_criado(valor):
        if pd.isna(valor):
            
            return pd.NaT

        if isinstance(valor, (pd.Timestamp, datetime)):
            return valor

        if isinstance(valor, (int, float)):
            return pd.to_datetime(valor, unit="d", origin="1899-12-30")

        valor = (
            str(valor)
            .replace("\xa0", "")
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )

        return pd.to_datetime(valor, errors='coerce', dayfirst=True)


    df["[Setor] Etapa - X1"] = df["[Setor] Etapa - X1"].apply(converter_criado)

    colunas_processo_interno = [
        "[Setor] Etapa - X1",
        "[Setor] Etapa - X2",
        "[Setor] Etapa - X3",
        "[Setor] Etapa - X4",
        "[Setor] Etapa - X5",
        "[Setor] Etapa - X6",
        "[Setor] Etapa - X7",
        "[Setor] Etapa - X8",
        "[Setor] Etapa - X9",
        "[Setor] Etapa - X10",
        "[Setor] Etapa - X11",
        "[Setor] Etapa - X12",
        "[Setor] Etapa - X13",
        "[Setor] Etapa - X14",
        "[Setor] Etapa - X15",
        "[Setor] Etapa - X16",
        "[Setor] Etapa - X17",
        "[Setor] Etapa - X18",
        "[Setor] Etapa - X19",
        "[Setor] Etapa - X20",
        "[Setor] Etapa - X21",
        "[Setor] Etapa - X22",
        "[Setor] Etapa - X23",
        "[Setor] Etapa - X24",
        "[Setor] Etapa - X25",
        "[Setor] Etapa - X26",
    ]

    for col in colunas_processo_interno:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    
    colunas_inicio = [
        '[Setor] Etapa - X1',
        '[Setor] Etapa - X2',
        '[Setor] Etapa - X3'
    ]
    
    df['Data_inicio_desocupacao'] = df[colunas_inicio].bfill(axis=1).iloc[:, 0]
    
    colunas_fim = [
        '[Setor] Etapa - X23',
        '[Setor] Etapa - X24',
        '[Setor] Etapa - X25',
        '[Setor] Etapa - X26'
    ]
    
    df['Data_fim_real'] = df[colunas_fim].bfill(axis=1).iloc[:, 0]
    
    df['Finalizado'] = (
        df['Data_inicio_desocupacao'].notna() &
        df['Data_fim_real'].notna()
    )
    
    df['Data_fim_desocupacao'] = df['Data_fim_real'].fillna(pd.Timestamp.now())
    
    delta = df['Data_fim_desocupacao'] - df['Data_inicio_desocupacao']
    delta = delta.where(delta >= pd.Timedelta(0))

    def timedelta_para_dias(td):
        if pd.isna(td):
            return np.nan
        return td.total_seconds() / 86400
    
    df['Tempo_total_dias'] = delta.apply(timedelta_para_dias)
    
    def dias_decimais_para_texto(valor):
        if pd.isna(valor):
            return ""
    
        dias = int(valor)
        resto = valor - dias
    
        horas_total = resto * 24
        horas = int(horas_total)
    
        minutos_total = (horas_total - horas) * 60
        minutos = int(round(minutos_total))
    
        if minutos == 60:
            minutos = 0
            horas += 1
    
        if horas == 24:
            horas = 0
            dias += 1
    
        return f"{dias:02d} dias {horas:02d} horas e {minutos:02d} minutos"
    
    df['Tempo_total_desocupacao'] = df['Tempo_total_dias'].apply(dias_decimais_para_texto)
    
    def etapa_final_utilizada(row):
        for col in colunas_fim:
            if pd.notna(row[col]):
                return col
        return ""
    
    df['Etapa_final_utilizada'] = df.apply(etapa_final_utilizada, axis=1)
    
    df_final = pd.concat(
        [
            df[['[Setor] Etapa - XX', '[Setor] Etapa - XX', '[Setor] Etapa - XX']],
            df[colunas_processo_interno],
            df[
                [
                    'Data_inicio_desocupacao',
                    'Data_fim_desocupacao',
                    'Tempo_total_desocupacao',
                    'Tempo_total_dias',
                    'Finalizado',
                    'Etapa_final_utilizada'
                ]
            ]
        ],
        axis=1
    )
    caminho_saida = caminho_arquivo.with_name(
        f"processado_{caminho_arquivo.name}"
    )

    df_final.to_excel(caminho_saida, index=False, engine="openpyxl")

    print("Arquivo processado criado em:", caminho_saida)

    return str(caminho_saida)