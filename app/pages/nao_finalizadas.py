import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
from dash.dash_table import DataTable

COLUNAS_TABELA_NAO_FINALIZADAS = [
    '[Setor] Etapa - XX',
    '[Setor] Etapa - XX',
    'Data_inicio_desocupacao',
    'Data_fim_desocupacao',
    'Finalizado'
]

def filtrar_dataframe_nao_finalizadas(df, filtro):
    if filtro == "andamento":
        return df[df['Desocupacoes_em_andamento'] == True], "Desocupações em Andamento"
    elif filtro == "sem_automacao":
        return df[df['Desocupacao_nao_finalizada'] == True], "Desocupações sem automação no sistema XX"
    else:
        return df.copy(), "Total Desocupações Não Finalizadas"

def criar_grafico_nao_finalizadas(VALORES_NF, LABELS_NF, CORES_NF, PULL_NF, total, filtro):
    labels = LABELS_NF[filtro]
    values = VALORES_NF[filtro]
    colors = CORES_NF[filtro]
    pull = PULL_NF[filtro]

    if filtro == "todos":
        opacity = 1
        customdata = ["andamento", "sem_automacao"]
    elif filtro == "andamento":
        opacity = 0.9
        customdata = ["andamento"]
    else:
        opacity = 0.9
        customdata = ["sem_automacao"]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        customdata=customdata,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='black', width=2)),
        pull=pull,
        textinfo='value+label',
        textfont=dict(size=14, color= 'black', family="Arial Black"),
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
            text="Desocupações Não Finalizadas",
            font=dict(size=20, color='#000000', family="Arial Black"),
            x=0.5
        ),
        showlegend=False
    )

    if filtro == "todos":
        x_annotation = 1.0
        yshift_value = -45
        texto_legenda = (
            f"<b>Total de células analisadas:</b> {total}<br>"
            f"<b>Desocupações em andamento:</b> {VALORES_NF['todos'][0]}<br>"
            f"<b>Desocupações sem automação no sistema XX:</b> {VALORES_NF['todos'][1]}"
        )
    elif filtro == "finalizadas":
        x_annotation = 0.85
        yshift_value = 40
        texto_legenda = f"<b>Desocupações em andamento:</b> {VALORES_NF['andamento'][0]}"
    else:
        x_annotation = 0.85
        yshift_value = 40
        texto_legenda = f"<b>Desocupações Não Finalizadas:</b> {VALORES_NF['sem_automacao'][0]}"

    fig.add_annotation(
        x=x_annotation,
        y=0.01,
        yshift=yshift_value,
        xref='paper',
        yref='paper',
        showarrow=False,
        text=texto_legenda,
        align="left",
        font=dict(size=14, color="black", family="Arial Black"),
        bordercolor="#95a5a6",
        borderwidth=2,
        borderpad=10,
        bgcolor="white"
    )

    return fig


def layout_nao_finalizadas(df):
    nao_finalizados = df[df['Finalizado'] == False].copy()

    cols_paramentro = [
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
        "[Setor] Etapa - X26"
    ]

    def verificar_etapa(row):
        for col in cols_paramentro:
            if pd.notna(row[col]) and row[col] != "":
                return True
        return False

    nao_finalizados['Desocupacoes_em_andamento'] = nao_finalizados.apply(verificar_etapa, axis=1)
    nao_finalizados['Desocupacao_nao_finalizada'] = ~nao_finalizados['Desocupacoes_em_andamento']

    em_andamento = int(nao_finalizados['Desocupacoes_em_andamento'].sum())
    sem_automacao = int(nao_finalizados['Desocupacao_nao_finalizada'].sum())
    total = len(nao_finalizados)

    VALORES_NF = {
        "todos": [em_andamento, sem_automacao],
        "andamento": [em_andamento],
        "sem_automacao": [sem_automacao]
    }

    LABELS_NF = {
        "todos": [
            "Desocupações em Andamento",
            "Desocupações sem Automação no sistema XX"
        ],
        "andamento": ["Desocupações em Andamento"],
        "sem_automacao": ["Desocupações sem Automação no sistema XX"]
    }

    CORES_NF = {
        "todos": ['#2d5016', '#fffacd'],
        "andamento": ['#2d5016'],
        "sem_automacao": ['#fffacd']
    }

    PULL_NF = {
        "todos": [0.05, 0.05],
        "andamento": [0.05],
        "sem_automacao": [0.05]
    }

    layout = html.Div([
        
        dcc.Store(id="filtro"),
        html.Button(
            "📥",
            id="btn-download-nao-finalizado",
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

        dcc.Download(id="download-nao-finalizado"),

        dcc.Dropdown(
            id="filtro-desocupacao-nao-finalizadas",
            value="todos",
            clearable=False,
            options=[
                {"label": "Todos", "value": "todos"},
                {"label": "Desocupações em Andamento", "value": "andamento"},
                {"label": "Desocupações sem Automação no sistema XX", "value": "sem_automacao"},
            ],
            style={"width": "420px", "marginBottom": "20px"}
        ),

        dcc.Graph(
            id="grafico-desocupacao-nao-finalizadas",
            figure=criar_grafico_nao_finalizadas(
                VALORES_NF,
                LABELS_NF,
                CORES_NF,
                PULL_NF,
                total,
                "todos"
            )
        ),

        html.Div(id="lista-imoveis-nao-finalizadas", style={"marginTop": "30px"})
    ])

    return layout, nao_finalizados, em_andamento, sem_automacao, total, VALORES_NF, LABELS_NF, CORES_NF, PULL_NF
