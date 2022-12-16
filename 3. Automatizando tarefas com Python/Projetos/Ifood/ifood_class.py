from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from imbox import Imbox # pip install imbox
from email.message import EmailMessage

from datetime import date, datetime
import time
import re
import json
import os

from threading import Thread

'''
Selenium - browser automation software
WebDriver - explica o Chrome pro Selenium - ChromeDriver
Chrome - web browser

O problema é que toda vez que se atualiza o Chrome, provável que tenha que reinstalar o ChromeDriver, como pular isso?
webdriver-manager é um manager que
'''
class Isimov:
    def __init__(self, email):
        self.email = email
        self.senha = open(os.path.join('passwords', 'password_gmail'), 'r').read()
        self.valor_final = 0
        self.retorno = []

        # inicializando o ifood
        self.initialize_ifood()

    def initialize_ifood(self):
        # inserindo processo de inicialização em uma função para utilizar como thread
        # afinal, se o navegador não estiver aberto, as outras funcs não podem rodar
        def open_ifood(self):
            chrome_options = Options()
            # chrome_options.add_argument("--headless") # para abrir o navegador sem UI

            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.driver.get("https://www.ifood.com.br/inicio")
            assert "iFood" in self.driver.title
            # Logando via email
            while True:
                try:
                    self.driver.find_element(By.XPATH, '//*[contains(text(), "Entrar ou cadastrar")]').click()
                    self.driver.find_element(By.XPATH, '//*[contains(text(), "E-mail")]').click()
                    self.driver.find_element(By.NAME, "email").send_keys("rodrigovanzelotti@gmail.com" + Keys.RETURN)
                    break
                except: pass

            # Verificação do código do email - consumindo do email para inserir no ifood
            try:
                time.sleep(5)  # tempo pro ifood mandar o código
                self.senha = open(os.path.join('passwords', 'password_gmail'), 'r').read()
                self.email = 'rodrigovanzelotti@gmail.com'
                host = 'imap.gmail.com'

                mail = Imbox(host, username=self.email, password=self.senha)

                # TESTES =====================
                while True:
                    time.sleep(5) # evitar over request
                    msgs_do_ifood = mail.messages(sent_from='naoresponder@login.ifood.com.br', date__gt=date.today())
                    msg_list = [msg for uid, msg in msgs_do_ifood]
                    if msg_list == None:
                        print("O código de acesso não foi enviado... Tentantiva de reenviar")
                        self.driver.find_element(By.XPATH, '//*[contains(text(), "Não recebi meu código")]').click()
                        self.driver.find_element(By.XPATH, '//*[contains(text(), "Reenviar código")]').click()
                        continue
                    else:
                        title = msg_list[-1].subject
                        if "é o seu código de acesso" in title:
                            # code = title[:6]
                            for n, code in enumerate(title[:6]):
                                self.driver.find_element(By.ID, f'otp-input-{n}').send_keys(code)
                        else: continue
                    try:
                        time.sleep(1.5)
                        self.driver.find_element(By.XPATH, '//*[contains(text(), "Código expirado ou inválido")]')
                        for n in range(6): self.driver.find_element(By.ID, f'otp-input-{n}').send_keys(Keys.BACKSPACE)
                    except: break
            except Exception as e: print('\n Exception: ', e)
            # Selecionando a localização
            while True:
                try: self.driver.find_element(By.CSS_SELECTOR, "[aria-label=Casa]").click(); break
                except: time.sleep(5)

        self.init_ifood = Thread(target=open_ifood, args=(self,))
        self.init_ifood.start()
        pass

    def pedido(self, tipo, pedido):
        self.init_ifood.join()
        # pedido padrão do usuário
        if tipo == "pesquisa": self.pedido_pesquisa(pedido)
        if tipo == "padrao": self.pedido_padrao(pedido)
        # Como desenvolver os pedidos padrões?
        '''
        Documentação para desenvolvimento de pedidos padrões:
        Registrar os pedidos padrões em código ou deixar que o usuário registre esse pedido padrão?

        Registrado em código:
            Talvez não seja uma boa, mas certamente mais prático; como funcionaria:
                1. Perguntar qual o pedido padrão que o usuário quer via Alicia
                2. Dado o número, confirmar qual o pedido (nome do restaurante/item)
                3. Realizar o pedido via ifood_class (como padronizar isso para os pedidos padrões?)]

        Registrado pelo usuário:
            Para registrar os pedidos padrões do usuário, seria necessário salvar essas infos em um arquivo qualquer
            no computador, conseguir puxá-los e atualizá-los caso necessário. Pra isso, atualizariamos algumas variavel
            self.padroes[] e ao iniciar o programa, baixaríamos as infos desse arquivo ainda na função initialize_ifood().
            Mas como estruturar esses dados e automatizá-los? CSV [restaurante, item, ?]. Sinceramente, ideia muito complexa.
                1. Para salvar pedidos padrões, poderia ser perguntado ao final de cada compra normal de pesquisa. "Salvar como pedido padrão?"
                    O único contra é que isso nos impossibilita de pedir combos ou mais de um item, o que seria a graça do pedido padrão...
                2. Se sim, registra-se o restaurante e o nome exato do item que estamos comprando.
                3. Tendo o restaurante e o item, é possível utilizá-los pela engine de pesquisa posteriormente.
        '''
    
    def pedido_padrao(self, numero):
        pedidos = {1: 'big mac', 2: 'generico1', 3: 'generico2'}
        match numero:
            case 1:
                # 1. Qual o termo especifico de pesquisa?
                pedido = pedidos[numero]
                search = self.driver.find_element(By.CSS_SELECTOR, "[role='search']")
                search.send_keys([Keys.CONTROL + "a", Keys.BACKSPACE])
                search.send_keys(pedido + Keys.ENTER)
                
                while True:
                    try:
                        self.driver.find_element(By.XPATH, '//*[contains(text(), "Itens")]').click()
                        break
                    except: time.sleep(3)
                
                #   a. Achar o Mcdonald's no titulo
                time.sleep(7)
                restaurantes = self.driver.find_elements(By.XPATH, "//article[@class='merchant-list-carousel']")

                kill = False
                for rest in restaurantes:
                    if "Mcdonald's".lower() in rest.text.lower():
                        itens = rest.find_elements(By.CLASS_NAME, 'merchant-list-carousel__item-title')
                        for item in itens:
                            if (re.search('McOferta'.lower(), item.text.lower()) and re.search("Big Mac".lower(), item.text.lower())): 
                                item.click(); 
                                break
                            kill = True
                    if kill: break   
                
                #   b. Filtrando os requisitos obrigatórios para o pedido (apenas o refri)  
                time.sleep(7)
                list_options = self.driver.find_elements(By.CLASS_NAME, 'dish-garnishes')
                if len(list_options) != 0:
                    list_options = list_options[0].find_elements(By.CLASS_NAME, 'garnish-choices__list')
                else:
                    self.retorno = ["O restaurante esta fechado! Até a proxima."]

                #   b.1. Achando a fanta laranja
                for opt in list_options:
                    if "OBRIGATÓRIO" in opt.text:
                        try:
                            opt.find_element(By.XPATH, '//*[contains(text(), "Fanta laranja")]').click()
                        except:
                            opt.find_element(By.XPATH, '//*[contains(text(), "Coca-Cola")]').click()
                
                #   c. Adicionar pedido
                while True:
                    try: self.driver.find_element(By.XPATH, '//*[contains(text(), "Adicionar")]').click(); break
                    except: time.sleep(3)
                try:
                    if recado := self.driver.find_element(By.XPATH, '//*[contains(text(), "Esta loja abre às")]').text:
                        print(f"A loja esta fechada, {recado}")                         # GTTs
                        self.driver.quit()
                except: pass
                
                # ir pra href "/pedido/finalizar"
                while True:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, '[href="/pedido/finalizar"]').click()
                        break
                    except: time.sleep(5)
                    
                with open(os.path.join('passwords', 'card.json')) as f:
                    card_data = json.load(f)

                time.sleep(5)
                self.driver.find_element(By.XPATH, '//*[contains(text(), "Adicionar novo cartão")]').click()
                time.sleep(5)
                self.driver.find_element(By.XPATH, '//*[contains(text(), "Débito")]').click(),
                inputs= self.driver.find_elements(By.TAG_NAME, 'input')

                for inp, value in zip(inputs, card_data.values()):
                    inp.send_keys(value)    
                self.driver.find_element(By.XPATH, '//*[contains(text(), "Adicionar")]').click()
                
                time.sleep(10)
                apelido = card_data['apelido']
                self.driver.find_element(By.XPATH, f'//*[contains(text(), "{apelido}")]').click()
                
                cpf_input = self.driver.find_element(By.CSS_SELECTOR, '[name="idDocument"]')
                cpf_input.send_keys([Keys.CONTROL + "a", Keys.BACKSPACE])
                
                cpf_input.send_keys(card_data['cpf'])
                
                if self.driver.find_element(By.XPATH, '//*[contains(text(), "Fazer pedido")]'):
                    print('possivel fazer o pedido')
                    # self.driver.find_element(By.XPATH, '//*[contains(text(), "Fazer pedido")]').click()
                try:
                    recado = self.driver.find_element(By.XPATH, '//*[contains(text(), "O pedido mínimo para essa loja é de ")]').text
                    print(f"Nao foi possivel realizar o pedido pois {recado}")
                    self.driver.quit()
                except: pass

                valor = self.driver.find_element(By.XPATH, '//span[@data-test-id="total-price"]').text
                self.valor_final = float(valor[3:].replace(',', '.'))


            case 2:
                print("Pedido 2 foi requerido. Cachorro Quente do Bigode")
            case 3:
                print("Pedido 3 foi requerido. Açai com leite ninho")

    # def finalizar_pedido(self, result):
    #     positive = ['finalizar', 'sim']
    #     negative = ['não', 'cancelar']
    #     if any(word for word in txt for word in self.itens_keywords)

    def pedido_pesquisa(self, item): 
        '''
        Separar possíveis paths. Estamos pesquisando um restaurante ou um item?
        Se for um item, devemos ler os primeiros cards disponíveis na aba de item e seus respectivos preços;
        - Na sequencia, solicitar para escolher entre os cards de 1 a 5 por ex

        Se for um restaurante, abrir o restaurante e ler os 5 primeiros itens, ou os promocionais;
        - Na sequencia, solicitar para escolher entre os cards de 1 a 5 por ex

        ** Testar o algorítmo de voz!
        '''
        # 1. Qual o termo especifico de pesquisa?
        pass
        