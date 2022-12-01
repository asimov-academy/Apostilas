import os

# Mostra o caminho completo do diretório atual
os.getcwd()

# Retorna uma lista contendo todos os arquivos de determinada pasta
os.listdir()
os.listdir('/Users/rodrigosoares/')

# os.chdir() - Troca o diretório atual
actual_dir = os.getcwd()
print(os.getcwd())
os.chdir('/Users/rodrigosoares/')
print(os.getcwd())
os.chdir(actual_dir)

# Cria uma pasta.
os.mkdir()

# Renomeia um arquivo
os.rename()

# Deleta arquivo. Não deleta pastas.
os.remove()

# Deleta uma pasta.
os.rmdir()


# Executa um comando de shell
cmd = 'date'
os.system(cmd)
