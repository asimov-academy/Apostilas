from PIL import Image
import os

reduct_fact = 0.5

# Criando a pasta das files comprimidas
compressed_path = "compressed_images"
if compressed_path not in os.listdir():
    os.mkdir(compressed_path)

# Coletando as files
files_path = 'fotos'
files = [i for i in os.listdir(files_path) if 'jpg' in i]

size_antes = 0  # Bytes - para ser em MegaBytes, /(1024*1024)
size_depois = 0 
# Iterando sobre todas as files
for file in files:
    # Tamanho anterior, para questoes de feedback
    file_path = os.path.join(files_path, file)
    new_path = os.path.join(compressed_path, file)

    file_stats = os.stat(file_path)
    size_antes += file_stats.st_size

    # Comprimindo a imagem
    img = Image.open(file_path)

    new_w = int(reduct_fact * img.size[0])
    new_h = int(reduct_fact * img.size[1])
    img = img.resize((new_w, new_h), Image.ANTIALIAS)

    img.save(new_path, 'JPEG', optimize=True, quality=95)

    file_stats = os.stat(new_path)
    size_depois += file_stats.st_size

# Imprimindo os resultados
diferenca = (size_antes - size_depois)/(1024*1024)
percent = 100*diferenca/size_antes*(1024*1024)
print(f"Tamanho Anterior (Mb): {size_antes/(1024*1024)}\nTamanho Comprimido (Mb): {size_depois/(1024*1024)}")
print(f"Diferença de {diferenca} Megabytes")
print(f"Reduzido o tamanho das files em {round(percent,2)}%")