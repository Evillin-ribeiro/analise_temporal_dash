import pandas as pd
import numpy as np
from dash import html, dcc, html, dash_table
import plotly.graph_objects as go

COLUNAS_FIXA_ORCAMENTO = [
    '[Setor] Etapa - XX',
    '[Setor] Etapa - XX'
]

COLUNAS_ETAPAS_ORCAMENTO = [
    '[Setor] Etapa - X10',
    '[Setor] Etapa - X11'
]

MAPA_FASE_CURTA_PARA_ORCAMENTO = {
    "[Setor] Etapa - X10": "Etapa - X10",
    "[Setor] Etapa - X11": "Etapa - X11"
}

fases_orcamento = [
    '[Setor] Etapa - X10': 'Etapa - X10',
    '[Setor] Etapa - X11': 'Etapa - X11'
]

todas_fases = [
    '[Setor] Etapa - X1',
    '[Setor] Etapa - X2',
    '[Setor] Etapa - X3',
    '[Setor] Etapa - X4',
    '[Setor] Etapa - X5',
    '[Setor] Etapa - X6',
    '[Setor] Etapa - X7',
    '[Setor] Etapa - X8',
    '[Setor] Etapa - X9',
    '[Setor] Etapa - X12',
    '[Setor] Etapa - X13',
    '[Setor] Etapa - X14',
    '[Setor] Etapa - X15', 
    '[Setor] Etapa - X16'
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
    '[Setor] Etapa - X10',
    '[Setor] Etapa - X11'
}

def calcular_tempo_na_fase(row, fase_inicio, fases_orcamento, todas_fases):
    if pd.isna(row[fase_inicio]):
        return pd.NaT

    data_inicio = row[fase_inicio]
    datas_validas = []

    for fase in todas_fases:
        if fase in fases_orcamento:
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

def criar_layout_orcamento(df: pd.DataFrame):
    df_orcamento = df[df['Finalizado'] == True].copy()

    for fase in fases_orcamento:
        df_orcamento[f'tempo_{fase}'] = df_orcamento.apply(
            lambda row: calcular_tempo_na_fase(row, fase, fases_orcamento, todas_fases),
            axis=1
        )

    tempo_total_acumulado = pd.Timedelta(0)
    tempos_por_fase_real = {}
    tempos_medios_por_fase = {}

    for fase in fases_orcamento:
        tempos_validos = df_orcamento[f'tempo_{fase}'].dropna()
        tempo_fase = tempos_validos.sum()
        tempos_por_fase_real[fase] = tempo_fase
        tempo_total_acumulado += tempo_fase
        tempos_medios_por_fase[fase] = tempos_validos.mean() if len(tempos_validos) > 0 else pd.Timedelta(0)

    valores_segundos_fase = pd.Series({k: v.total_seconds() / 86400 for k, v in tempos_por_fase_real.items()})
    valores_dias_tempo_medio = pd.Series({fase: tempos_medios_por_fase[fase].total_seconds() / 86400 for fase in fases_orcamento})
    textos_tempo_medio = [formatar_timedelta(tempos_medios_por_fase[fase]) for fase in valores_segundos_fase.index]

    def criar_grafico_pizza():
        fig = go.Figure()
        total_segundos = tempo_total_acumulado.total_seconds()
        tempo_total_formatado = formatar_timedelta(pd.Timedelta(seconds=total_segundos))

        fig.add_trace(go.Pie(
            labels=['Tempo Total Acumulado nas Fases de Orçamento'],
            values=[total_segundos],
            hole=0.6,
            pull=[0.05],
            marker=dict(colors=['#228B22'], line=dict(color='black', width=2)),
            text=[tempo_total_formatado],
            textposition='inside',
            textfont=dict(size=15, color='black', family='Arial', weight='bold'),
            hovertemplate='<b>Tempo total:</b><br>%{text}<extra></extra>', 
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

        cores = ['#006994', '#FFFF99']
        fig.add_trace(go.Pie(
            labels=[mapa_fases_curtas[f] for f in valores_segundos_fase.index],
            values=valores_segundos_fase.values,
            hole=0.6,
            pull=[0.05] * len(valores_segundos_fase),
            marker=dict(colors=cores, line=dict(color='black', width=2)),
            texttemplate='%{percent:.1%}',  #mostra só a porcentagem nas fatias
            textfont=dict(size=15, color='black', family='Arial', weight='bold'),
            text=[formatar_timedelta(v) for v in tempos_por_fase_real.values()],  
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
                text='Análise de Tempo nas Fases de Orçamento',
                x=0.5,
                font=dict(color='black', size=16, family='Arial', weight='bold')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig

    def criar_grafico_barras():
        cores = ['#006994', '#FFFF99'] * (len(valores_segundos_fase) // 2 + 1)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[mapa_fases_curtas[f] for f in valores_dias_tempo_medio.index],
            y=valores_dias_tempo_medio.values,
            marker=dict(color=cores[:len(valores_dias_tempo_medio)], line=dict(color='black', width=2.5)),
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
                text='Tempo Médio de Permanência por Fase',
                x=0.5,
                font=dict(color='black', size=16, family='Arial', weight='bold')
            ),
            yaxis=dict(title='Tempo Médio (Dias)', gridcolor='rgba(0,0,0,0.15)'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=60, t=90, b=140)
        )
        return fig
        
    layout = html.Div(
        children=[
            dcc.Graph(id='grafico-orcamento-pizza', figure=criar_grafico_pizza()),
            dcc.Graph(id='grafico-orcamento-barras', figure=criar_grafico_barras()),

            html.Button(
                "📥",
                id="btn-download-orcamento",
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
            dcc.Download(id="download-orcamento"),

            dash_table.DataTable(
                id="tabela-orcamento",
                columns=[{'name': col, 'id': col} for col in COLUNAS_FIXA_ORCAMENTO + COLUNAS_ETAPAS_ORCAMENTO],
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
                    'midth': '220px',
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
                            text-overflow: unset !important;
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
