import requests
from bs4 import BeautifulSoup

class Site:
    def __init__ (self, opcao:str):
        self.opcao = opcao

    def update_news(self):
        if self.opcao.lower() == 'globo':
            url = 'https://www.globo.com/'
            browsers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \(KHTML, like Gecko) Chrome / 86.0.4240.198Safari / 537.36"}
            page = requests.get(url, headers = browsers)

            resposta = page.text
            soup = BeautifulSoup(resposta, 'html.parser')
            noticias = soup.find_all('a')

            target_class_1 = 'post__title'
            target_class_2 = 'post-multicontent__link--title__text'

            news_dict_globo = {}

            for noticia in noticias:       
                if (noticia.h2 != None) and (noticia.h2.get('class') != None):
                    if target_class_1 in noticia.h2.get('class'):
                        news_dict_globo[noticia.h2.text] = noticia.get('href')
                    if target_class_2 in noticia.h2.get('class'):
                        news_dict_globo[noticia.h2.text] = noticia.get('href')
            self.news = news_dict_globo

        if self.opcao.lower() == 'veja':
            url = 'https://veja.abril.com.br/'
            browsers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \(KHTML, like Gecko) Chrome / 86.0.4240.198Safari / 537.36"}
            page = requests.get(url, headers = browsers)

            resposta = page.text
            soup = BeautifulSoup(resposta, 'html.parser')
            noticias = soup.find_all('a')

            target_class_1 = 'related-article'
            target_class_2 = 'title'

            news_dict_veja = {}

            for noticia in noticias:
                if (noticia.get('class') != None) and (target_class_1 in noticia.get('class')):
                    news_dict_veja[noticia.text] = noticia.get('href')
                if (noticia.h2 != None) and (noticia.h2.get('class') != None) and (target_class_2 in noticia.h2.get('class')):
                    news_dict_veja[noticia.h2.text] = noticia.get('href')
                if (noticia.h3 != None) and (noticia.h3.get('class') != None) and (target_class_2 in noticia.h3.get('class')):
                    news_dict_veja[noticia.h3.text] = noticia.get('href')
                if (noticia.h4 != None) and (noticia.h4.get('class') != None) and (target_class_2 in noticia.h4.get('class')):
                    news_dict_veja[noticia.h4.text] = noticia.get('href')
            self.news =  news_dict_veja

        if self.opcao.lower() == 'r7':
            url = 'https://www.r7.com/'
            browsers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \(KHTML, like Gecko) Chrome / 86.0.4240.198Safari / 537.36"}
            page = requests.get(url, headers = browsers)

            resposta = page.text
            soup = BeautifulSoup(resposta, 'html.parser')
            noticias = soup.find_all('a')

            target_class_1 = 'r7-flex-title-h4__link'
            target_class_2 = 'r7-flex-title-h5__link'
            target_class_3 = 'r7-flex-title-h6__link'

            news_dict_r7 = {}          
                        
            for i in range(len(noticias)):
                if noticias[i].get('class') != None:
                    if target_class_1 in noticias[i].get('class'):
                        news_dict_r7[noticias[i].text.split("\n")[1].strip()] = noticias[i].get('href')
                    if target_class_2 in noticias[i].get('class'):
                        news_dict_r7[noticias[i].text.split("\n")[1].strip()] = noticias[i].get('href')
                    if target_class_3 in noticias[i].get('class'):
                        news_dict_r7[noticias[i].text.split("\n")[1].strip()] = noticias[i].get('href')

            self.news = news_dict_r7

        if self.opcao.lower() == 'cnn':
            url = 'https://www.cnnbrasil.com.br/'
            browsers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \(KHTML, like Gecko) Chrome / 86.0.4240.198Safari / 537.36"}
            page = requests.get(url, headers = browsers)

            resposta = page.text
            soup = BeautifulSoup(resposta, 'html.parser')
            noticias = soup.find_all('a')

            target_class_1 = 'headline__primary_title'
            target_class_2 = 'home__title'
            target_class_3 = 'articles__title'
            target_class_4 = 'webstories_title'
            news_dict_cnn = {}

            for i in range(len(noticias)):
                if (noticias[i].h2 != None) and (noticias[i].h2.get('class') != None) and (target_class_1 in noticias[i].h2.get('class')):
                    news_dict_cnn[noticias[i].h2.text] = noticias[i].get('href')
                if noticias[i].h3 != None and (noticias[i].h3.get('class') != None):
                    if target_class_2 in noticias[i].h3.get('class'):
                        news_dict_cnn[noticias[i].h3.text] = noticias[i].get('href')
                    if target_class_3 in noticias[i].h3.get('class'):
                        news_dict_cnn[noticias[i].h3.text] = noticias[i].get('href')
                    if target_class_4 in noticias[i].h3.get('class'):
                        news_dict_cnn[noticias[i].h3.text] = noticias[i].get('href')

            self.news = news_dict_cnn

