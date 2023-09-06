import pandas as pd
import requests
import telebot

#IMPORTANDO DADOS DAS EMPRESAS
url = 'http://www.fundamentus.com.br/resultado.php'
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
r = requests.get(url, headers=header)
tabela = pd.read_html(r.text,  decimal=',', thousands='.')[0]

#TRATANDO DADOS
for coluna in ['Div.Yield', 'Mrg Ebit', 'Mrg. Líq.', 'ROIC', 'ROE', 'Cresc. Rec.5a']:
  tabela[coluna] = tabela[coluna].str.replace('.', '')
  tabela[coluna] = tabela[coluna].str.replace(',', '.')
  tabela[coluna] = tabela[coluna].str.rstrip('%').astype('float') / 100

#CRIANDO RANKING
tabela = tabela[['Papel', 'Cotação', 'EV/EBIT', 'ROIC', 'Liq.2meses', 'P/L']]
tabela['Empresa'] = tabela['Papel'].str[:4]
tabela = tabela.drop_duplicates(subset='Empresa')
tabela = tabela.set_index('Papel')
tabela = tabela[tabela['Liq.2meses'] > 1000000]
tabela = tabela[tabela['P/L'] > 0]
tabela = tabela[tabela['EV/EBIT'] > 0]
tabela = tabela[tabela['ROIC'] > 0]
tabela['RANKING_EV/EBIT'] = tabela['EV/EBIT'].rank(ascending = True)
tabela['RANKING_ROIC'] = tabela['ROIC'].rank(ascending = False)
tabela['RANKING_TOTAL'] = tabela['RANKING_EV/EBIT'] + tabela['RANKING_ROIC']
tabela = tabela.sort_values('RANKING_TOTAL')
tabela = tabela.head(15)

ranking = tabela.index
ranking = '\n'.join(f'{i+1}. {acao}' for i, acao in enumerate(ranking))

#ENVIANDO MENSAGEM PARA TELEGRAM COM O RANKING
mensagem = f'RANKING DA MAGIC FORMULA:\n{ranking}'
print(mensagem)
bot = telebot.TeleBot("YOUR BOT HERE")
group = "YOUR GROUP HERE"
bot.send_message(group, mensagem)
