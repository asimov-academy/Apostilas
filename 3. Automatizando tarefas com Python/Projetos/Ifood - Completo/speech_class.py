'''
pip install SpeechRecognition       => reconhecimento da voz
pip install pyaudio                 => reconhecimento da voz
pip install gTTS                    => API com o google text to speech
pip install playsound==1.2.2        => reproduz a file mp3

REF.: https://letscode.com.br/blog/speech-recognition-com-python
'''

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
import time

class Alicia:
    def __init__(self):
        # self.search_keywords = ['pedi', 'pesquisa', 'busca', 'acha', 'procura', 'varre']
        # self.restaurante_keywords = ['restaurante', 'local', 'lugar']
        # self.itens_keywords = ['prato', 'item', 'lanche', 'elemento', 'produto', 'objeto']
        self.pedidos_keywords = ['pedido', 'rápido', 'rapido', 'instantâneo', 'padrão', 'clássico', 'sempre', 'ágil']
        self.quit_keywords = ['sai', 'fecha', 'encerra']
        self.quit = False
        self.retorno = []
        
        self.loop()

    def ouvir_microfone(self):
        # Habilita o microfone
        microfone = sr.Recognizer()
        with sr.Microphone() as source: 
            # Chama um algoritmo de reducao de ruidos no som
            microfone.adjust_for_ambient_noise(source)
            
            # Frase para o usuario dizer algo e armazenamento do audio
            playsound(os.path.join('default_audios', 'talk.mp3'))
            audio = microfone.listen(source)
        
        # Passa a variável para o algoritmo reconhecedor de padroes com proteção pra caso de falha relativo ao padrão de reconhecimento
        try: frase = microfone.recognize_google(audio,language='pt-BR')
        except sr.UnknownValueError: 
            playsound(os.path.join('default_audios', 'error.mp3'))
            os.remove('last_commmand.mp3')
            time.sleep(3)
            return self.ouvir_microfone()

        return frase

    def reproduzir_audio(self, txt, file='last_commmand.mp3'): 
        # Objeto Google Text-to-Speech e play no audio
        tts = gTTS(txt, lang='pt-br')
        time.sleep(0.5)
        try:
            tts.save(file)
        except:
            import pdb; pdb.set_trace()
        playsound(file)

    def loop(self, txt=''):
        txt = txt + ' ' + self.ouvir_microfone()
        if any(word in txt for word in self.quit_keywords):
            self.quit = True

        # # Caso de pesquisa
        # elif any(word in txt for word in self.search_keywords):
        #     # # Caso de pesquisa por restaurante - offline por agora
        #     # if any(word in txt for word in self.restaurante_keywords):
        #     #     self.reproduzir_audio('Qual restaurante?')
        #     #     restaurante = self.ouvir_microfone()
        #     #     print('RESTAURANTE:', restaurante)
        #     #     self.retorno = ["pesquisa", restaurante]

        #     # é possível tirar essa linha abaixo, mas vamos deixar caso queiramos pesquisar por restaurante mais tarde
        #     if any(word in txt for word in self.itens_keywords): pass
        #         # Caso de pesquisa por item
        #         # self.reproduzir_audio('Qual item gostaria?')
        #         # item = self.ouvir_microfone()
        #         # print('ITEM:', item)
        #         # self.retorno = ["pesquisa", item]

        # Pedidos rapidos pré-configurados.
        elif any(word in txt for word in self.pedidos_keywords):
            if not "configurado_path" in txt:
                self.reproduzir_audio("Qual pedido de sempre?", "alternative_command.mp3")
                return self.loop('pedido padrão configurado_path')
            if any(word in txt for word in ['um', '1']):
                self.retorno = ["padrao", 1]
                print('Pedidos pre-configurados 1...')
                print('TEXTO:', txt)
            if any(word in txt for word in ['dois', '2']):
                print('Pedidos pre-configurados 2...')
                print('TEXTO:', txt)
            if any(word in txt for word in ['três', '3']):
                print('Pedidos pre-configurados 3...')
                print('TEXTO:', txt)

        else:
            print("Caiu aqui")
            print("Nao entendi nada")
            return self.ouvir_microfone()
    def finalizar_processo(self):
        
        pass