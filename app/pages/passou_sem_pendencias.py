import pandas as pd
from dash import html, dcc, dash_table
import plotly.graph_objects as go

COLUNAS_TABELA_PASSOU_SP = [
    'Código do imóvel',
    'Contato',
    'Criado',
    '[Desocupação] Etapa - Integração',
    '[Desocupação] Etapa - Aviso de Desocupação',
    '[Desocupação] Etapa - Chaves Entregues',
    '[Desocupação] Etapa - Vistoria Agendada',
    '[Desocupação] Etapa - Vistoria Cancelada',
    '[Desocupação] Etapa - Vistoria Sem Agendamento',
    '[Desocupação] Etapa - Vistoria Parcial',
    '[Desocupação] Etapa - Comparativo da Vistoria',
    '[Desocupação] Etapa - Orçamento',
    '[Desocupação] Etapa - Vistoria Com Pendência',
    '[Desocupação] Etapa - Orçamento Aprovado',
    '[Desocupação] Etapa - Análise de Contestação',
    '[Desocupação] Etapa - Reparo Estrutural',
    '[Desocupação] Etapa - Inquilino Irá Executar',
    '[Desocupação] Etapa - Revistoria',
    '[Desocupação] Etapa - Orçamento da Revistoria',
    '[Desocupação] Etapa - Revistoria com Pendência',
    '[Desocupação] Etapa - Roque Serviços',
    '[Desocupação] Etapa - Imóvel Sem Pendências',
    'Finalizado'
]

def processar_dados_passou_sp(df):
    imoveis_com_data = df[df['[Desocupação] Etapa - Imóvel Sem Pendências'].notna()].copy()

    ordem_fases = [
        '[Desocupação] Etapa - Roque Serviços',
        '[Desocupação] Etapa - Revistoria com Pendência',
        '[Desocupação] Etapa - Orçamento da Revistoria',
        '[Desocupação] Etapa - Revistoria',
        '[Desocupação] Etapa - Inquilino Irá Executar',
        '[Desocupação] Etapa - Reparo Estrutural',
        '[Desocupação] Etapa - Análise de Contestação',
        '[Desocupação] Etapa - Orçamento Aprovado',
        '[Desocupação] Etapa - Vistoria Com Pendência',
        '[Desocupação] Etapa - Orçamento',
        '[Desocupação] Etapa - Comparativo da Vistoria',
        '[Desocupação] Etapa - Vistoria Parcial',
        '[Desocupação] Etapa - Vistoria Sem Agendamento',
        '[Desocupação] Etapa - Vistoria Cancelada',
        '[Desocupação] Etapa - Vistoria Agendada',
        '[Desocupação] Etapa - Chaves Entregues',
        '[Desocupação] Etapa - Aviso de Desocupação',
        '[Desocupação] Etapa - Integração',
        'Criado'
    ]

    def validar_fase_na_ordem(linha, ordem_fases):
        for fase in ordem_fases:
            if fase in linha.index and pd.notna(linha[fase]):
                return fase
        return None

    imoveis_com_data['fase_encontrada'] = imoveis_com_data.apply(
        validar_fase_na_ordem,
        axis=1,
        ordem_fases=ordem_fases
    )

    contagem_fases = imoveis_com_data['fase_encontrada'].value_counts().reindex(ordem_fases, fill_value=0)

    return imoveis_com_data, contagem_fases

def atualizar_grafico_passou_sp(contagem_grupo, clickData, selected_groups):
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

def criar_grafico_passou_sem_pendencias(contagem_grupo, total, selected_groups=None):
        cores = ['#228B22', '#DC143C', '#FFD700', '#4169E1', '#FF69B4', '#8B4513', '#00CED1', '#FF4500']
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
                textfont=dict(size=11, color='black'),
                hovertemplate='<b>Fase:</b> %{x}<br><b>Quantidade:</b> %{y}<extra></extra>',
                hoverlabel=dict(
                    font=dict(color='black', size=13, family='Arial'),
                    bgcolor='white',
                    bordercolor='black'
                )
            ))

        fig.update_layout(
            title=dict(
                text='Penúltima fase, antes do imóvel ir para a fase "Imóvel Sem Pendência"',
                x=0.5,
                font=dict(
                    color='black',      
                    size=16,          
                    family='Arial',     
                    weight='bold'      
                )
            ),
            xaxis=dict(tickangle=30, tickfont=dict(size=11), title=''),
            yaxis=dict(title='Quantidade de Imóveis', tickfont=dict(size=11),
                       gridcolor='rgba(0,0,0,0.15)', zeroline=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=60, t=90, b=140)
        )

        fig.add_annotation(
            x=1, y=1, xref='paper', yref='paper',
            text=f'<b>Total de Imóveis Analisados:</b> {total}',
            showarrow=False, align='right',
            font=dict(size=12, color='black'),
            bgcolor='wheat',
            bordercolor='black', borderwidth=1
        )

        return fig

def criar_layout_passou_sp(df):
    imoveis_com_data, contagem_grupo = processar_dados_passou_sp(df)
    total = len(imoveis_com_data)

    selected_groups = list(contagem_grupo.index)

    layout = html.Div([
        dcc.Store(id="filtro-passou-sp"),

        html.Button(
            "📥",
            id="btn-download-passou-sp",
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

        dcc.Download(id="download-excel-passou-sp"),

        dcc.Graph(
            id='grafico-passou-sem-pendencias',
            figure=criar_grafico_passou_sem_pendencias(
                contagem_grupo, 
                total, 
                selected_groups
            )
        ),

        html.Div(id='tabela-passou-sp', style={'marginTop': '30px'})
    ])

    return layout, criar_grafico_passou_sem_pendencias, imoveis_com_data