import yfinance as yf
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import os

def gerar_explicacao_grafico(ticker: str, estatisticas: dict):
    """Gera uma explicação em texto sobre a análise do ativo."""
    ultimo_preco = estatisticas['ultimo_valor']
    media_preco = estatisticas['media']
    
    tendencia = "acima" if ultimo_preco > media_preco else "abaixo"
    
    explicacao = (
        f"Esta é uma análise técnica para o ativo {ticker.upper()}.\n\n"
        f"O gráfico de candlestick mostra a variação de preço diária, onde cada 'vela' representa um dia. Esse gráfico contém os dados relativos aos últimos 6 meses."
        f" Velas verdes indicam dias de alta e velas vermelhas, dias de baixa.\n\n"
        f"As linhas azul e laranja são as Médias Móveis de 20 e 50 dias, respectivamente. Elas ajudam a visualizar a tendência do ativo. "
        f"Quando a linha azul (curto prazo) está acima da laranja (longo prazo), geralmente sinaliza uma tendência de alta.\n\n"
        f"Estatísticas Principais:\n"
        f"- Último Preço de Fechamento: R$ {ultimo_preco:.2f}\n"
        f"- Preço Médio no Período: R$ {media_preco:.2f} (o preço atual está {tendencia} da média)\n"
        f"- Volatilidade (Desvio Padrão): R$ {estatisticas['desvio_padrao']:.2f}\n"
        f"- Faixa de Preço no Período: R$ {estatisticas['minimo']:.2f} (mín) a R$ {estatisticas['maximo']:.2f} (máx)"
    )
    return explicacao

def gerar_analise(ticker: str):
    """
    Função principal que retorna estatísticas, caminho do gráfico e explicação.
    """
    # Garante que a pasta 'static' exista
    os.makedirs("static", exist_ok=True)

    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=730)

    # 1. Coleta de Dados
    dados = yf.download(ticker, start=data_inicial, end=data_final)

    if dados.empty:
        return None, None, None

    dados.columns = dados.columns.droplevel(1)
    dados = dados[:-1]

    # 2. Análise Estatística
    preco_fechamento = dados['Close']
    estatisticas = {
        "media": preco_fechamento.mean(),
        "mediana": preco_fechamento.median(),
        "desvio_padrao": preco_fechamento.std(),
        "minimo": preco_fechamento.min(),
        "maximo": preco_fechamento.max(),
        "ultimo_valor": preco_fechamento.iloc[-1]
    }

    # 3. Geração da Explicação
    explicacao = gerar_explicacao_grafico(ticker, estatisticas)

    # 4. Geração do Gráfico
    dados_grafico = dados.tail(180)

    caminho_grafico = f"static/grafico_{ticker.replace('.', '_').upper()}.png"

    mpf.plot(dados_grafico,
             type='candle',
             style='yahoo',
             title=f'Análise de Preços - {ticker.upper()}',
             ylabel='Preço (R$)',
             volume=True,
             mav=(20, 50),
             figratio=(16,8),
             savefig=caminho_grafico
            )

    return estatisticas, caminho_grafico, explicacao