from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from analise import gerar_analise

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/api/analise/{ticker}")
def obter_analise_json(ticker: str):
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
    print(f"Gerando relatório web para o ticker: {ticker}")
    
    stats, caminho_imagem, explicacao = gerar_analise(ticker.upper())

    if not stats:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' não encontrado ou sem dados.")

    stats_formatado = {key: f"{value:.2f}" for key, value in stats.items()}
    
    contexto = {
        "request": request,
        "ticker": ticker.upper(),
        "estatisticas": stats_formatado,
        "explicacao": explicacao,
        "url_grafico": f"/{caminho_imagem}"
    }
    
    return templates.TemplateResponse("resultado.html", contexto)