import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
import plotly.graph_objects as go

COLUNAS_FIXA_DESOCUPACAO = [
    '[Setor] Etapa - XX',
    '[Setor] Etapa - XX'
]

COLUNAS_ETAPAS_DESOCUPACAO = [
    '[Setor] Etapa - X1',
    '[Setor] Etapa - X2',
    '[Setor] Etapa - X3',
    '[Setor] Etapa - X5',
    '[Setor] Etapa - X10',
    '[Setor] Etapa - X11',
    '[Setor] Etapa - X12',
    '[Setor] Etapa - X13',
    '[Setor] Etapa - X15', 
    '[Setor] Etapa - X16'
]

MAPA_FASE_CURTA_PARA_DESOCUPACAO = {
    "Etapa X": "[Setor] Etapa - X1",
    "Etapa Y": "[Setor] Etapa - X2",
    "Etapa C": "[Setor] Etapa - X4",
    "Etapa D": "[Setor] Etapa - X5",
    "Etapa E": "[Setor] Etapa - X10",
    "Etapa W": "[Setor] Etapa - X11",
    "Etapa XX": "[Setor] Etapa - X12", 
    "Etapa XY": "[Setor] Etapa - X13", 
    "Etapa F": "[Setor] Etapa - X15",
    "Etapa M": "[Setor] Etapa - X16"
}

fases_desoc = [
    '[Setor] Etapa - X1',
    '[Setor] Etapa - X2',
    '[Setor] Etapa - X3',
    '[Setor] Etapa - X5',
    '[Setor] Etapa - X10',
    '[Setor] Etapa - X11',
    '[Setor] Etapa - X12',
    '[Setor] Etapa - X13',
    '[Setor] Etapa - X15', 
    '[Setor] Etapa - X16'
]

todas_fases = [
    '[Setor] Etapa - X4',
    '[Setor] Etapa - X6',
    '[Setor] Etapa - X7',
    '[Setor] Etapa - X8',
    '[Setor] Etapa - X9',
    '[Setor] Etapa - X14',
    '[Setor] Etapa - X17',
    '[Setor] Etapa - X18',
    '[Setor] Etapa - X19',
    '[Setor] Etapa - X20',
    '[Setor] Etapa - X21',
    '[Setor] Etapa - X22',
    '[Setor] Etapa - X23',
    '[Setor] Etapa - X24',
    '[Setor] Etapa - X25',
    '[Setor] Etapa - X26'
]

mapa_fases_curtas = {
    "Etapa X": "[Setor] Etapa - X1",
    "Etapa Y": "[Setor] Etapa - X2",
    "Etapa C": "[Setor] Etapa - X4",
    "Etapa D": "[Setor] Etapa - X5",
    "Etapa E": "[Setor] Etapa - X10",
    "Etapa W": "[Setor] Etapa - X11",
    "Etapa XX": "[Setor] Etapa - X12", 
    "Etapa XY": "[Setor] Etapa - X13", 
    "Etapa F": "[Setor] Etapa - X15",
    "Etapa M": "[Setor] Etapa - X16"
}

def calcular_tempo_na_fase(row, fase_inicio, fases_desoc, todas_fases):
    if pd.isna(row[fase_inicio]):
        return pd.NaT

    data_inicio = row[fase_inicio]
    datas_validas = []

    for fase in todas_fases:
        if fase in fases_desoc:
            continue
        data = row.get(fase)
        if pd.notna(data) and data > data_inicio:
            datas_validas.append(data)

    if not datas_validas:
        return pd.NaT

    return min(datas_validas) - data_inicio


def formatar_timedelta(td):
    total_segundos = int(td.total_seconds())
    dias = total_segundos // 86400
    horas = (total_segundos % 86400) // 3600
    minutos = (total_segundos % 3600) // 60
    return f'{dias}d {horas}h {minutos}m'

def criar_layout_desocupacao(df: pd.DataFrame):
    df_copia = df.copy()
    desocupacao = df_copia[df_copia['Finalizado'] == True].copy()

    for fase in fases_desoc:
        desocupacao[f'tempo_{fase}'] = desocupacao.apply(
            lambda row: calcular_tempo_na_fase(row, fase, fases_desoc, todas_fases),
            axis=1
        )

    tempo_total_acumulado = pd.Timedelta(0)
    tempos_por_fase_real = {}
    tempos_medios_por_fase = {}

    for fase in fases_desoc:
        tempos_validos = desocupacao[f'tempo_{fase}'].dropna()
        tempo_fase = tempos_validos.sum()
        tempos_por_fase_real[fase] = tempo_fase
        tempo_total_acumulado += tempo_fase
        tempos_medios_por_fase[fase] = tempos_validos.mean() if len(tempos_validos) > 0 else pd.Timedelta(0)

    valores_segundos_fase = pd.Series({k: v.total_seconds() / 86400 for k, v in tempos_por_fase_real.items()})
    valores_dias_tempo_medio = pd.Series({fase: tempos_medios_por_fase[fase].total_seconds() / 86400 for fase in fases_desoc})
    textos_tempo_medio = [formatar_timedelta(tempos_medios_por_fase[fase]) for fase in valores_segundos_fase.index]

    def criar_graficos_tempo():
        fig = go.Figure()
        total_segundos = tempo_total_acumulado.total_seconds()
        tempo_total_formatado = formatar_timedelta(pd.Timedelta(seconds=total_segundos))

        fig.add_trace(go.Pie(
            labels=['Tempo Total Acumulado nas Fases de Desocupação'],
            values=[total_segundos],
            hole=0.6,
            pull=[0.05],
            marker=dict(colors=['#228B22'], line=dict(color='black', width=2)),
            text=[tempo_total_formatado],
            textposition='inside',
            textfont=dict(size=15, color='black', family='Arial', weight='bold'),
            hovertemplate='<br>Tempo total:</br><br>%{text}<extra></extra>',
            hoverlabel=dict(                                                
                font=dict(
                    color='black',
                    size=13,
                    family='Arial'
                ),
                bgcolor='white',
                bordercolor='black'
            ),
            domain=dict(x=[0, 0.45], y=[0, 1])
        ))
 
        cores = ['#006994', '#FFFF99', '#FF8C00', '#C8A2C8', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        fig.add_trace(go.Pie(
            labels=[mapa_fases_curtas[f] for f in valores_segundos_fase.index],
            values=valores_segundos_fase.values,
            hole=0.6,
            pull=[0.05] * len(valores_segundos_fase),
            marker=dict(colors=cores, line=dict(color='black', width=2)),
            textinfo='percent',  # mostra só a porcentagem nas fatias
            textfont=dict(size=15, color='black', family='Arial', weight='bold'),
            text=[formatar_timedelta(v) for v in tempos_por_fase_real.values()],  # define o texto para o hover
            hovertemplate='<b>Fase:</b> %{label}<br><b>Tempo:</b> %{text}<extra></extra>',
            hoverlabel=dict(                    
                font=dict(
                    color='black',
                    size=13,
                    family='Arial'
                ),
                bgcolor='white'
            ),
            domain=dict(x=[0.55, 1], y=[0, 1])
        ))

        fig.update_layout(
            title=dict(
                text='Análise de Tempo nas Fases de Desocupação',
                x=0.5,
                font=dict(color='black', size=16, family='Arial', weight='bold')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig

    def criar_grafico_fases():
        cores = ['#006994', '#FFFF99', '#FF8C00', '#C8A2C8', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        cores = cores * (len(valores_segundos_fase) // len(cores) + 1)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[mapa_fases_curtas[f] for f in valores_dias_tempo_medio.index],
            y=valores_dias_tempo_medio.values,
            marker=dict(
                color=cores[:len(valores_dias_tempo_medio)],
                line=dict(color='black', width=2.5)
            ),
            text=textos_tempo_medio,
            textposition='outside',
            textfont=dict(size=14, color='black', family='Arial', weight='bold'),
            hovertemplate='<b>Fase:</b> %{x}<br><b>Tempo médio:</b> %{text}<extra></extra>',
            hoverlabel=dict(
                font=dict(
                    color='black',
                    size=13,
                    family='Arial'
                ),
                bgcolor='white',
                bordercolor='black'
            )
        ))
        
        fig.update_layout(
            title=dict(
                text='Tempo de Permanência de Cada Fase em Desocupação',
                x=0.5,
                font=dict(color='black', size=16, family='Arial', weight='bold')
            ),
            xaxis=dict(tickangle=20),
            yaxis=dict(title='Tempo Médio (Dias)', gridcolor='rgba(0,0,0,0.15)'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=60, t=90, b=140)
        )
        return fig

    layout = html.Div(
        children=[
            dcc.Graph(id="grafico-desocupacao-pizza", figure=criar_graficos_tempo()),
            dcc.Graph(id="grafico-desocupacao-barras", figure=criar_grafico_fases()),

            html.Button(
                "📥",
                id="btn-download-desocupacao",
                style={
                    "position": "fixed",
                    "top": "240px",
                    "right": "14px",
                    "color": "white",
                    "border": "none",
                    "padding": "0",
                    "background": "transparent",
                    "outline": "none",             
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "cursor": "pointer",
                    "borderRadius": "5px",
                    "zIndex": "1000"
                }
            ),
            dcc.Download(id="download-desocupacao"),

            dash_table.DataTable(
                id="tabela-desocupacao",
                columns=[{'name': col, 'id': col} for col in COLUNAS_FIXA_DESOCUPACAO + COLUNAS_ETAPAS_DESOCUPACAO],
                data = [],
                page_size=15,
                fixed_rows={"headers": True},
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial', 
                    'fontSize': '12px',
                    'whiteSpace': 'normal',
                    'minWidth': '220px',
                    'width': '220px',
                    'maxWidth': '220px',
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                },
                css=[
                    {
                        "selector": ".dash-spreadsheet-container .dash-spreadsheet-inner th .dash-cell-value",
                        "rule": """
                            white-space: normal !important;
                            overflow: visible !important;
                            text-overflow: unset !imporatnt;
                            line-height: 1.2;
                        """
                    },
                    {
                        "selector": ".dash-spreadsheet-container .dash-spreadsheet-inner th",
                        "rule": """
                            height: auto !important;
                        """
                    }
                ]
            )
        ]
    )

    return layout