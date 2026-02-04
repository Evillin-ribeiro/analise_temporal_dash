import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, dash_table

COLUNAS_TABELA_LIBERACAO = [
    '[Setor] Etapa - XX'
    '[Setor] Etapa - XX'
    'Data_inicio_desocupacao',
    '[Setor] Etapa - X10',
    'Data_fim_desocupacao',
    'Tempo_total_desocupacao',
    'Finalizado'
]

def processar_dados_liberacao(df):

    antes_vistoria = [
        '[Setor] Etapa - XX',
        '[Setor] Etapa - X1',
        '[Setor] Etapa - X2',
        '[Setor] Etapa - X3'
    ]

    depois_vistoria = [
        '[Setor] Etapa - X4',
        '[Setor] Etapa - X5',
        '[Setor] Etapa - X6',
        '[Setor] Etapa - X7',
        '[Setor] Etapa - X8',
        '[Setor] Etapa - X9'
    ]

    ordem_fases = [
        '[Setor] Etapa - X10',
        '[Setor] Etapa - X11',
        '[Setor] Etapa - X12',
        '[Setor] Etapa - X13',
        '[Setor] Etapa - X14',
        '[Setor] Etapa - X15',
        '[Setor] Etapa - X16',
        '[Setor] Etapa - X17',
        '[Setor] Etapa - X18',
        '[Setor] Etapa - X19',
        '[Setor] Etapa - X20',
        '[Setor] Etapa - X21',
        '[Setor] Etapa - X22',
        '[Setor] Etapa - X23',
        '[Setor] Etapa - X24',
        '[Setor] Etapa - X25',
        '[Setor] Etapa - X26',
        '[Setor] Etapa - X27',
        '[Setor] Etapa - XX'
    ]

    df_filtrado = df[
        df['[Setor] Etapa - X10'].notna()
    ].copy()

    def encontrar_fase_mais_avancada(linha):
        for fase in ordem_fases:
            if fase in linha and pd.notna(linha[fase]):
                return fase
        return None

    def classificar_vistoria(fase):
        if fase in antes_vistoria:
            return 'Antes da Vistoria'
        elif fase in depois_vistoria:
            return 'Após Vistoria e Antes do Envio do Laudo'
        else:
            return 'Outras Fases'

    df_filtrado['fase_encontrada'] = df_filtrado.apply(
        encontrar_fase_mais_avancada,
        axis=1
    )

    df_filtrado['grupo_vistoria'] = df_filtrado['fase_encontrada'].apply(classificar_vistoria)

    contagem_grupo = df_filtrado['grupo_vistoria'].value_counts()

    return df_filtrado, contagem_grupo 

def atualizar_grupos_selecionados(contagem_grupo, clickData, selected_groups):
    todos_grupos = list(contagem_grupo.index)

    if selected_groups is None:
        selected_groups = todos_grupos

    if clickData:
        grupo_clicado = clickData["points"][0]["x"]

        if selected_groups == [grupo_clicado]:
            selected_groups = todos_grupos
        else:
            selected_groups = [grupo_clicado]

    return selected_groups   

def criar_grafico_liberacao_vistoria(contagem_grupo, total, selected_groups=None):
    
    cores = ['#4169E1', '#2E8B57', '#FF8C00']
    cores = cores * (len(contagem_grupo) // len(cores) + 1)

    if selected_groups is None or set(selected_groups) == set(contagem_grupo.index):
        selected_groups = list(contagem_grupo.index)

    fig = go.Figure()

    for i, grupo in enumerate(contagem_grupo.index):
        opacidade = 1.0 if grupo in selected_groups else 0.4
        fig.add_trace(go.Bar(
            x=[grupo],
            y=[contagem_grupo[grupo]],
            marker=dict(
                color=cores[i],
                line=dict(color='black', width=1.5)
            ),
            opacity=opacidade,
            text=[contagem_grupo[grupo]],
            textposition='outside',
            textfont=dict(size=12, color='black'),
            hovertemplate='<b>Grupo:</b> %{x}<br><b>Quantidade:</b> %{y}<extra></extra>',
            hoverlabel=dict(
                font=dict(color='black', size=13, family='Arial'),
                bgcolor='white',
                bordercolor='black'
            )
        ))

    fig.update_layout(
        title=dict(
            text='Análise de Imóveis com Vistorias Liberadas pelo Proprietário',
            x=0.5,
            font=dict(color='black', size=16, family='Arial', weight='bold')
        ),
        yaxis=dict(
            title='Quantidade de Imóveis',
            gridcolor='rgba(0,0,0,0.15)',
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=60, t=90, b=80)
    )

    fig.add_annotation(
        x=1,
        y=1,
        xref='paper',
        yref='paper',
        text=f'<b>Total de Imóveis Analisados:</b> {total}',
        showarrow=False,
        align='right',
        bgcolor='wheat',
        bordercolor='black',
        borderwidth=1
    )

    return fig

def criar_layout_liberacao_vistoria(df): 

    df_filtrado, contagem_grupo = processar_dados_liberacao(df)
    total = len(df_filtrado) 

    selected_groups = list(contagem_grupo.index)

    layout = html.Div([
        dcc.Store(id="filtro-liberacao"),

        html.Button(
            "📥",
            id="btn-download-liberacao",
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

        dcc.Download(id="download-excel-liberacao"),
        
        dcc.Graph(
            id="grafico-liberacao",
            figure=criar_grafico_liberacao_vistoria(
                contagem_grupo, 
                total,
                selected_groups
            )
        ),
                
        html.Div(id='tabela-liberacao', style={'marginTop': '30px'})
    ])

    return layout, criar_grafico_liberacao_vistoria, df_filtrado

