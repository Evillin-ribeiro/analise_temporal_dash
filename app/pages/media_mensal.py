import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
import plotly.graph_objects as go

COLUNAS_TABELA_MEDIA_MENSAL =[
    'Código do imóvel',
    'Contato',
    'Data_inicio_desocupacao',
    'Data_fim_desocupacao',
    'Finalizado'
]

def criar_layout_media_mensal(df: pd.DataFrame):
    df_f = df[df['Finalizado'] == True].copy()
    df_f['Data_fim_desocupacao'] = pd.to_datetime(df_f['Data_fim_desocupacao'])
    df_f['duracao_dias'] = df_f['Tempo_total_dias']
    
    df_f['mes_ano'] = df_f['Data_fim_desocupacao'].dt.to_period('M')
    
    media_mensal = df_f.groupby('mes_ano')['duracao_dias'].mean().reset_index()
    media_mensal.columns = ['Mês/Ano', 'Média de Dias']
    media_mensal['Mês/Ano_str'] = media_mensal['Mês/Ano'].astype(str)
    
    z = np.polyfit(range(len(media_mensal)), media_mensal['Média de Dias'], 1)
    p = np.poly1d(z)
    media_mensal['Tendência'] = p(range(len(media_mensal)))
    
    max_idx = media_mensal['Média de Dias'].idxmax()
    min_idx = media_mensal['Média de Dias'].idxmin()


    def criar_grafico_media():
       
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=media_mensal['Mês/Ano_str'],
            y=media_mensal['Média de Dias'],
            mode='lines+markers',
            name='Média Mensal',
            customdata=media_mensal['Mês/Ano_str'], #inseri na atualização
            line=dict(color='black', width=3),
            marker=dict(size=10, color='darkorange', line=dict(color='white', width=2)),
            hovertemplate='%{x}<br>Média: %{y:.1f} dias<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=media_mensal['Mês/Ano_str'],
            y=media_mensal['Média de Dias'],
            fill='tozeroy',
            mode='none',
            fillcolor='rgba(240,230,140,0.3)',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=media_mensal['Mês/Ano_str'],
            y=media_mensal['Tendência'],
            mode='lines',
            name='Tendência',
            line=dict(color='red', width=2, dash='dash'),
            opacity=0.8,
            hovertemplate='Tendência: %{y:.1f} dias<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=[media_mensal['Mês/Ano_str'][max_idx]],
            y=[media_mensal['Média de Dias'][max_idx]],
            mode='markers+text',
            name='Máximo',
            marker=dict(color='yellow', size=12, symbol='circle'),
            text=[f"Máx: {media_mensal['Média de Dias'][max_idx]:.1f}"],
            textposition='top right',
            hovertemplate='Máximo: %{y:.1f} dias<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=[media_mensal['Mês/Ano_str'][min_idx]],
            y=[media_mensal['Média de Dias'][min_idx]],
            mode='markers+text',
            name='Mínimo',
            marker=dict(color='lightgreen', size=12, symbol='circle'),
            text=[f"Mín: {media_mensal['Média de Dias'][min_idx]:.1f}"],
            textposition='bottom right',
            hovertemplate='Mínimo: %{y:.1f} dias<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='Evolução da Média Mensal do Tempo de Desocupação',
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
            text=f"Média Geral: {media_mensal['Média de Dias'].mean():.1f} dias | "
                 f"Desvio Padrão: {media_mensal['Média de Dias'].std():.1f} dias",
            showarrow=False,
            font=dict(size=12, family='Arial Black'),
            align='left'
        )

        return fig

    layout = html.Div([
        html.Button(
            "📥",
            id="btn-download-media-mensal",
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
        dcc.Download(id="download-media-mensal"),

        dcc.Graph(
            id='grafico-media-mensal', figure=criar_grafico_media()
        ),

        dash_table.DataTable(
            id='tabela-media-mensall',
            columns=[{'name': col, 'id':col} for col in COLUNAS_TABELA_MEDIA_MENSAL],
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
                }]
            
            )

        ]

    )
            
    return layout, criar_grafico_media


