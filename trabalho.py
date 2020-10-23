# Atenção instalar as bibliotecas abaixo:
# pip install requests
# pip install beautifulsoup4
# pip install selenium
# pip install webdriver_manager
# pip install easygui
# pip install PyQt5

# Importa as bibliotecas
import time
import easygui
import sys
import re
import bs4
from urllib.request import urlopen, Request
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from PyQt5.QtWidgets import QSplashScreen, QApplication
from PyQt5.QtGui import QPixmap


# Lista de mensagens a serem eviadas

# Mensagens Introdutórias
msgs_intro = []

# Bloco de Mensagens sobre o Tempo
msgs_tempo = []

# Bloco de Mensagens sobre as Notícias
msgs_noticias = []

# Bloco de Mensagens sobre as Cotação do Dólar
msgs_dolar = []

# Bloco de Mensagens Final
msgs_final = []
msgs_final.append("Tenha um excelente dia!")

# Define o período atual do dia
def periodo():
    now = datetime.now()

    if now.hour >= 0 and now.hour < 12:
        return "Bom dia!"
    elif now.hour >= 12 and now.hour < 18:
        return "Boa tarde!"
    else:
        return "Boa noite!"

# Limpa os espaços iniciais e finais da palavra/frase
def trim(texto):
    s = texto
    pattern = re.compile(r'\s+$')    
    s = re.sub(pattern, '', s)
    pattern = re.compile(r'^\s+')
    s = re.sub(pattern, '', s)
    return s

# Retira os acentos das vogais
def formata_texto(texto):
    texto = trim(texto)
    texto = texto.lower()
    texto = texto.replace("ã","a")
    texto = texto.replace("á","a")
    texto = texto.replace("à","a")
    texto = texto.replace("é","e")
    texto = texto.replace("í","i")
    texto = texto.replace("õ","a")
    texto = texto.replace("ó","o")
    texto = texto.replace("ü","u")
    return texto

# Abre um browser do Chrome com o Whatsapp
def abre_whatsapp():
    # Acessa o browser através do selenium
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://web.whatsapp.com/')

    time.sleep(2)

    if easygui.boolbox("Você já se conectou no whatsapp?", "Conectar-se no Whatsapp", ["Sim","Não"] ) == 1:     # show a Continue/Cancel dialog

        return driver # user chose Continue
    else:  # user chose Cancel
        driver.quit()
        sys.exit(0)

# Buscar contatos/grupos
def buscar_contato(driver):

    contato = ""

    while contato == "" or contato =="novaTentativa":

        # Informe a cidade que deseja obter as informações
        contato = easygui.enterbox("Informe o nome do contato/grupo?",title="Nome Contato/Grupo:")

        if contato == "":
            easygui.msgbox("O nome do contato/grupo não pode estar vazio!", title="Erro:", ok_button="OK")

        else:
            campo_pesquisa = driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]')
            campo_pesquisa.click()
            campo_pesquisa.send_keys(contato)
            campo_pesquisa.send_keys(Keys.ENTER)

            nome_contato_grupo = driver.find_element_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span').text
            
            if formata_texto(contato) != formata_texto(nome_contato_grupo):
                easygui.msgbox("O contato/grupo informado: (" + contato +  ") não é o mesmo localizado: (" + nome_contato_grupo + ")", title="Erro:", ok_button="OK")

                if easygui.boolbox("Deseja digitar um novo contato/grupo?", "Nome Contato/Grupo:", ["Sim","Não"] ) == 1:     # show a sim/não dialog
                    contato = "novaTentativa"
                else:  # user chose Cancel
                    driver.quit()
                    sys.exit(0)
    
    msgs_intro.append("Olá *" + nome_contato_grupo + "*, " + periodo())
    msgs_intro.append("*Receba o seu informativo diário*")


# Enviar mensagem para o contato/grupo
def escrever_mensagem(mensagem, driver):
    campo_mensagem = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')

    x = len(mensagem)
    y = 0
    for msg in mensagem:
        campo_mensagem.send_keys(Keys.SHIFT + Keys.ENTER) # Comando para Pular Linha        
        campo_mensagem.send_keys(msg)# Comando para Escrever
        y += 1
        if x == y:
            campo_mensagem.send_keys(Keys.ENTER)

# Captura as informações de previsão de tempo de uma cidade pré-informada
def previsao_tempo():

    # Informe a cidade que deseja obter as informações
    nome_cidade = easygui.enterbox("De qual cidade você quer receber informações sobre o tempo?",title="Nome da cidade:")

    while nome_cidade == "":
        easygui.msgbox("O nome da cidade não pode estar vazio!", title="Erro:", ok_button="OK")
        # Informe a cidade que deseja obter as informações
        nome_cidade = easygui.enterbox("Qual cidade quer receber notícia?",title="Nome da cidade:")

    # Acessa o browser através do selenium e inibe a tela
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)

    # Abre a imagem de carregando
    app = QApplication([])
    pixmap = QPixmap("Carregando.png")
    splash = QSplashScreen()
    splash.setPixmap(pixmap)
    splash.show()
    
    # Carrega o html da página
    driver.get('https://tempo.cptec.inpe.br/')
    
    campo_buscar_cidade = driver.find_element_by_xpath('//*[@id="search"]')
    campo_buscar_cidade.send_keys(nome_cidade)
    time.sleep(2)
    campo_buscar_cidade.send_keys(Keys.ARROW_DOWN)
    time.sleep(2)
    campo_buscar_cidade.send_keys(Keys.ENTER)
    time.sleep(5)
    link = driver.current_url
    driver.quit()
   
    # Acessa o browser através do BeautifulSoup
    data = urlopen(link).read()
    soup = bs4.BeautifulSoup(data, features="html.parser")

    estado_cidade = soup.findAll('label', {'class': 'pt-1'})[0].text
    # Pega somete o estado e a cidade
    estado_cidade = estado_cidade[0:estado_cidade.find('|')]

    # Compara o nome da cidade dígitada com o nome da cidada capturada do site   
    nome_cidade = formata_texto(nome_cidade)
    cidade = formata_texto(estado_cidade[0:estado_cidade.find('/')])

    if nome_cidade != cidade:
        msgs_tempo.append("Não foi possível carregar os dados para a cidade: " + nome_cidade )

    else:
        msgs_tempo.append("*Veja como está o tempo hoje:*")
        msgs_tempo.append("*INEP*")
        msgs_tempo.append(estado_cidade)

        dia_semana = soup.findAll('span', {'class': 'font-weight-bold text-uppercase'})[0].text
        dia = soup.findAll('small')[1].text
        msgs_tempo.append(dia_semana + ", " + dia)

        temperatura_maxima = soup.findAll('span', {'class': 'temp-max text-center font-dados'})[0].text
        msgs_tempo.append("*Temperatura máxima:* " + temperatura_maxima.replace('°', " graus"))

        temperatura_minima = soup.findAll('div', {'class': 'p-1 temp-min font-dados'})[0].text
        msgs_tempo.append("*Temperatura mínima:* " + temperatura_minima.replace('°', " graus"))

        # Verifica qual é o período atual do dia para pegar as informações necessárias
        i = 1
        periodo_dia = soup.findAll('span', {'class': 'font-weight-bold'})[i].text

        if periodo_dia == "Manhã":
            previsao = soup.findAll('img', {'alt': 'Previsão de Tempo'})[i - 1].get('title')
            msgs_tempo.append("*" + periodo_dia + "*" + ": " + previsao)

            i += 1
            periodo_dia = soup.findAll('span', {'class': 'font-weight-bold'})[i].text

            if periodo_dia == "Tarde":
                previsao = soup.findAll('img', {'alt': 'Previsão de Tempo'})[i - 1].get('title')
                msgs_tempo.append("*" + periodo_dia + "*"  + ": " + previsao)

                i += 1
                periodo_dia = soup.findAll('span', {'class': 'font-weight-bold'})[i].text

                if periodo_dia == "Noite":
                    previsao = soup.findAll('img', {'alt': 'Previsão de Tempo'})[i - 1].get('title')
                    msgs_tempo.append("*" + periodo_dia + "*" + ": " + previsao)

        elif periodo_dia == "Tarde":
            previsao = soup.findAll('img', {'alt': 'Previsão de Tempo'})[i - 1].get('title')
            msgs_tempo.append("*" + periodo_dia + "*" + ": " + previsao)

            i += 1
            periodo_dia = soup.findAll('span', {'class': 'font-weight-bold'})[i].text

            if periodo_dia == "Noite":
                previsao = soup.findAll('img', {'alt': 'Previsão de Tempo'})[i - 1].get('title')
                msgs_tempo.append("*" + periodo_dia + "*" + ": " + previsao)

        elif periodo_dia == "Noite":
            previsao = soup.findAll('img', {'alt': 'Previsão de Tempo'})[i - 1].get('title')
            msgs_tempo.append("*" + periodo_dia + "*" + ": " + previsao)

        # Bloco de mensagens humanizadas
        temperatura_media = (int(temperatura_maxima.replace('°', "")) + int(temperatura_minima.replace('°', "")))/2

        if temperatura_media >= 25:
            msgs_tempo.append("_Coloque uma roupa leve, será um dia bem quente._")
        elif temperatura_media >= 20:
            msgs_tempo.append("_Dia com temperatura bem confortável, aproveite._")
        elif temperatura_media >= 15:
            msgs_tempo.append("_Está um pouco frio, mas não o necessário para usar jaqueta com pele de urso._")
        elif temperatura_media >= 5:
            msgs_tempo.append("_Mó frio, Elsa do Frozen passou aqui._")
    
    splash.close()

# Captura ultimas noticias 
def noticia():
    # Endereço do Site
    link = "https://valor.globo.com/ultimas-noticias/"

    # Acessa o browser através do BeautifulSoup
    data = urlopen(link).read()
    soup = bs4.BeautifulSoup(data, features="html.parser")

    msgs_noticias.append("*Últimas notícias:*")

    msgs_noticias.append("*Valor Econômico*")

    tema = soup.findAll('span', {'class': 'feed-post-header-chapeu'})[0].text
    msgs_noticias.append("*Tema*: " + tema)

    titulo = soup.findAll('a', {'class': 'feed-post-link'})[0].text
    msgs_noticias.append("*Titulo*: " + titulo)

    resumo = soup.findAll('div', {'class': 'feed-post-body-resumo'})[0].text
    msgs_noticias.append(resumo)

    data = soup.findAll('span', {'class': 'feed-post-datetime'})[0].text
    tema = soup.findAll('span', {'class': 'feed-post-metadata-section'})[0].text
    msgs_noticias.append("_" + data + " - Em " + tema.strip() + "_")

    msgs_noticias.append("----------------------------------------------")

    tema = soup.findAll('span', {'class': 'feed-post-header-chapeu'})[1].text
    msgs_noticias.append("*Tema*: " + tema)

    titulo = soup.findAll('a', {'class': 'feed-post-link'})[1].text
    msgs_noticias.append("*Titulo*: " + titulo)

    resumo = soup.findAll('div', {'class': 'feed-post-body-resumo'})[1].text
    msgs_noticias.append(resumo)

    data = soup.findAll('span', {'class': 'feed-post-datetime'})[1].text
    tema = soup.findAll('span', {'class': 'feed-post-metadata-section'})[1].text
    msgs_noticias.append("_" + data + " - Em " + tema.strip() + "_")

# Captura a cotação atual do dólar
def cotacao_dolar(): 
    # Endereço do Site
    link = "https://economia.uol.com.br/cotacoes/"

    # Acessa o browser através do BeautifulSoup
    data = urlopen(link).read()
    soup = bs4.BeautifulSoup(data, features="html.parser")

    msgs_dolar.append("*Cotação do Dólar:*")

    msgs_dolar.append("*UOL Economia*")

    campo_cotacao = soup.findAll('h3', {'class' : 'tituloGrafico'})[0].text
    msgs_dolar.append(campo_cotacao)

# Inicia a execução do crawler
if easygui.boolbox("Deseja iniciar a aplicação?", "Inicializar aplicação:", ["Sim","Não"] ) == 1: # show a sim/não dialog

    # Chama os métodos
    previsao_tempo()
    noticia()
    cotacao_dolar()

    ## Métodos Whatsapp
    driver = abre_whatsapp()
    buscar_contato(driver)
    escrever_mensagem(msgs_intro, driver)
    escrever_mensagem(msgs_tempo, driver)
    escrever_mensagem(msgs_noticias, driver)
    escrever_mensagem(msgs_dolar, driver)
    escrever_mensagem(msgs_final, driver)

else:  # user chose Cancel
    sys.exit(0)


