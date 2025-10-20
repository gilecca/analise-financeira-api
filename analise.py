import yfinance as yf
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import os

def gerar_explicacao_grafico(ticker: str, estatisticas: dict):
    """Gera uma explicação em texto sobre a análise do ativo."""
    ultimo_preco = estatisticas['ultimo_valor']
    mediana_preco = estatisticas['mediana']
    
    explicacao = (
        f"Esta é uma análise técnica para o ativo {ticker.upper()}.\n\n"
        f"O gráfico de linha (preta) mostra a variação do preço de fechamento diário para os últimos 6 meses.\n\n"
        f"O gráfico contém as seguintes linhas de referência:\n"
        f" - Linha Vermelha: É a média móvel simples de 20 dias (MMS20). Ela suaviza os preços e ajuda a identificar a tendência de curto prazo do ativo.\n"
        f" - Linha Laranja (tracejada): É a Mediana de todo o período, o valor que divide os preços exatamente ao meio.\n"
        f" - Linhas de Desvio Padrão (pontilhadas): Marcam as zonas de volatilidade com cores distintas:\n"
        f"    - Verde: Para ±1 desvio padrão, onde cerca de 68% dos preços costumam estar.\n"
        f"    - Roxo: Para ±2 desvios padrão, abrangendo cerca de 95% dos preços.\n"
        f"    - Ciano: Para ±3 desvios padrão, indicando faixas de preço menos comuns.\n\n"
        f"Estatísticas Principais (baseadas em todo o período de 2 anos):\n"
        f"- Último Preço de Fechamento: R$ {ultimo_preco:.2f}\n"
        f"- Preço Médio no Período: R$ {estatisticas['media']:.2f}\n"
        f"- Mediana no Período: R$ {mediana_preco:.2f}\n"
        f"- Volatilidade (Desvio Padrão): R$ {estatisticas['desvio_padrao']:.2f}\n"
        f"- Faixa de Preço no Período: R$ {estatisticas['minimo']:.2f} (mín) a R$ {estatisticas['maximo']:.2f} (máx)"
    )
    return explicacao

def gerar_analise(ticker: str):
    """
    Função principal que retorna estatísticas, caminho do gráfico e explicação.
    """
    os.makedirs("static", exist_ok=True)

    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=730)

    dados = yf.download(ticker, start=data_inicial, end=data_inicial + timedelta(days=730)) # Limitando a 2 anos exatos

    if dados.empty:
        return None, None, None

    if isinstance(dados.columns, pd.MultiIndex):
        dados.columns = dados.columns.droplevel(1)
        
    dados = dados[:-1]

    preco_fechamento = dados['Close']
    estatisticas = {
        "media": preco_fechamento.mean(),
        "mediana": preco_fechamento.median(),
        "desvio_padrao": preco_fechamento.std(),
        "minimo": preco_fechamento.min(),
        "maximo": preco_fechamento.max(),
        "ultimo_valor": preco_fechamento.iloc[-1]
    }
    
    dados_grafico = dados.tail(180) # Gráfico para os últimos 6 meses

    periodo_media_movel = 20 
    dados_grafico[f'SMA{periodo_media_movel}'] = dados_grafico['Close'].rolling(window=periodo_media_movel).mean()

    media_total = estatisticas['media']
    mediana = estatisticas['mediana']
    dp = estatisticas['desvio_padrao']
    
    linhas_horizontais = [
        mediana,
        media_total + dp, media_total - dp,          # ±1 DP
        media_total + 2 * dp, media_total - 2 * dp,  # ±2 DP
        media_total + 3 * dp, media_total - 3 * dp   # ±3 DP
    ]
    
    cores = [
        '#FFA500',      # Mediana (Laranja)
        '#28A745', '#28A745',  # Desvio Padrão 1 (Verde)
        '#6f42c1', '#6f42c1',  # Desvio Padrão 2 (Roxo)
        '#17A2B8', '#17A2B8'   # Desvio Padrão 3 (Ciano)
    ]
    estilos = ['--', ':', ':', ':', ':', ':', ':']

    explicacao = gerar_explicacao_grafico(ticker, estatisticas)

    caminho_grafico = f"static/grafico_{ticker.replace('.', '_').upper()}.png"

    add_plot = [mpf.make_addplot(dados_grafico[f'SMA{periodo_media_movel}'], color='#dc3545')] # Média Móvel (Vermelho)
    
    market_colors = mpf.make_marketcolors(up='black', down='black')
    custom_style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=market_colors)

    mpf.plot(dados_grafico,
             type='line',
             style=custom_style,
             title=f'Análise Estatística de Preços - {ticker.upper()}',
             ylabel='Preço (R$)',
             figratio=(16,8),
             savefig=caminho_grafico,
             hlines=dict(hlines=linhas_horizontais, colors=cores, linestyle=estilos, linewidths=1.2),
             addplot=add_plot
            )

    return estatisticas, caminho_grafico, explicacao