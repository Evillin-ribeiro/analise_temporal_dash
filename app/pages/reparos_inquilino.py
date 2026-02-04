import pandas as pd
from dash import dcc, html, dash_table
import plotly.graph_objects as go

COLUNAS_TABELA_REPAROS_INQ = [
    '[Setor] Etapa - XX',
    '[Setor] Etapa - XX',
    'Data_inicio_desocupacao',
    '[Setor] Etapa - X18',
    'Data_fim_desocupacao',
    'Finalizado'
]

def criar_layout_reparos_inquilino(df: pd.DataFrame):

    df_f = df[df['Finalizado'] == True].copy()

    df_f['Data_inicio_desocupacao'] = pd.to_datetime(df_f['Data_inicio_desocupacao'])
    df_f['duracao_dias'] = df_f['Tempo_total_dias']

    df_f['mes_ano'] = df_f['Data_inicio_desocupacao'].dt.to_period('M')

    df_f['inquilino_fez_por_conta'] = (
        df_f['[Setor] Etapa - X18'].notna()
    )

    df_f['mes_ano_label'] = (
        df_f['Data_inicio_desocupacao']
        .dt.strftime('%b %Y')
        .str.lower()
    )

    meses_disponiveis = sorted(df_f['mes_ano'].astype(str).unique())

    def criar_grafico(df_base: pd.DataFrame, opacidade_total=0.85, opacidade_inquilino=0.85):
        reparos_mensal = (
            df_base
            .groupby('mes_ano', as_index=False)
            .agg(
                **{
                    'Inquilino Fez por Conta': ('inquilino_fez_por_conta', 'sum'),
                    'Total Finalizados': ('Finalizado', 'sum')
                }
            )
            .sort_values('mes_ano')
        )

        reparos_mensal['Percentual'] = (
            reparos_mensal['Inquilino Fez por Conta'] /
            reparos_mensal['Total Finalizados']
        ).fillna(0) * 100

        reparos_mensal['Mês/Ano'] = (
            reparos_mensal['mes_ano']
            .dt.strftime('%b %Y')
            .str.lower()
        )

        total_finalizados = df_base['Finalizado'].sum()
        total_fechou = df_base['inquilino_fez_por_conta'].sum()
        percentual_geral = (
            (total_fechou / total_finalizados) * 100
            if total_finalizados > 0 else 0
        )

        fig = go.Figure()

        fig.add_bar(
            x=reparos_mensal['Mês/Ano'],
            y=reparos_mensal['Total Finalizados'],
            name='Total de Desocupações',
            opacity=opacidade_total,
            marker=dict(color='#F0E68C', line=dict(color='black', width=1.3)),
            text=reparos_mensal['Total Finalizados'],
            textposition='outside',
            textfont=dict(size=12, color='black'),
            hovertemplate='%{x}, %{y}<extra></extra>'
        )

        fig.add_bar(
            x=reparos_mensal['Mês/Ano'],
            y=reparos_mensal['Inquilino Fez por Conta'],
            name='Inquilino Fez por Conta',
            opacity=opacidade_inquilino,
            marker=dict(color='#4682B4', line=dict(color='black', width=1.3)),
            text=reparos_mensal['Inquilino Fez por Conta'],
            textposition='outside',
            textfont=dict(size=12, color='black'),
            hovertemplate='%{x}, %{y}<extra></extra>'
        )

        fig.add_scatter(
            x=reparos_mensal['Mês/Ano'],
            y=reparos_mensal['Percentual'],
            name='% Fez por Conta',
            mode='lines+markers',
            yaxis='y2',
            line=dict(color='#B22222', width=3),
            marker=dict(size=9, color='#B22222', line=dict(color='white', width=2))            
        )

        fig.update_layout(
            title=dict(
                text='Inquilino Fez por Conta',
                x=0.5,
                font=dict(size=18, family='Arial', color='black')
            ),
            hoverlabel=dict(
                bgcolor='white',
                bordercolor='black',
                font=dict(
                    color='black',
                    size=12
                )
            ),
            barmode='group',
            bargap=0.2,
            bargroupgap=0.08,
            xaxis=dict(title='Mês/Ano', tickangle=-45),
            yaxis=dict(title='Quantidade de Desocupações'),
            yaxis2=dict(
                title='Percentual (%)',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=60, t=80, b=80)
        )

        fig.add_annotation(
            x=1,
            y=1.1,
            xref='paper',
            yref='paper',
            showarrow=False,
            align='left',
            bgcolor='wheat',
            bordercolor='black',
            borderwidth=1,
            text=(
                f"<b>Total de Desocupações:</b> {total_finalizados}<br>"
                f"<b>Fez por Conta:</b> {total_fechou}<br>"
                f"<b>Percentual Geral:</b> {percentual_geral:.1f}%"
            )
        )

        return fig

    layout = html.Div(
        children=[
            dcc.Dropdown(
                id='filtro-reparos-inquilino',
                options=[
                    {'label': 'Todos', 'value': 'ALL'},
                    *[
                        {'label': mes, 'value': mes}
                        for mes in meses_disponiveis
                    ]
                ],
                value=['ALL'],
                multi=True,
                clearable=False,
                style={'width': '420px', 'marginBottom': '15px'}
            ),

            html.Button(
                "📥",
                id="btn-download-reparos-inquilino",
                style={
                    "position": "fixed",
                    "top": "220px",
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

            dcc.Download(id="download-reparos-inquilino"),

            dcc.Graph(
                id='grafico-reparos-inquilino',
                config={'displayModeBar': True, 'displaylogo': False}
            ),

            dash_table.DataTable(
                id='tabela-reparos-inquilino',
                columns=[{'name': col, 'id': col} for col in COLUNAS_TABELA_REPAROS_INQ],
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
                ]
            )
        ]
    )

    return layout, df_f, criar_grafico
