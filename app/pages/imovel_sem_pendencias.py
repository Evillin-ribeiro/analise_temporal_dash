import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
from dash.dash_table import DataTable

COLUNAS_TABELA_SEM_PENDENCIAS = [
    'Código do imóvel',
    'Contato',
    'Data_inicio_desocupacao',
    '[Desocupação] Etapa - Imóvel Sem Pendências',
    'Data_fim_desocupacao',
    'Finalizado'
]

def filtrar_dataframe_sem_pendencias(df, filtro):
    coluna_fase = '[Desocupação] Etapa - Imóvel Sem Pendências'

    if filtro == "passaram_sem_pendencia":
        df_filtrado = df[df[coluna_fase].notna()]
        return df_filtrado, "Imóveis que passaram por essa fase"

    elif filtro == "nao_passou_fase":
        df_filtrado = df[df[coluna_fase].isna()]
        return df_filtrado, "Imóveis que não passaram por essa fase"

    else:
        return df.copy(), "Todas as Desocupações"

def criar_grafico_sem_pendencias(VALORES_SP, LABELS_SP, CORES_SP, PULL_SP, total_sp, qtd_com_data, qtd_sem_data, filtro):
    labels = LABELS_SP[filtro]
    values = VALORES_SP[filtro]
    colors = CORES_SP[filtro]
    pull = PULL_SP[filtro]

    if filtro == "todos":
        opacity = 1
        customdata = ["passaram_sem_pendencia", "nao_passou_fase"]
        texto_legenda = (
            f"<b>Total de imóveis analisados:</b> {total_sp}<br>"
            f"<b>Imóveis que passaram por essa fase:</b> {qtd_com_data}<br>"
            f"<b>Imóveis que não passaram por essa fase:</b> {qtd_sem_data}"
        )

    elif filtro == "passaram_sem_pendencia":
        opacity = 0.9
        customdata = ["passaram_sem_pendencia"]
        texto_legenda = (
            f"<b>Imóveis que passaram por essa fase:</b> {qtd_com_data}"
        )

    else:  
        opacity = 0.9
        customdata = ["nao_passou_fase"]
        texto_legenda = (
            f"<b>Imóveis que não passaram por essa fase:</b> {qtd_sem_data}"
        )

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        customdata=customdata,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='black', width=2)),
        pull=pull,
        textinfo='value+label',
        textfont=dict(size=14, color='black', family="Arial Black"),
        hoverinfo='label+value+percent',
        domain=dict(x=[0, 0.65], y=[0, 1]),
        opacity=opacity
    ))

    fig.update_layout(
        width=1150,
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor='white',
            bordercolor='black',
            font=dict(color='black', size=12)
        ),
            title=dict(
            text='Fase "Imóvel Sem Pendência"',
            font=dict(size=17, color='#000000', family='Arial Black'),
            x=0.5
        ),
        showlegend=False,
    )

    fig.add_annotation(
        x=0.99,
        y=0.20,
        xref='paper',
        yref='paper',
        xanchor="right",
        yanchor="bottom",
        xshift=25,
        showarrow=False,
        text=texto_legenda,
        align="left",
        font=dict(size=12, color="#000000", family="Arial Black"),
        bordercolor="#95a5a6",
        borderwidth=2,
        borderpad=15,
        bgcolor="white"
    )

    return fig

def criar_layout_imovel_sem_pendencias(df):
    imoveis_com_data = df[df['[Desocupação] Etapa - Imóvel Sem Pendências'].notna()]
    imoveis_sem_data = df[df['[Desocupação] Etapa - Imóvel Sem Pendências'].isna()]

    qtd_com_data = len(imoveis_com_data)
    qtd_sem_data = len(imoveis_sem_data)
    total_sp = len(df)

    VALORES_SP = {
        "todos": [qtd_com_data, qtd_sem_data],
        "passaram_sem_pendencia": [qtd_com_data],
        "nao_passou_fase": [qtd_sem_data]
    }
    LABELS_SP = {
        "todos": [
            "Imóveis que passaram por essa fase",
            "Imóveis que não passaram por essa fase"
        ],
        "passaram_sem_pendencia": ["Imóveis que passaram por essa fase"],
        "nao_passou_fase": ["Imóveis que não passaram por essa fase"]
    }

    CORES_SP = {
        "todos": ['#228B22', '#DC143C'],
        "passaram_sem_pendencia": ['#228B22'],
        "nao_passou_fase": ['#DC143C']
    }

    PULL_SP = {
        "todos": [0.05, 0.05],
        "passaram_sem_pendencia": [0.05],
        "nao_passou_fase": [0.05]
    }    

    layout = html.Div([
        dcc.Store(id="filtro-sem-pendencia"),
        html.Button(
            "📥",
            id="btn-download-sem-pendencia",
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

        dcc.Download(id="download-excel-sem-pendencia"),
        
        dcc.Dropdown(
            id="filtro-imovel-sem-pendencia",
            value="todos",
            clearable=False,
            options=[
                {"label": "Todos", "value": "todos"},
                {"label": "Imóveis que passaram por essa fase", "value": "passaram_sem_pendencia"},
                {"label": "Imóveis que não passaram por essa fase", "value": "nao_passou_fase"},
            ],
            style={"width": "420px", "marginBottom": "20px"}
        ),
        
        dcc.Graph(
            id="grafico-imovel-sem-pendencia", 
            figure=criar_grafico_sem_pendencias(
                VALORES_SP, 
                LABELS_SP, 
                CORES_SP, 
                PULL_SP, 
                total_sp,
                qtd_com_data,
                qtd_sem_data,
                "todos"
            )
        ),
        html.Div(id="lista-imoveis-sem-pendencia", style={"marginTop": "30px"})
    ])              

    return layout, VALORES_SP, LABELS_SP, CORES_SP, PULL_SP, total_sp, qtd_com_data, qtd_sem_data
