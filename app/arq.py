import os
import pandas as pd
import numpy as np
import html5lib
from pathlib import Path
from datetime import datetime

def processar_excel(caminho_arquivo: str) -> str:
    caminho_arquivo = Path(caminho_arquivo)

#Abrindo o arquivo
    ext = caminho_arquivo.suffix.replace(".", "").lower()

    if ext == "xlsx":
        df = pd.read_excel(caminho_arquivo, engine="openpyxl")
        print("Arquivo Excel processado com sucesso")

    elif ext == "xls":
        df = pd.concat(pd.read_html(caminho_arquivo))
        print("Arquivo Excel processado com sucesso(pd.read_html)")

    else:
        raise ValueError("Formato de arquivo não suportado")

#Conversão da coluna criado 
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


    df["Criado"] = df["Criado"].apply(converter_criado)

#Colunas da desocupação
    colunas_desocupacao = [
        "[Desocupação] Etapa - Integração",
        "[Desocupação] Etapa - Aviso de Desocupação",
        "[Desocupação] Etapa - Chaves Entregues",
        "[Desocupação] Etapa - Vistoria Agendada",
        "[Desocupação] Etapa - Vistoria Cancelada",
        "[Desocupação] Etapa - Vistoria Sem Agendamento",
        "[Desocupação] Etapa - Vistoria Parcial",
        "[Desocupação] Etapa - Comparativo da Vistoria",
        "[Desocupação] Etapa - Orçamento",
        "[Desocupação] Etapa - Vistoria Com Pendência",
        "[Desocupação] Etapa - Orçamento Aprovado",
        "[Desocupação] Etapa - Análise de Contestação",
        "[Desocupação] Etapa - Reparo Estrutural",
        "[Desocupação] Etapa - Inquilino Irá Executar",
        "[Desocupação] Etapa - Revistoria",
        "[Desocupação] Etapa - Orçamento da Revistoria",
        "[Desocupação] Etapa - Revistoria com Pendência",
        "[Desocupação] Etapa - Roque Serviços",
        "[Desocupação] Etapa - Imóvel Sem Pendências",
        "[Desocupação] Etapa - Fechamento",
        "[Desocupação] Etapa - Envio de Débitos Finais",
        "[Desocupação] Etapa - Pendente Roque Serviços",
        "[Desocupação] Etapa - Finalizado Adimplente",
        "[Desocupação] Etapa - Finalizado Inadimplente",
        "[Desocupação] Etapa - Desistiu da Desocupação",
        "[Desocupação] Etapa - Em Acordo",
    ]

    for col in colunas_desocupacao:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    
    colunas_inicio = [
        '[Desocupação] Etapa - Chaves Entregues',
        '[Desocupação] Etapa - Aviso de Desocupação',
        'Criado'
    ]
    
    df['Data_inicio_desocupacao'] = df[colunas_inicio].bfill(axis=1).iloc[:, 0]
    
    colunas_fim = [
        '[Desocupação] Etapa - Envio de Débitos Finais',
        '[Desocupação] Etapa - Finalizado Adimplente',
        '[Desocupação] Etapa - Finalizado Inadimplente',
        '[Desocupação] Etapa - Em Acordo'
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
            df[['Código do imóvel', 'Contato', 'Criado']],
            df[colunas_desocupacao],
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