from bs4 import BeautifulSoup
import requests    # pip install requests

# nosso objetivo nesse código é extrair os trabalhos de uma página

site_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=&txtLocation=New+York').text
doc = BeautifulSoup(site_text, 'lxml')
# print(doc)

# trabalho = doc.find('li', class_='clearfix job-bx wht-shd-bx')
# # print(trabalho.text)

# empresa = trabalho.find('h3', class_='joblist-comp-name').text.strip()
# # print(empresa)

# habilidades = trabalho.find('span', class_='srp-skills').text.strip().split(',')
# # print(habilidades)
# for i in range(len(habilidades)):
#     habilidades[i] = habilidades[i].strip()
# # print(habilidades)

# # tempo = trabalho.find('span', class_='sim-posted')
# # print(tempo)
# # tempo = tempo.find('span')
# # Ou
# tempo = trabalho.find('span', class_='sim-posted').span.text
# # .span, .div ou qualquer semelhante é igual a .find('div') ou .find('span') sem nenhum outro argumento

# # Printando resultados
# print(f'''
# Empresa: {empresa}\n
# Habilidades: {habilidades}\n
# Tempo de Postagem: {tempo}\n
# ''')

# Tendo o conceito em mente, é possível montar um compilado desse código, iterando sobre todos os trabalhos da página
trabalhos = doc.find_all('li', class_='clearfix job-bx wht-shd-bx')
for trabalho in trabalhos:
    empresa = trabalho.find('h3', class_='joblist-comp-name').text.split()
    habilidades = trabalho.find('span', class_='srp-skills').text.strip().split(',')
    for i in range(len(habilidades)):
        habilidades[i] = habilidades[i].strip()
    tempo = trabalho.find('span', class_='sim-posted').span.text

    print(f'''
    Empresa: {empresa}
    Habilidades: {habilidades}
    Tempo de Postagem: {tempo}
    ''')