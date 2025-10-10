
from fastapi import FastAPI, HTTPException, Request 

from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from analise import gerar_analise

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    """
    Esta função é executada quando o usuário acessa a URL raiz ('/').
    Ela renderiza e retorna a página inicial interativa (home.html).
    """
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/api/analise/{ticker}")
def obter_analise_json(ticker: str):
    """
    Esta é uma rota de API pura. Ela retorna os dados em formato JSON.
    É útil se você quiser que outro programa consuma os dados, em vez de um humano vendo uma página web.
    """
    stats, caminho_imagem, explicacao = gerar_analise(ticker.upper())
    
    if not stats:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' não encontrado.")
    
    stats_formatado = {key: f"{value:.2f}" for key, value in stats.items()}
    
    return {
        "ticker_analisado": ticker.upper(),
        "estatisticas": stats_formatado,
        "explicacao_analise": explicacao,
        "url_grafico": f"/{caminho_imagem}"
    }

@app.get("/relatorio/{ticker}")
def gerar_relatorio_web(ticker: str, request: Request):
    """
    Esta é a rota principal para o usuário. Ela gera a análise e decide qual página HTML mostrar:
    - Se a análise for bem-sucedida, mostra 'resultado.html' com todos os dados.
    - Se a análise falhar, mostra 'erro.html' com uma mensagem amigável.
    """
    print(f"Gerando relatório web para o ticker: {ticker}")
    
    stats, caminho_imagem, explicacao = gerar_analise(ticker.upper())

    if not stats:
        contexto_erro = {
            "request": request,
            "ticker": ticker.upper()
        }
        return templates.TemplateResponse("erro.html", contexto_erro, status_code=404)

    stats_formatado = {key: f"{value:.2f}" for key, value in stats.items()}
 
    contexto_sucesso = {
        "request": request,
        "ticker": ticker.upper(),
        "estatisticas": stats_formatado,
        "explicacao": explicacao,
        "url_grafico": f"/{caminho_imagem}"
    }

    return templates.TemplateResponse("resultado.html", contexto_sucesso)