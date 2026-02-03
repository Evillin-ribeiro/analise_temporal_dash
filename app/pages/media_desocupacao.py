import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
import plotly.graph_objects as go

COLUNAS_TABELA_MEDIA_DESOCUPACAO = [
    'Código do imóvel', 
    'Contato',
    'Data_inicio_desocupacao',
    'Data_fim_desocupacao',
    'Tempo_total_desocupacao',
    'Finalizado'
]

def criar_layout_media_desocupacao(df: pd.DataFrame):
    df_copia = df.copy()
    desocupacao = df_copia[df_copia['Finalizado'] == True].copy()
    
    fases_desocupacao = [
        '[Desocupação] Etapa - Aviso de Desocupação',
        '[Desocupação] Etapa - Chaves Entregues',
        '[Desocupação] Etapa - Comparativo da Vistoria',
        '[Desocupação] Etapa - Vistoria Com Pendência',
        '[Desocupação] Etapa - Análise de Contestação',
        '[Desocupação] Etapa - Reparo Estrutural',
        '[Desocupação] Etapa - Inquilino Irá Executar',
        '[Desocupação] Etapa - Revistoria com Pendência',
        '[Desocupação] Etapa - Imóvel Sem Pendências',
        '[Desocupação] Etapa - Fechamento',
    ]
    
    todas_fases = [
        '[Desocupação] Etapa - Integração',
        '[Desocupação] Etapa - Vistoria Sem Agendamento',
        '[Desocupação] Etapa - Vistoria Cancelada',
        '[Desocupação] Etapa - Vistoria Parcial',
        '[Desocupação] Etapa - Orçamento',
        '[Desocupação] Etapa - Orçamento Aprovado',
        '[Desocupação] Etapa - Revistoria',
        '[Desocupação] Etapa - Orçamento da Revistoria',
        '[Desocupação] Etapa - Roque Serviços',
        '[Desocupação] Etapa - Pendente Roque Serviços',
        '[Desocupação] Etapa - Envio de Débitos Finais',
        '[Desocupação] Etapa - Finalizado Adimplente',
        '[Desocupação] Etapa - Finalizado Inadimplente',
        '[Desocupação] Etapa - Desistiu da Desocupação',
        '[Desocupação] Etapa - Em Acordo'
    ]

    mapa_fases_curtas = {
        '[Desocupação] Etapa - Aviso de Desocupação': 'Aviso de Desocupação',
        '[Desocupação] Etapa - Chaves Entregues': 'Chaves Entregues',
        '[Desocupação] Etapa - Comparativo da Vistoria': 'Comparativo da Vistoria',
        '[Desocupação] Etapa - Vistoria Com Pendência': 'Vistoria com Pendência',
        '[Desocupação] Etapa - Análise de Contestação': 'Análise de Contestação',
        '[Desocupação] Etapa - Reparo Estrutural': 'Reparo Estrutural',
        '[Desocupação] Etapa - Inquilino Irá Executar': 'Inquilino Irá Executar',
        '[Desocupação] Etapa - Revistoria com Pendência': 'Revistoria com Pendência',
        '[Desocupação] Etapa - Imóvel Sem Pendências': 'Imóvel Sem Pendências',
        '[Desocupação] Etapa - Fechamento': 'Fechamento'
    }

    def calcular_tempo_na_fase(row, fase_inicio, fases_desocupacao, todas_fases):
        if pd.isna(row.get(fase_inicio)):
            return pd.NaT
    
        data_inicio = row[fase_inicio]
        datas_validas = []
    
        for fase in todas_fases:
            data = row.get(fase)
            if pd.notna(data) and data > data_inicio:
                datas_validas.append(data)
    
        if not datas_validas:
            return pd.NaT
    
        return min(datas_validas) - data_inicio

    for fase in fases_desocupacao:
        desocupacao[f'tempo_{fase}'] = desocupacao.apply(
            lambda row: calcular_tempo_na_fase(
                row,
                fase,
                fases_desocupacao,
                todas_fases
            ),
            axis=1
        )
    
    desocupacao['Data_fim_desocupacao'] = pd.to_datetime(
        desocupacao['Data_fim_desocupacao']
    )
    
    colunas_tempo = [f'tempo_{fase}' for fase in fases_desocupacao]
    
    df_tempo = desocupacao[colunas_tempo + ['Data_fim_desocupacao']].copy()
    
    df_tempo['tempo_total_fases_desocupacao'] = df_tempo[colunas_tempo].apply(
        lambda row: row.sum(min_count=1),
        axis=1
    )
    
    df_tempo['tempo_total_dias'] = (
        df_tempo['tempo_total_fases_desocupacao']
        .dt.total_seconds() / 86400
    )
    
    df_tempo['mes'] = df_tempo['Data_fim_desocupacao'].dt.to_period('M')
    
    media_mensal_fases_desocupacao = (
        df_tempo
        .groupby('mes', as_index=False)
        .agg(tempo_medio_dias=('tempo_total_dias', 'mean'))
    )
    
    media_mensal_fases_desocupacao['Mês/Ano_str'] = (
        media_mensal_fases_desocupacao['mes'].astype(str)
    )
    
    X = np.arange(len(media_mensal_fases_desocupacao))
    y = media_mensal_fases_desocupacao['tempo_medio_dias'].values
    z = np.polyfit(X, y, 1)
    tendencia = np.poly1d(z)
    
    media_mensal_fases_desocupacao['Tendência'] = tendencia(X)
    max_idx = media_mensal_fases_desocupacao['tempo_medio_dias'].idxmax()
    min_idx = media_mensal_fases_desocupacao['tempo_medio_dias'].idxmin()

    def criar_grafico_media_desocupacao():
        fig = go.Figure()
    
        fig.add_trace(go.Scatter(
            x=media_mensal_fases_desocupacao['Mês/Ano_str'],
            y=media_mensal_fases_desocupacao['tempo_medio_dias'],
            mode='lines+markers',
            name='Média Mensal',
            customdata=media_mensal_fases_desocupacao['Mês/Ano_str'],
            line=dict(color='black', width=3),
            marker=dict(size=10, color='darkorange', line=dict(color='white', width=2)),
            hovertemplate='%{x}<br>Média: %{y:.1f} dias<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=media_mensal_fases_desocupacao['Mês/Ano_str'],
            y=media_mensal_fases_desocupacao['tempo_medio_dias'],
            fill='tozeroy',
            mode='none',
            fillcolor='rgba(240,230,140,0.3)',
            showlegend=False
        ))
    
        fig.add_trace(go.Scatter(
            x=media_mensal_fases_desocupacao['Mês/Ano_str'],
            y=media_mensal_fases_desocupacao['Tendência'],
            mode='lines',
            name='Tendência',
            line=dict(color='red', width=2, dash='dash'),
            opacity=0.8,
            hovertemplate='Tendência: %{y:.1f} dias<extra></extra>'
        ))
    
        fig.add_trace(go.Scatter(
            x=[media_mensal_fases_desocupacao['Mês/Ano_str'][max_idx]],
            y=[media_mensal_fases_desocupacao['tempo_medio_dias'][max_idx]],
            mode='markers+text',
            name='Máximo',
            marker=dict(color='yellow', size=12),
            text=[f"Máx: {media_mensal_fases_desocupacao['tempo_medio_dias'][max_idx]:.1f}"],
            textposition='top right',
            hovertemplate='Máximo: %{y:.1f} dias<extra></extra>'
        ))
    
        fig.add_trace(go.Scatter(
            x=[media_mensal_fases_desocupacao['Mês/Ano_str'][min_idx]],
            y=[media_mensal_fases_desocupacao['tempo_medio_dias'][min_idx]],
            mode='markers+text',
            name='Mínimo',
            marker=dict(color='lightgreen', size=12),
            text=[f"Mín: {media_mensal_fases_desocupacao['tempo_medio_dias'][min_idx]:.1f}"],
            textposition='bottom right',
            hovertemplate='Mínimo: %{y:.1f} dias<extra></extra>'
        ))
    
        fig.update_layout(
            title=dict(
                text='Média Mensal de Tempo com Etapas Exclusivas da Desocupação',
                x=0.5,
                font=dict(size=18, family='Arial Black')
            ),
            xaxis_title='Mês/Ano',
            yaxis_title='Média de Dias',
            template='plotly_white',
            width=1150,
            height=600,
            hovermode='closest',
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    x=1.17,
                    y=1.09,
                    xanchor="right",
                    yanchor="top",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Voltar para todos",
                            method="relayout",
                            args=[{"reset_tabela": True}]
                        )
                    ]
                )
            ]
        )
        
        fig.add_annotation(
            x=0, y=1.05, xref='paper', yref='paper',
            text=f"Média Geral: {media_mensal_fases_desocupacao['tempo_medio_dias'].mean():.1f} dias | "
                 f"Desvio Padrão: {media_mensal_fases_desocupacao['tempo_medio_dias'].std():.1f} dias",
            showarrow=False,
            font=dict(size=12, family='Arial Black'),
            align='left'
        )
        
        return fig

    layout = html.Div([
        html.Button(
            "📥",
            id="btn-download-media-desocupacao",
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
        
        dcc.Download(id="download-media-desocupacao"),
                
        dcc.Graph(
            id='grafico-media-desocupacao'
        ),

        dash_table.DataTable(
            id='tabela-media-desocupacao',
            columns=[{'name': col, 'id': col} for col in COLUNAS_TABELA_MEDIA_DESOCUPACAO],
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
            ])
        ]
    )
    
    return layout, criar_grafico_media_desocupacao
