from dash import html, dcc, dash_table
import plotly.graph_objects as go

COLUNAS_TABELA = [
    'Código do imóvel',
    'Contato',
    'Data_inicio_desocupacao',
    'Data_fim_desocupacao',
    'Tempo_total_desocupacao',
    'Finalizado'
]

def filtrar_dataframe(df, filtro):
    if filtro == "finalizadas":
        return df[df['Finalizado'] == True], "Desocupações Finalizadas"
    elif filtro == "nao_finalizadas":
        return df[df['Finalizado'] == False], "Desocupações Não Finalizadas"
    else:
        return df.copy(), "Todas as Desocupações"

def criar_grafico(VALORES, LABELS, CORES, PULL, total_analisadas, filtro):
    labels = LABELS[filtro]
    values = VALORES[filtro]
    colors = CORES[filtro]
    pull = PULL[filtro]

    if filtro == "todos":
        opacity = 1
        customdata = ["finalizadas", "nao_finalizadas"]
    elif filtro == "finalizadas":
        opacity = 0.9
        customdata = ["finalizadas"]
    else:
        opacity = 0.9
        customdata = ["nao_finalizadas"]

    fig = go.Figure(
        go.Pie(
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
        )
    )

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
            text="Volume Total de Desocupações Cadastradas no NIA",
            font=dict(size=20, color='#000000', family="Arial Black"),
            x=0.5
        ),
        showlegend=False
    )

    if filtro == "todos":
        texto_legenda = (
            f"<b>Total de células analisadas:</b> {total_analisadas}<br>"
            f"<b>Desocupações Finalizadas:</b> {VALORES['todos'][0]}<br>"
            f"<b>Desocupações Não Finalizadas:</b> {VALORES['todos'][1]}"
        )
    elif filtro == "finalizadas":
        texto_legenda = f"<b>Desocupações Finalizadas:</b> {VALORES['finalizadas'][0]}"
    else:
        texto_legenda = f"<b>Desocupações Não Finalizadas:</b> {VALORES['nao_finalizadas'][0]}"

    fig.add_annotation(
        x=0.99,
        y=0.09,
        yshift=35,
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

def layout_volume_total(df):

    df_porcetagem = df['Finalizado'].value_counts()
    total_analisadas = len(df)

    VALORES = {
        "todos": [df_porcetagem.get(True, 0), df_porcetagem.get(False, 0)],
        "finalizadas": [df_porcetagem.get(True, 0)],
        "nao_finalizadas": [df_porcetagem.get(False, 0)]
    }

    LABELS = {
        "todos": ['Desocupações Finalizadas', 'Desocupações Não Finalizadas'],
        "finalizadas": ['Desocupações Finalizadas'],
        "nao_finalizadas": ['Desocupações Não Finalizadas']
    }

    CORES = {
        "todos": ['#2d5016', '#fffacd'],
        "finalizadas": ['#2d5016'],
        "nao_finalizadas": ['#fffacd']
    }

    PULL = {
        "todos": [0.05, 0.05],
        "finalizadas": [0.05],
        "nao_finalizadas": [0.05]
    }

    layout = html.Div(
        [
            html.Div(
                [
                    html.Button(
                        "📥",
                        id="btn-download",
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
                    dcc.Download(id="download-excel"),

                    dcc.Dropdown(
                        id="filtro-desocupacao",
                        options=[
                            {"label": "Todos", "value": "todos"},
                            {"label": "Desocupações Finalizadas", "value": "finalizadas"},
                            {"label": "Desocupações Não Finalizadas", "value": "nao_finalizadas"}
                        ],
                        value="todos",
                        clearable=False,
                        style={
                            "width": "420px",
                            "marginBottom": "20px"
                        }
                    ),

                    dcc.Graph(
                        id="grafico-totaldesocupacao",
                        figure=criar_grafico(
                            VALORES,
                            LABELS,
                            CORES,
                            PULL,
                            total_analisadas,
                            "todos"
                        )
                    ),

                    html.Div(
                        id="lista-imoveis",
                        style={"marginTop": "30px"}
                    )
                ]
            )
        ]
    )

    return layout, VALORES, LABELS, CORES, PULL, total_analisadas
