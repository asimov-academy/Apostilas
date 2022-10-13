# Definindo variáveis como funções
def soma_um(numero):
    return numero + 1

adiciona_um = soma_um
adiciona_um(5)


# Definindo funções dentro de outras funções
def soma_um(numero):
    def adiciona_um(numero):
        return numero + 1


    result = adiciona_um(numero)
    return result
soma_um(4)


# Passando funções como argumentos de outras funções
def soma_um(numero):
    return numero + 1

def function_call(function):
    numero_to_add = 5
    return function(numero_to_add)

function_call(soma_um)


# Funções retornando outras funções
def funcao_ola():
    def diga_oi():
        return "Hi"
    return say_hi
hello = funcao_ola()
hello()



# Criando decoradores
def decorador_maiusculo(function):
    def wrapper():
        func = function()
        cria_maiusculo = func.upper()
        return cria_maiusculo

    return wrapper

def diga_oi():
    return 'hello there'


funcao_decorada = decorador_maiusculo(diga_oi)
funcao_decorada()

# Com decorador
@decorador_maiusculo
def diga_oi():
    return 'hello there'

diga_oi()