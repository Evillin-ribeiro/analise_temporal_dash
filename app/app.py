import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, Input, Output, callback_context, no_update
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
import pandas as pd
from flask import Flask, request, redirect, render_template, session
from werkzeug.utils import secure_filename
from flask_session import Session
from processar_arquivo import processar_excel_upload
import os
import uuid
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user,
    current_user,
    login_required
)

server = Flask(__name__)
server.secret_key = os.getenv("FLASK_SECRET_KEY")

server.config["SESSION_TYPE"] = "filesystem"
server.config["SESSION_PERMANENT"] = False
server.config["SESSION_USE_SIGNER"] = True
server.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session")
Session(server)

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    routes_pathname_prefix="/dash/"
)

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"

USUARIOS = {
    os.getenv("USER_ADMIN"): {"senha": os.getenv("PASS_ADMIN")},
}

class Usuario(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in USUARIOS:
        return Usuario(user_id)
    return None
 
@server.route("/")
def index():
    return redirect("/login")

@server.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("username")
        senha = request.form.get("password")

        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            login_user(Usuario(usuario), remember=False)
            return redirect("/dash/")

        return render_template("login.html", error="Usuário ou senha inválidos")

    return render_template("login.html")

@server.route("/logout")
@login_required
def logout():
    caminho = session.pop("arquivo_excel", None)
    if caminho and os.path.exists(caminho):
        os.remove(caminho)

    logout_user()
    return redirect("/login")

@server.before_request
def proteger_rotas():

    if request.path.startswith(("/_dash", "/assets", "/static")):
        return

    if request.path in ("/login", "/logout", "/upload", "/"):
        return

    if not current_user.is_authenticated:
        return redirect("/login")
 
    if request.path.startswith("/dash"):
        if "arquivo_excel" not in session:
            return redirect("/upload")

@server.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
server.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
server.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

@server.errorhandler(RequestEntityTooLarge)
def arquivo_muito_grande(e):
    return render_template(
        "upload.html",
        erro="Arquivo muito grande. O limite é de 10MB."
    ), 413


def obter_df_sessao():
    caminho = session.get("arquivo_excel")
    if not caminho or not os.path.exists(caminho):
        return None
    return pd.read_excel(caminho, engine="openpyxl")

def arquivo_permitido(nome):
    return "." in nome and nome.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@server.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":

        arquivo = request.files.get("arquivo")

        if not arquivo or arquivo.filename == "":
            return render_template("upload.html", erro="Selecione um arquivo")

        if not arquivo.filename.lower().endswith((".xlsx", ".xls")):
            return render_template("upload.html", erro="Formato inválido")

        nome = secure_filename(arquivo.filename)
        nome_unico = f"{uuid.uuid4()}_{nome}"
        caminho = os.path.join(server.config["UPLOAD_FOLDER"], nome_unico)

        arquivo.save(caminho)

        try:
            caminho_processado = processar_excel_upload(caminho)
        
            session["arquivo_excel"] = caminho_processado
            session.modified = True
        
            return redirect("/dash/")

        except Exception as e:
            return render_template(
                "upload.html",
                erro=f"Erro ao processar o arquivo. Verifique o formato e tente novamente: {str(e)}"
            )

        session["arquivo_excel"] = caminho
        session.modified = True  

        return redirect("/")

    return render_template("upload.html")

from pages.volume_total import layout_volume_total, filtrar_dataframe, criar_grafico, COLUNAS_TABELA
from pages.nao_finalizadas import layout_nao_finalizadas, criar_grafico_nao_finalizadas, filtrar_dataframe_nao_finalizadas, COLUNAS_TABELA_NAO_FINALIZADAS
from pages.media_mensal import criar_layout_media_mensal, COLUNAS_TABELA_MEDIA_MENSAL
from pages.reparos_imobiliaria import criar_layout_reparos_imobiliaria, COLUNAS_TABELA_REPAROS_IMOB
from pages.reparos_inquilino import criar_layout_reparos_inquilino, COLUNAS_TABELA_REPAROS_INQ
from pages.vistoria import criar_layout_vistoria, COLUNAS_FIXA_VISTORIA, COLUNAS_ETAPAS_VISTORIA, MAPA_FASE_CURTA_PARA_COLUNA
from pages.media_vistoria import criar_layout_media_vistoria, COLUNAS_TABELA_MEDIA_VISTORIA
from pages.orcamento import criar_layout_orcamento, COLUNAS_FIXA_ORCAMENTO, COLUNAS_ETAPAS_ORCAMENTO, MAPA_FASE_CURTA_PARA_ORCAMENTO
from pages.media_orcamento import criar_layout_media_orcamento, COLUNAS_TABELA_MEDIA_ORCAMENTO
from pages.desocupacao import criar_layout_desocupacao, COLUNAS_FIXA_DESOCUPACAO, COLUNAS_ETAPAS_DESOCUPACAO, MAPA_FASE_CURTA_PARA_DESOCUPACAO
from pages.media_desocupacao import criar_layout_media_desocupacao, COLUNAS_TABELA_MEDIA_DESOCUPACAO
from pages.imovel_sem_pendencias import criar_layout_imovel_sem_pendencias, criar_grafico_sem_pendencias, filtrar_dataframe_sem_pendencias, COLUNAS_TABELA_SEM_PENDENCIAS
from pages.passou_sem_pendencias import criar_layout_passou_sp, criar_grafico_passou_sem_pendencias, processar_dados_passou_sp, atualizar_grafico_passou_sp, COLUNAS_TABELA_PASSOU_SP
from pages.liberacao_vistoria import criar_layout_liberacao_vistoria, criar_grafico_liberacao_vistoria, processar_dados_liberacao, atualizar_grupos_selecionados, COLUNAS_TABELA_LIBERACAO

def carregar_df():
    caminho = session.get("arquivo_excel")
    if not caminho:
        return pd.DataFrame()
    return pd.read_excel(caminho)

paginas = {
    "Total de desocupações no NIA": None,
    "Desocupações não finalizadas": None,
    "Média mensal de desocupações": None,
    "Inquilino fez reparos com a imobiliária": None,
    "Inquilino fez reparos por conta": None,
    "Análise de imóveis na fase vistoria": None,
    "Média mensal da fase de vistoria": None,
    "Análise de imóveis na fase em orçamento": None,
    "Média mensal da fase de orçamento": None,
    "Análise de imóveis na fase em desocupação": None,
    "Média mensal da fase de desocupação": None,
    "Total de imóveis na fase sem pendências": None,
    "Análise da fase imóvel sem pendência": None,
    "Imóveis liberados da vistoria": None,
}

app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, Arial, sans-serif",
        "backgroundColor": "#F4F6F8",
        "minHeight": "100vh",
        "padding": "10px 20px"
    },
    children=[
        dcc.Location(id="url"),

        html.Div(
            style={
                "padding": "15px 10px",
                "marginBottom": "10px",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center"
            },
            children=[

                html.Div(
                    children=[
                        html.H2(
                            "Dashboard – Desocupações Sistema XX",
                            style={"margin": "0", "color": "#2C3E50"}
                        ),
                        html.Span(
                            "Análises operacionais e temporais do processo de desocupação",
                            style={"fontSize": "13px", "color": "#555"}
                        )
                    ]
                ),

                html.A(
                    "Sair",
                    href="/logout",
                    style={
                        "backgroundColor": "#EAF0F6",
                        "color": "#2C3E50",
                        "border": "1px solid #D5DBE0",
                        "borderRadius": "6px",
                        "padding": "6px 14px",
                        "fontSize": "13px",
                        "fontWeight": "600",
                        "cursor": "pointer",
                        "textDecoration": "none"
                    }
                )
            ]
        ),
        dcc.Tabs(
            id="tabs-menu",
            value=list(paginas.keys())[0],
            style={
                "backgroundColor": "#FFFFFF",
                "borderRadius": "8px",
                "padding": "5px"
            },
            children=[
                dcc.Tab(
                    label=nome,
                    value=nome,
                    style={
                        "fontWeight": "600",
                        "fontSize": "13px",
                        "padding": "10px",
                        "color": "#555",
                        "borderRadius": "6px"
                    },
                    selected_style={
                        "fontWeight": "700",
                        "fontSize": "13px",
                        "padding": "10px",
                        "color": "#2C3E50",
                        "backgroundColor": "#EAF0F6",
                        "borderRadius": "6px"
                    }
                )
                for nome in paginas.keys()
            ]
        ),

        html.Div(id="tabs-content")
    ]
)

@app.callback(
    Output("url", "pathname"),
    Input("btn-logout", "n_clicks"),
    prevent_initial_call=True
)
def logout_dash(n_clicks):
    if n_clicks:
        return "/logout"
    raise PreventUpdate

@app.callback(
    Output("tabs-content", "children"),
    Input("tabs-menu", "value")
)
def renderizar_pagina(tab):
    df = obter_df_sessao()

    if df is None:
        return html.Div(
            "Nenhum arquivo carregado. Faça o upload novamente.",
            style={
                "color": "#C0392B",
                "fontWeight": "600",
                "padding": "20px"
            }
        )

    if tab == "Total de desocupações no NIA":
        layout, *_ = layout_volume_total(df)
        return layout

    if tab == "Desocupações não finalizadas":
        layout, *_ = layout_nao_finalizadas(df)
        return layout

    if tab == "Média mensal de desocupações":
        layout, _ = criar_layout_media_mensal(df)
        return layout
 
    if tab == "Inquilino fez reparos com a imobiliária":
        layout, *_ = criar_layout_reparos_imobiliaria(df)
        return layout

    if tab == "Inquilino fez reparos por conta":
        layout, *_ = criar_layout_reparos_inquilino(df)
        return layout

    if tab == "Análise de imóveis na fase vistoria":
        layout = criar_layout_vistoria(df)
        return layout

    if tab == "Média mensal da fase de vistoria":
        layout, _ = criar_layout_media_vistoria(df)
        return layout

    if tab == "Análise de imóveis na fase em orçamento":
        layout = criar_layout_orcamento(df)
        return layout

    if tab == "Média mensal da fase de orçamento":
        layout, _ = criar_layout_media_orcamento(df)
        return layout

    if tab == "Análise de imóveis na fase em desocupação":
        layout = criar_layout_desocupacao(df)
        return layout

    if tab == "Média mensal da fase de desocupação":
        layout, _ = criar_layout_media_desocupacao(df)
        return layout

    if tab == "Total de imóveis na fase sem pendências":
        layout, *_ = criar_layout_imovel_sem_pendencias(df)
        return layout

    if tab == "Análise da fase imóvel sem pendência":
        layout, *_ = criar_layout_passou_sp(df)
        return layout

    if tab == "Imóveis liberados da vistoria":
        layout, *_ = criar_layout_liberacao_vistoria(df)
        return layout

    return html.Div("Página não encontrada")

@app.callback(
    Output("grafico-totaldesocupacao", "figure"),
    Output("lista-imoveis", "children"),
    Output("filtro-desocupacao", "value"),
    Input("grafico-totaldesocupacao", "clickData"),
    Input("filtro-desocupacao", "value")
)
def atualizar_dashboard_total(clickData, filtro_dropdown):

    df = obter_df_sessao()
    if df is None:
        return dash.no_update, dash.no_update, dash.no_update

    layout, VALORES, LABELS, CORES, PULL, total_analisadas = layout_volume_total(df)

    filtro_final = filtro_dropdown or "todos"
    trigger = ctx.triggered_id

    if trigger == "grafico-totaldesocupacao" and clickData:
        filtro_final = clickData["points"][0]["customdata"]

    fig = criar_grafico(
        VALORES,
        LABELS,
        CORES,
        PULL,
        total_analisadas,
        filtro_final
    )

    df_filtrado, titulo = filtrar_dataframe(df, filtro_final)

    tabela = DataTable(
        columns=[{"name": c, "id": c} for c in COLUNAS_TABELA],
        data=df_filtrado[COLUNAS_TABELA].to_dict("records"),
        page_size=15,
        fixed_rows={"headers": True},
        style_table={
            "overflowX": "auto",
            "minWidth": "100%",
        },
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontFamily": "Arial",
            "fontSize": "12px",
            "whiteSpace": "normal",
            "minWidth": "220px",
            "width": "220px",
            "maxWidth": "220px",
        },
        style_header={
            "backgroundColor": "#2c3e50",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
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
        ],
        style_data_conditional=[
            {
                "if": {"filter_query": "{Finalizado} = True"},
                "backgroundColor": "#e8f5e9"
            },
            {
                "if": {"filter_query": "{Finalizado} = False"},
                "backgroundColor": "#fffde7"
            }
        ]
    )

    return fig, html.Div(
        [
            html.H4(
                titulo,
                style={
                    "fontFamily": "Arial Black",
                    "fontSize": "15px",
                    "color": "black",
                    "marginBottom": "15px",
                    "marginTop": "10px"
                }
            ),
            tabela
        ]
    ), filtro_final
    
@app.callback(
    Output("download-excel", "data"),
    Input("btn-download", "n_clicks"),
    State("filtro-desocupacao", "value"),
    prevent_initial_call=True
)
def baixar_excel_total(n_clicks, filtro_ativo):

    df = obter_df_sessao()
    df_filtrado, _ = filtrar_dataframe(df, filtro_ativo)

    return dcc.send_data_frame(
        df_filtrado[COLUNAS_TABELA].to_excel,
        f"desocupacoes_{filtro_ativo}.xlsx",
        index=False
    )

@app.callback(
    Output("grafico-desocupacao-nao-finalizadas", "figure"),
    Output("lista-imoveis-nao-finalizadas", "children"),
    Output("filtro-desocupacao-nao-finalizadas", "value"),  
    Input("grafico-desocupacao-nao-finalizadas", "clickData"),
    Input("filtro-desocupacao-nao-finalizadas", "value")
)
def atualizar_dashboard_nao_finalizadas(clickData, filtro_dropdown):

    df = obter_df_sessao()
    if df is None:
        return dash.no_update, dash.no_update, dash.no_update

    layout,  nao_finalizados, em_andamento, sem_automacao, total, VALORES_NF, LABELS_NF, CORES_NF, PULL_NF = layout_nao_finalizadas(df)

    filtro_final = filtro_dropdown or "todos"
    trigger = ctx.triggered_id

    if trigger == "grafico-desocupacao-nao-finalizadas" and clickData:
        filtro_final = clickData["points"][0]["customdata"]

    fig = criar_grafico_nao_finalizadas(
        VALORES_NF,
        LABELS_NF,
        CORES_NF,
        PULL_NF,
        total,
        filtro_final
    )

    df_filtrado, titulo = filtrar_dataframe_nao_finalizadas(nao_finalizados, filtro_final)

    tabela = DataTable(
        columns=[{"name": c, "id": c} for c in COLUNAS_TABELA_NAO_FINALIZADAS],
        data=df_filtrado[COLUNAS_TABELA_NAO_FINALIZADAS].to_dict("records"),
        page_size=15,
        fixed_rows={"headers": True},
        style_table={
            "overflowX": "auto",
            "minWidth": "100%",
        },
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontFamily": "Arial",
            "fontSize": "13px",
            "whiteSpace": "normal",
            "minWidth": "220px",
            "width": "220px",
            "maxWidth": "220px",
        },
        style_header={
            "backgroundColor": "#2c3e50",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
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
    return fig, html.Div(
        [
            html.H4(
                titulo,
                style={
                    "fontFamily": "Arial Black",
                    "fontSize": "15px",
                    "color": "black",
                    "marginBottom": "15px",
                    "marginTop": "10px"
                }
            ),
            tabela
        ]
    ), filtro_final  
    
@app.callback(
    Output("download-nao-finalizado", "data"),
    Input("btn-download-nao-finalizado", "n_clicks"),
    State("filtro-desocupacao-nao-finalizadas", "value"),
    prevent_initial_call=True
)
def baixar_excel_nao_finalizado(n_clicks, filtro):
    df = obter_df_sessao()
    if df is None:
        return dash.no_update

    nao_finalizados = df[df['Finalizado'] == False].copy()

    df_filtrado, _ = filtrar_dataframe_nao_finalizadas(nao_finalizados, filtro)

    df_filtrado = df_filtrado[COLUNAS_TABELA_NAO_FINALIZADAS]

    return dcc.send_data_frame(
        df_filtrado.to_excel,
        filename=f"desocupacoes_nao_finalizadas_{filtro}.xlsx",
        index=False
    )
   
@app.callback(
    Output("grafico-media-mensal", "figure"),
    Input("tabs-menu", "value")
)
def atualizar_grafico_media(tab):
    if tab != "Média mensal de desocupações":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    df = df[df['Finalizado'] == True].copy()

    _, criar_grafico_media = criar_layout_media_mensal(df)
    return criar_grafico_media()

@app.callback(
    Output("tabela-media-mensall", "data"),
    Input("tabs-menu", "value"),
    Input("grafico-media-mensal", "clickData"),
    Input("grafico-media-mensal", "relayoutData"),
)
def atualizar_tabela_media(tab, clickData, relayoutData):

    if tab != "Média mensal de desocupações":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    df = df[df['Finalizado'] == True].copy()
    df['Data_fim_desocupacao'] = pd.to_datetime(df['Data_fim_desocupacao'])
    df['mes_ano'] = df['Data_fim_desocupacao'].dt.to_period('M').astype(str)

    if relayoutData and relayoutData.get("reset_tabela"):
        return df[COLUNAS_TABELA_MEDIA_MENSAL].to_dict("records")

    if clickData and 'points' in clickData and clickData['points']:
        point0 = clickData['points'][0]

        if point0.get('curveNumber') == 0:
            mes_selecionado = point0.get('customdata')
            if mes_selecionado:
                df = df[df['mes_ano'] == mes_selecionado]

    return df[COLUNAS_TABELA_MEDIA_MENSAL].to_dict("records")
    
@app.callback(
    Output("download-media-mensal", "data"),
    Input("btn-download-media-mensal", "n_clicks"),
    prevent_initial_call=True
)
def baixar_excel_media_mensal(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    df_f = df[df['Finalizado'] == True].copy()
    df_f = df_f[COLUNAS_TABELA_MEDIA_MENSAL]

    return dcc.send_data_frame(
        df_f.to_excel,
        filename="media_mensal.xlsx",
        index=False
    )
    
@app.callback(
    Output("grafico-reparos-imobiliaria", "figure"),
    Output("tabela-reparos-imobiliaria", "data"),
    Input("filtro-reparos-imobiliaria", "value"),
    Input("grafico-reparos-imobiliaria", "restyleData")
)
def atualizar_grafico_reparos_imobiliaria(meses, restyle_data):
    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update, dash.no_update, dash.no_update
    
    df = pd.read_excel(caminho)
    
    layout, df_base, criar_grafico = criar_layout_reparos_imobiliaria(df)
    
    df_filtrado = (
        df_base
        if "ALL" in meses
        else df_base[df_base["mes_ano"].astype(str).isin(meses)]
    )

    visivel_total = 0.85
    visivel_imobiliaria = 0.85

    if restyle_data:
        props, indices = restyle_data
    
        if 'visible' in props:
            visible_values = props['visible']  # lista
    
            for idx, trace_index in enumerate(indices):
                visible = visible_values[idx]
    
                if trace_index == 0:  # Total
                    visivel_total = 0.2 if visible == 'legendonly' else 0.85
    
                elif trace_index == 1:  # Reparos com a imobiliária
                    visivel_imobiliaria = 0.2 if visible == 'legendonly' else 0.85

    figura = criar_grafico(df_filtrado, opacidade_total=visivel_total, opacidade_imobiliaria=visivel_imobiliaria)

    if visivel_total < 0.85 and visivel_imobiliaria >= 0.85:
        tabela = df_filtrado[df_filtrado['fechou_com_imobiliaria']]
    elif visivel_imobiliaria <0.85 and visivel_total >= 0.85:
        tabela = df_filtrado.copy()
    else:
        tabela = df_filtrado.copy()

    tabela = tabela[COLUNAS_TABELA_REPAROS_IMOB].sort_values('Data_inicio_desocupacao').to_dict('records')

    return figura, tabela
    
@app.callback(
    Output("download-reparos-imobiliaria", "data"),
    Input("btn-download-reparos-imobiliaria", "n_clicks"),
    prevent_initial_call=True
)
def baixar_excel_reparos_imobiliaria(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    df_f = df[df['Finalizado'] == True].copy()

    df_f = df_f[COLUNAS_TABELA_REPAROS_IMOB]

    return dcc.send_data_frame(
        df_f.to_excel,
        filename="reparos_feito_pela_imobiliaria.xlsx",
        index=False
    )

@app.callback(
    Output("grafico-reparos-inquilino", "figure"),
    Output("tabela-reparos-inquilino", "data"),
    Input("filtro-reparos-inquilino", "value"),
    Input("grafico-reparos-inquilino", "restyleData")
)
def atualizar_grafico_reparos_inquilino(meses, restyle_data):
    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update, dash.no_update, dash.no_update

    df = pd.read_excel(caminho)

    layout, df_base, criar_grafico = criar_layout_reparos_inquilino(df)

    df_filtrado = (
        df_base
        if "ALL" in meses
        else df_base[df_base["mes_ano"].astype(str).isin(meses)]
    )

    visivel_total = 0.85
    visivel_inquilino = 0.85

    if restyle_data:
        props, indices = restyle_data
    
        if 'visible' in props:
            visible_values = props['visible']  # lista
    
            for idx, trace_index in enumerate(indices):
                visible = visible_values[idx]
    
                if trace_index == 0:  # Total
                    visivel_total = 0.2 if visible == 'legendonly' else 0.85
    
                elif trace_index == 1:  # Inquilino fez por conta
                    visivel_inquilino = 0.2 if visible == 'legendonly' else 0.85
            
    figura = criar_grafico(df_filtrado, opacidade_total=visivel_total, opacidade_inquilino=visivel_inquilino)

    if visivel_total < 0.85 and visivel_inquilino >= 0.85:
        tabela = df_filtrado[df_filtrado['inquilino_fez_por_conta']]
    elif visivel_inquilino < 0.85 and visivel_total >= 0.85:
        tabela = df_filtrado.copy()
    else:
        tabela = df_filtrado.copy()

    tabela = tabela[COLUNAS_TABELA_REPAROS_INQ].sort_values('Data_inicio_desocupacao').to_dict('records')

    return figura, tabela

@app.callback(
    Output("download-reparos-inquilino", "data"),
    Input("btn-download-reparos-inquilino", "n_clicks"),
    prevent_initial_call=True
)
def baixar_excel_reparos_inquilino(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    df_f = df[df['Finalizado'] == True].copy()

    df_f = df_f[COLUNAS_TABELA_REPAROS_INQ]

    return dcc.send_data_frame(
        df_f.to_excel,
        filename="reparos_feito_pelo_inquilino.xlsx",
        index=False
    )

@app.callback(
    Output("tabela-vistoria", "columns"),
    Output("tabela-vistoria", "data"),
    Input("grafico-rosca-vistoria", "clickData"),
    Input("grafico-barras-vistoria", "clickData")
)
def atualizar_tabela_vistoria(click_rosca, click_barra):

    caminho = session.get("arquivo_excel")
    if not caminho:
        return no_update, no_update

    df = pd.read_excel(caminho)
    vistoria = df[df["Finalizado"] == 1].copy()

    ctx = callback_context
    
    if not ctx.triggered:
        colunas = COLUNAS_FIXA_VISTORIA + COLUNAS_ETAPAS_VISTORIA
        df_tabela = vistoria[colunas]

        return (
            [{'name': c, 'id': c} for c in colunas],
            df_tabela.to_dict("records")
        )

    grafico_disparado = ctx.triggered_id

    if grafico_disparado == "grafico-rosca-vistoria":
        label = click_rosca["points"][0].get("label")

        if label == "Tempo Total Acumulado nas Fases de Vistoria":
            colunas = COLUNAS_FIXA_VISTORIA + COLUNAS_ETAPAS_VISTORIA
        else:
            coluna_fase = MAPA_FASE_CURTA_PARA_COLUNA.get(label)
            if not coluna_fase:
                return no_update, no_update
            colunas = COLUNAS_FIXA_VISTORIA + [coluna_fase]

    elif grafico_disparado == "grafico-barras-vistoria":
        label = click_barra["points"][0]["x"]
        coluna_fase = MAPA_FASE_CURTA_PARA_COLUNA.get(label)
        if not coluna_fase:
            return no_update, no_update
        colunas = COLUNAS_FIXA_VISTORIA + [coluna_fase]

    else:
        return no_update, no_update

    df_tabela = vistoria[colunas]

    return (
        [{'name': c, 'id': c} for c in colunas],
        df_tabela.to_dict("records")
    )

    layout_vistoria, criar_grafico_vistoria_pizza, criar_grafico_vistoria_barras = criar_layout_vistoria(df)

    figura = criar_grafico_vistoria_barras()
    tabela = vistoria[COLUNAS_FIXA_VISTORIA + COLUNAS_ETAPAS_VISTORIA].to_dict("records")

    return figura, tabela

@app.callback(
    Output("download-vistoria", "data"),
    Input("btn-download-vistoria", "n_clicks"),
    prevent_initial_call=True
)
def baixar_execel_vistoria(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    vistoria = df[df['Finalizado'] == True].copy()
    vistoria = vistoria[COLUNAS_FIXA_VISTORIA + COLUNAS_ETAPAS_VISTORIA]

    return dcc.send_data_frame(
        vistoria.to_excel,
        filename="fases-da-vistoria.xlsx",
        index=False
    )

@app.callback(
    Output("grafico-media-vistoria", "figure"),
    Input("tabs-menu", "value")
)
def atualizar_grafico_media_vistoria(tab):
    if tab != "Média mensal da fase de vistoria":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)        
    vistoria = df[df['Finalizado'] == True].copy()
    
    layout, criar_grafico_media_vistoria = criar_layout_media_vistoria(df)
    
    return criar_grafico_media_vistoria()

@app.callback(
    Output("tabela-media-vistoria", "data"),
    Input("tabs-menu", "value"),
    Input("grafico-media-vistoria", "clickData"),
    Input("grafico-media-vistoria", "relayoutData"),
)
def atualizar_tabela_media(tab, clickData, relayoutData):
    if tab != "Média mensal da fase de vistoria":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    df = df[df['Finalizado'] == True].copy()
    df['Data_fim_desocupacao'] = pd.to_datetime(df['Data_fim_desocupacao'])
    df['mes_ano'] = df['Data_fim_desocupacao'].dt.to_period('M').astype(str)

    
    if relayoutData and relayoutData.get("reset_tabela"):
        return df[COLUNAS_TABELA_MEDIA_VISTORIA].to_dict("records")
        
    if clickData and 'points' in clickData and clickData['points']:
        point0 = clickData['points'][0]
        if point0.get('curveNumber') == 0:
            mes_selecionado = point0.get('customdata')
            if mes_selecionado:
                df = df[df['mes_ano'] == mes_selecionado]
    
    return df[COLUNAS_TABELA_MEDIA_VISTORIA].to_dict("records")
    
@app.callback(
    Output("download-media-vistoria", "data"),
    Input("btn-download-media-vistoria", "n_clicks"),
    prevent_initial_call=True
)
def baixar_execel_media_vistoria(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    vistoria = df[df['Finalizado'] == True].copy()
    vistoria = vistoria[COLUNAS_TABELA_MEDIA_VISTORIA]

    return dcc.send_data_frame(
        vistoria.to_excel,
        filename="media-exclusiva-fase-vistoria.xlsx",
        index=False
    )

@app.callback(
    Output("tabela-orcamento", "columns"),
    Output("tabela-orcamento", "data"),
    Input("grafico-orcamento-pizza", "clickData"),
    Input("grafico-orcamento-barras", "clickData")
)
def atualizar_tabela_orcamento(click_rosca, click_barra):
    caminho = session.get("arquivo_excel")
    if not caminho:
        return no_update, no_update

    df = pd.read_excel(caminho)
    orcamento = df[df["Finalizado"] == 1].copy()

    ctx = callback_context

    colunas = COLUNAS_FIXA_ORCAMENTO + COLUNAS_ETAPAS_ORCAMENTO
    df_tabela = orcamento[colunas]

    if not ctx.triggered:
        return (
            [{'name': c, 'id': c} for c in colunas],
            df_tabela.to_dict("records")
        )

    grafico_disparado = ctx.triggered_id

    if grafico_disparado == "grafico-orcamento-pizza":
        if not click_rosca:
            return no_update, no_update

        label = click_rosca["points"][0].get("label")

        if label == "Tempo Total Acumulado nas Fases de Orçamento":
            colunas = COLUNAS_FIXA_ORCAMENTO + COLUNAS_ETAPAS_ORCAMENTO
        else:
            coluna_fase = MAPA_FASE_CURTA_PARA_ORCAMENTO.get(label)
            if not coluna_fase:
                return no_update, no_update
            colunas = COLUNAS_FIXA_ORCAMENTO + [coluna_fase]

    elif grafico_disparado == "grafico-orcamento-barras":
        if not click_barra:
            return no_update, no_update

        label = click_barra["points"][0]["x"]
        coluna_fase = MAPA_FASE_CURTA_PARA_ORCAMENTO.get(label)
        if not coluna_fase:
            return no_update, no_update
        colunas = COLUNAS_FIXA_ORCAMENTO + [coluna_fase]

    else:
        return no_update, no_update

    df_tabela = orcamento[colunas]

    return (
        [{'name': c, 'id': c} for c in colunas],
        df_tabela.to_dict("records")
    )

    layout_orcamento, criar_grafico_orcamento_pizza, criar_grafico_orcamento_barras = criar_layout_orcamento(df)

    figura = criar_grafico_orcamento()
    tabela = orcamento[COLUNAS_FIXA_ORCAMENTO + COLUNAS_ETAPAS_ORCAMENTO].to_dict("records")

    return figura, tabela 

@app.callback(
    Output("download-orcamento", "data"),
    Input("btn-download-orcamento", "n_clicks"),
    prevent_initial_call=True
)
def baixar_excel_orcamento(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    orcamento = df[df['Finalizado'] == True].copy()
    orcamento = orcamento[COLUNAS_FIXA_ORCAMENTO + COLUNAS_ETAPAS_ORCAMENTO]

    return dcc.send_data_frame(
        orcamento.to_excel,
        filename="fases-de-orcamento.xlsx",
        index=False
    )
          
@app.callback(
    Output("grafico-media-orcamento", "figure"),
    Input("tabs-menu", "value")
)
def atualizar_grafico_media_orcamento(tab):
    if tab != "Média mensal da fase de orçamento":
        return dash.no_update
        
    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    orcamento = df[df['Finalizado'] == True].copy()

    layout, criar_grafico_media_orcamento = criar_layout_media_orcamento(df)
     
    return criar_grafico_media_orcamento()

@app.callback(
    Output("tabela-media-orcamento", "data"),
    Input("tabs-menu", "value"),
    Input("grafico-media-orcamento", "clickData"),
    Input("grafico-media-orcamento", "relayoutData"),
)
def atualizar_tabela_media_orcamento(tab, clickData, relayoutData):

    if tab != "Média mensal da fase de orçamento":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    df = df[df['Finalizado'] == True].copy()
    df['Data_fim_desocupacao'] = pd.to_datetime(df['Data_fim_desocupacao'])
    df['mes_ano'] = df['Data_fim_desocupacao'].dt.to_period('M').astype(str)
    
    if relayoutData and relayoutData.get("reset_tabela"):
        return df[COLUNAS_TABELA_MEDIA_ORCAMENTO].to_dict("records")

    if clickData and 'points' in clickData and clickData['points']:
        point0 = clickData['points'][0]

        if point0.get('curveNumber') == 0:
            mes_selecionado = point0.get('customdata')
            if mes_selecionado:
                df = df[df['mes_ano'] == mes_selecionado]

    return df[COLUNAS_TABELA_MEDIA_ORCAMENTO].to_dict('records')
    
@app.callback(
    Output("download-media-orcamento", "data"),
    Input("btn-download-media-orcamento", "n_clicks"),
    prevent_initial_call=True
)
def baixar_excel_media_orcamento(n_clicks): 
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    orcamento = df[df['Finalizado'] == True].copy()
    orcamento = orcamento[COLUNAS_TABELA_MEDIA_ORCAMENTO]

    return dcc.send_data_frame(
        orcamento.to_excel,
        filename="media-exclusiva-fase-orcamento.xlsx",
        index=False
    )
    
@app.callback(
    Output("tabela-desocupacao", "columns"),
    Output("tabela-desocupacao", "data"),
    Input("grafico-desocupacao-pizza", "clickData"),
    Input("grafico-desocupacao-barras", "clickData")
)
def atualizar_tabela_desocupacao(click_pizza, click_barra):
    caminho = session.get("arquivo_excel")
    if not caminho:
        return no_update, no_update

    df = pd.read_excel(caminho)
    desocupacao = df[df["Finalizado"] == 1].copy()

    ctx = callback_context

    colunas = COLUNAS_FIXA_DESOCUPACAO + COLUNAS_ETAPAS_DESOCUPACAO
    df_tabela = desocupacao[colunas]

    if not ctx.triggered: 
        return (
            [{'name': c, 'id': c} for c in colunas],
            df_tabela.to_dict("records")
        )

    grafico_disparado = ctx.triggered_id

    if grafico_disparado == "grafico-desocupacao-pizza":
        if not click_pizza:
            return no_update, no_update

        label = click_pizza["points"][0].get("label")

        if label == "Tempo Total Acumulado nas Fases de Desocupação":
            colunas = COLUNAS_FIXA_DESOCUPACAO + COLUNAS_ETAPAS_DESOCUPACAO
        else:
            coluna_fase = MAPA_FASE_CURTA_PARA_DESOCUPACAO.get(label)
            if not coluna_fase:
                return no_update, no_update
            colunas = COLUNAS_FIXA_DESOCUPACAO + [coluna_fase]

    elif grafico_disparado == "grafico-desocupacao-barras":
        if not click_barra:
            return no_update, no_update
            
        label = click_barra["points"][0]["x"]
        coluna_fase = MAPA_FASE_CURTA_PARA_DESOCUPACAO.get(label)
        if not coluna_fase:
            return no_update, no_update
        colunas = COLUNAS_FIXA_DESOCUPACAO + [coluna_fase]
    else:
        return no_update, no_update

    df_tabela = desocupacao[colunas]

    return (
        [{'name': c, 'id': c} for c in colunas],
        df_tabela.to_dict("records")
    )

    layout_desocupacao, criar_grafico_desocupacao_pizza, criar_grafico_desocupacao_barras = criar_layout_desocupacao(df)

    figura = criar_grafico_desocupacao()
    tabela = desocupacao[COLUNAS_FIXA_DESOCUPACAO + COLUNAS_ETAPAS_DESOCUPACAO].to_dict("records")

    return figura, tabela

@app.callback(
    Output("download-desocupacao", "data"),
    Input("btn-download-desocupacao", "n_clicks"),
    prevent_initial_call=True
)
def baixar_excel_desocupacao(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update

    desocupacao = df[df['Finalizado'] == True].copy()
    desocupacao = desocupacao[COLUNAS_FIXA_DESOCUPACAO + COLUNAS_ETAPAS_DESOCUPACAO]

    return dcc.send_data_frame(
        desocupacao.to_excel,
        filename="fases-da-desocupacao.xlsx", 
        index=False
    )

@app.callback(
    Output("grafico-media-desocupacao", "figure"),
    Input("tabs-menu", "value")
)
def atualizar_grafico_media_desocupacao(tab):
    if tab != "Média mensal da fase de desocupação":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    desocupacao = df[df["Finalizado"] == True].copy()
    
    layout, criar_grafico_media_desocupacao = criar_layout_media_desocupacao(df)

    return criar_grafico_media_desocupacao()

@app.callback(
    Output("tabela-media-desocupacao", "data"),
    Input("tabs-menu", "value"),
    Input("grafico-media-desocupacao", "clickData"),
    Input("grafico-media-desocupacao", "relayoutData"),
)
def atualizar_tabela_media_desocupacao(tab, clickData, relayoutData):
    if tab != "Média mensal da fase de desocupação":
        return dash.no_update

    caminho = session.get("arquivo_excel")
    if not caminho:
        return dash.no_update

    df = pd.read_excel(caminho)
    df = df[df['Finalizado'] == True].copy()
    df['Data_fim_desocupacao'] = pd.to_datetime(df['Data_fim_desocupacao'])
    df['mes_ano'] = df['Data_fim_desocupacao'].dt.to_period('M').astype(str)

    if relayoutData and relayoutData.get("reset_tabela"):
        return df[COLUNAS_TABELA_MEDIA_DESOCUPACAO].to_dict("records")

    if clickData and 'points' in clickData and clickData['points']:
        point0 = clickData['points'][0]

        if point0.get('curveNumber') == 0:
            mes_selecionado = point0.get('customdata')
            if mes_selecionado:
                df = df[df['mes_ano'] == mes_selecionado]

    return df[COLUNAS_TABELA_MEDIA_DESOCUPACAO].to_dict('records')

@app.callback(
    Output("download-media-desocupacao", "data"),
    Input("btn-download-media-desocupacao", "n_clicks"),
    prevent_initial_call=True
)
def baixar_execel_media_desocupacao(n_clicks):
    df = obter_df_sessao()
    if df is None or df.empty:
        return dash.no_update
        
    desocupacao = df[df['Finalizado'] == True].copy()
    desocupacao = desocupacao[COLUNAS_TABELA_MEDIA_DESOCUPACAO]

    return dcc.send_data_frame(
        desocupacao.to_excel,
        filename="media-exclusiva-fase-desocupacao.xlsx",
        index=False
    ) 

@app.callback(
    Output("grafico-imovel-sem-pendencia", "figure"),
    Output("lista-imoveis-sem-pendencia", "children"),
    Output("filtro-imovel-sem-pendencia", "value"),
    Input("grafico-imovel-sem-pendencia", "clickData"),
    Input("filtro-imovel-sem-pendencia", "value")
)
def atualizar_dashboard_sem_pendencias(clickData, filtro_dropdown):
    df = obter_df_sessao()
    if df is None:
        return dash.no_update, dash.no_update, dash.no_update

    layout, VALORES_SP, LABELS_SP, CORES_SP, PULL_SP, total_sp, qtd_com_data, qtd_sem_data = criar_layout_imovel_sem_pendencias(df)

    filtro_final = filtro_dropdown or "todos"
    trigger = ctx.triggered_id

    if trigger == "grafico-imovel-sem-pendencia" and clickData:
        filtro_final = clickData["points"][0]["customdata"]

    fig = criar_grafico_sem_pendencias(
        VALORES_SP,
        LABELS_SP,
        CORES_SP,
        PULL_SP,
        total_sp,
        qtd_com_data,
        qtd_sem_data,
        filtro_final
    )

    df_filtrado, titulo = filtrar_dataframe_sem_pendencias(df, filtro_final)

    tabela = DataTable(
        columns=[{"name": c, "id": c} for c in COLUNAS_TABELA_SEM_PENDENCIAS],
        data=df_filtrado[COLUNAS_TABELA_SEM_PENDENCIAS].to_dict("records"),
        page_size=15,
        fixed_rows={"headers": True},
        style_table={
            "overflowX": "auto",
            "minWidth": "100%",
        },
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontFamily": "Arial",
            "fontSize": "13px",
            "whiteSpace": "normal",
            "minWidth": "220px",
            "width": "220px",
            "maxWidth": "220px",
        },
        style_header={
            "backgroundColor": "#2c3e50",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
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

    return fig, html.Div(
        [
            html.H4(
                titulo,
                style={
                    "fontFamily": "Arial Black",
                    "fontSize": "15px",
                    "color": "black",
                    "marginBottom": "15px",
                    "marginTop": "10px"
                }
            ),
            tabela
        ]
    ), filtro_final
    
@app.callback(
    Output("download-excel-sem-pendencia", "data"),
    Input("btn-download-sem-pendencia", "n_clicks"),
    State("filtro-imovel-sem-pendencia", "value"),
    prevent_initial_call=True
)
def baixar_excel_sem_pendencia(n_clicks, filtro_ativo):

    df = obter_df_sessao()
    df_filtrado, _ = filtrar_dataframe(df, filtro_ativo)

    return dcc.send_data_frame(
        df_filtrado[COLUNAS_TABELA_SEM_PENDENCIAS].to_excel,
        f"desocupacoes_sem_pendencia{filtro_ativo}.xlsx",
        index=False
    )

@app.callback(
    Output("grafico-passou-sem-pendencias", "figure"),
    Output("filtro-passou-sp", "data"),
    Output("tabela-passou-sp", "children"),
    Input("grafico-passou-sem-pendencias", "clickData"),
    State("filtro-passou-sp", "data")
)
def atualizar_grafico_passou_sp(clickData, selected_groups):
    df = obter_df_sessao()
    imoveis_com_data, contagem_fases = processar_dados_passou_sp(df)
    total = len(imoveis_com_data)

    selected_groups = atualizar_grupos_selecionados(contagem_fases, clickData, selected_groups)

    fig = criar_grafico_passou_sem_pendencias(contagem_fases, total, selected_groups)

    df_grupo = imoveis_com_data[imoveis_com_data["fase_encontrada"].isin(selected_groups)]

    tabela = DataTable( 
        columns=[{"name": c, "id": c} for c in COLUNAS_TABELA_PASSOU_SP],
        data=df_grupo[COLUNAS_TABELA_PASSOU_SP].to_dict("records"),
        page_size=15,
        fixed_rows={"headers": True},
        style_table={
            "overflowX": "auto",
            "minWidth": "100%",
        },
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontFamily": "Arial",
            "fontSize": "13px",
            "whiteSpace": "normal",
            "minWidth": "220px",
            "width": "220px",
            "maxWidth": "220px",
        },
        style_header={
            "backgroundColor": "#2c3e50",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
        },
        css=[
            {
                "selector": ".dash-spreadsheet-container .dash-spreadsheet -inner th .dash-cell-value",
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

    return fig, selected_groups, tabela

@app.callback(
    Output("download-excel-passou-sp", "data"),
    Input("btn-download-passou-sp", "n_clicks"),
    State("filtro-passou-sp", "value"),  
    prevent_initial_call=True
)
def baixar_excel_passou_sp(n_clicks, selected_groups):
    df = obter_df_sessao()
    imoveis_com_data, _ = processar_dados_passou_sp(df)

    if selected_groups is None or len(selected_groups) == 0:
        selected_groups = imoveis_com_data['fase_encontrada'].unique()

    df_export = imoveis_com_data[imoveis_com_data["fase_encontrada"].isin(selected_groups)]

    df_export = df_export[COLUNAS_TABELA_PASSOU_SP]

    return dcc.send_data_frame(
        df_export.to_excel,
        f"passou_pela_fase_imovel_sp.xlsx",
        index=False
    )

@app.callback(
    Output("grafico-liberacao", "figure"),
    Output("filtro-liberacao", "data"),
    Output("tabela-liberacao", "children"),
    Input("grafico-liberacao", "clickData"),
    State("filtro-liberacao", "data")
)
def atualizar_grafico_e_tabela(clickData, selected_groups):
    df = obter_df_sessao()
    df_filtrado, contagem_grupo = processar_dados_liberacao(df)
    total = len(df_filtrado)

    selected_groups = atualizar_grupos_selecionados(contagem_grupo, clickData, selected_groups)

    fig = criar_grafico_liberacao_vistoria(contagem_grupo, total, selected_groups)

    df_grupo = df_filtrado[df_filtrado["grupo_vistoria"].isin(selected_groups)]

    tabela = DataTable( 
        columns=[{"name": c, "id": c} for c in COLUNAS_TABELA_LIBERACAO],
        data=df_grupo[COLUNAS_TABELA_LIBERACAO].to_dict("records"),
        page_size=15,
        fixed_rows={"headers": True},
        style_table={
            "overflowX": "auto",
            "minWidth": "100%",
        },
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontFamily": "Arial",
            "fontSize": "13px",
            "whiteSpace": "normal",
            "minWidth": "220px",
            "width": "220px",
            "maxWidth": "220px",
        },
        style_header={
            "backgroundColor": "#2c3e50",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
        },
        css=[
            {
                "selector": ".dash-spreadsheet-container .dash-spreadsheet-inner th .dash-cell-value",
                "rule": """
                    white-space: normal !important;
                    overflow: visible !important;
                    text-overflow: unset ! important;
                    line-height: 1.2;
                """
            },
            {
                "selecotr": ".dash-spreadsheet-container .dash-spreadsheet-inner th",
                "rule": """
                    height: auto !important
                """
            }
        ]
    )

    return fig, selected_groups, html.Div([tabela])

@app.callback(
    Output("download-excel-liberacao", "data"),
    Input("btn-download-liberacao", "n_clicks"),
    State("filtro-liberacao", "value"),  
    prevent_initial_call=True
)
def baixar_excel_liberacao(n_clicks, selected_groups):
    df = obter_df_sessao()
    df_filtrado, _ = processar_dados_liberacao(df)

    if selected_groups is None or len(selected_groups) == 0:
        selected_groups = df_filtrado['grupo_vistoria'].unique()

    df_export = df_filtrado[df_filtrado["grupo_vistoria"].isin(selected_groups)]

    df_export = df_export[COLUNAS_TABELA_LIBERACAO]

    return dcc.send_data_frame(
        df_export.to_excel,
        f"vistorias_liberadas_tabela.xlsx",
        index=False
    )
    
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  
        port=****,
        debug=False       
    )
