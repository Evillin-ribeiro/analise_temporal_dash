import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
import plotly.graph_objects as go

COLUNAS_FIXA_VISTORIA = [
    'Código do imóvel',
    'Contato'
]

COLUNAS_ETAPAS_VISTORIA = [
    '[Desocupação] Etapa - Vistoria Agendada',
    '[Desocupação] Etapa - Vistoria Sem Agendamento',
    '[Desocupação] Etapa - Vistoria Parcial',
    '[Desocupação] Etapa - Revistoria'    
]

MAPA_FASE_CURTA_PARA_COLUNA = {
    "Vistoria Agendada": "[Desocupação] Etapa - Vistoria Agendada",
    "Vistoria Sem Agendamento": "[Desocupação] Etapa - Vistoria Sem Agendamento",
    "Vistoria Parcial": "[Desocupação] Etapa - Vistoria Parcial",
    "Revistoria": "[Desocupação] Etapa - Revistoria"
}

FASES_VISTORIA = [
    "[Desocupação] Etapa - Vistoria Agendada",
    "[Desocupação] Etapa - Vistoria Sem Agendamento",
    "[Desocupação] Etapa - Vistoria Parcial",
    "[Desocupação] Etapa - Revistoria",
]

TODAS_FASES = [
    "[Desocupação] Etapa - Integração",
    "[Desocupação] Etapa - Aviso de Desocupação",
    "[Desocupação] Etapa - Chaves Entregues",
    "[Desocupação] Etapa - Vistoria Cancelada",
    "[Desocupação] Etapa - Comparativo da Vistoria",
    "[Desocupação] Etapa - Orçamento",
    "[Desocupação] Etapa - Vistoria Com Pendência",
    "[Desocupação] Etapa - Orçamento Aprovado",
    "[Desocupação] Etapa - Análise de Contestação",
    "[Desocupação] Etapa - Reparo Estrutural",
    "[Desocupação] Etapa - Inquilino Irá Executar",
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

MAPA_FASES_CURTAS = {
    "[Desocupação] Etapa - Vistoria Agendada": "Vistoria Agendada",
    "[Desocupação] Etapa - Vistoria Sem Agendamento": "Vistoria Sem Agendamento",
    "[Desocupação] Etapa - Vistoria Parcial": "Vistoria Parcial",
    "[Desocupação] Etapa - Revistoria": "Revistoria",
}

def calcular_tempo_na_fase(row, fase_inicio):
    if pd.isna(row[fase_inicio]):
        return pd.NaT

    data_inicio = row[fase_inicio]
    datas_validas = []

    for fase in TODAS_FASES:
        if fase in FASES_VISTORIA:
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
    return f"{dias}d {horas}h {minutos}m"

def criar_graficos_tempo(tempos_por_fase_real, tempo_total_acumulado):
    fig = go.Figure()

    total_segundos = tempo_total_acumulado.total_seconds()
    tempo_total_formatado = formatar_timedelta(
        pd.Timedelta(seconds=total_segundos)
    )

    # Pizza total
    fig.add_trace(go.Pie(
        labels=["Tempo Total Acumulado nas Fases de Vistoria"],
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

    cores = ["#006994", "#FFFF99", "#FF8C00", "#C8A2C8"]

    fig.add_trace(go.Pie(
        labels=[MAPA_FASES_CURTAS[f] for f in tempos_por_fase_real.keys()],
        values=[v.total_seconds() / 86400 for v in tempos_por_fase_real.values()],
        hole=0.6,
        pull=[0.05] * len(tempos_por_fase_real),
        marker=dict(colors=cores, line=dict(color="black", width=2)),
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
            text="Análise de Tempo nas Fases de Vistoria",
            x=0.5,
            font=dict(
                color='black',      
                size=16,          
                family='Arial',     
                weight='bold'      
            )
        ),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    return fig

def criar_grafico_fases(tempos_medios_por_fase):
    valores = [
        tempos_medios_por_fase[f].total_seconds() / 86400
        for f in FASES_VISTORIA
    ]

    textos = [
        formatar_timedelta(tempos_medios_por_fase[f])
        for f in FASES_VISTORIA
    ]

    cores = ["#006994", "#FFFF99", "#FF8C00", "#C8A2C8"]

    fig = go.Figure()

    fig.add_bar(
        x=[MAPA_FASES_CURTAS[f] for f in FASES_VISTORIA],
        y=valores,
        marker=dict(color=cores, line=dict(color="black", width=2.5)),
        text=textos,
        textposition='outside',
        textfont=dict(size=14, color='black', family='Arial', weight='bold'),
        hovertemplate=(
            '<b>Fase:</b> %{x}<br>'
            '<b>Tempo médio:</b> %{text}<extra></extra>'
        ),
        hoverlabel=dict(
            font=dict(
                color='black',
                size=13,
                family='Arial'
            ),
            bgcolor='white',
            bordercolor='black'
        )
    )


    fig.update_layout(
        title=dict(
            text="Tempo de Permanência de Cada Fase em Vistoria",
            x=0.5,
            font=dict(
                color='black',      
                size=16,            
                family='Arial',    
                weight='bold'       
            )
        ),
        yaxis=dict(title="Tempo Médio (Dias)"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=60, t=90, b=140)
    )

    return fig

def criar_layout_vistoria(df):
    vistoria = df[df["Finalizado"] == 1].copy()

    for fase in FASES_VISTORIA:
        vistoria[f"tempo_{fase}"] = vistoria.apply(
            lambda row: calcular_tempo_na_fase(row, fase),
            axis=1
        )

    tempos_por_fase_real = {}
    tempos_medios_por_fase = {}
    tempo_total_acumulado = pd.Timedelta(0)

    for fase in FASES_VISTORIA:
        tempos_validos = vistoria[f"tempo_{fase}"].dropna()

        tempo_total = tempos_validos.sum()
        tempos_por_fase_real[fase] = tempo_total
        tempo_total_acumulado += tempo_total

        tempos_medios_por_fase[fase] = (
            tempos_validos.mean()
            if len(tempos_validos) > 0
            else pd.Timedelta(0)
        )

    layout = html.Div(
        children=[
            dcc.Graph(
                id="grafico-rosca-vistoria",
                figure=criar_graficos_tempo(
                    tempos_por_fase_real,
                    tempo_total_acumulado
                )
            ),
            dcc.Graph(
                id="grafico-barras-vistoria",
                figure=criar_grafico_fases(tempos_medios_por_fase)
            ),

            html.Button(
                "📥",
                id="btn-download-vistoria",
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
            dcc.Download(id="download-vistoria"),

            dash_table.DataTable(
                id="tabela-vistoria",
                columns=[{'name': col, 'id': col} for col in COLUNAS_FIXA_VISTORIA + COLUNAS_ETAPAS_VISTORIA],
                data=[],
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
                    'maxWidth': '200px',
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                },
                css=[
                    {
                        "selector": ".dash-spreadsheet-container .dash-spreadsheet th .dash-cell-value",
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