from bs4 import BeautifulSoup   # o import é assim pq beautifulsoup é uma biblioteca dentro da pasta bs4

with open('asimov_ex.html', 'r') as file:
    conteudo = file.read()
    # print(conteudo)                       # Apenas printando o conteudo da file

    ex = BeautifulSoup(conteudo, 'lxml')    # Scrape com o BeautifulSoup, sem apenas ler a file, segundo elemento é o parse.
    # perguntar pro Rodrigo o que é parse na programação
    # parse, ou utilizar um parse, nada mais é do que transformar de um tipo 1 para outro tipo 2
    # Nesse caso estamos transformando o código HTML para string, utilizando uma lxml

    # print(ex.prettify())      # Aqui temos a identação exata

    # tags = ex.find('p') # Esse código só vai retornar a primeira situação do 'p', se quisermos todas
    all_tags = ex.find_all('p') # pra apresentar isso na aula, retorna uma lista
    # print(all_tags)

    for p in all_tags:
        print(p.text)