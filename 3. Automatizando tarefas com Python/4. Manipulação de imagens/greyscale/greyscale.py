from PIL import Image
import os

# Criando a pasta das files com marca d'agua
image_path = "greyscale_images"
if image_path not in os.listdir():
    os.mkdir(image_path)

# Coletando as files
files_path = 'fotos'
files = [i for i in os.listdir(files_path) if 'jpg' in i]

for file in files:
    # Abrindo a file e convertendo para GreyScale diretamente
    file_path = os.path.join(files_path, file)
    new_path = os.path.join(image_path, file)
    image = Image.open(file_path).convert('L')

    # Direcionando para o folder criado (ou existente)
    image.save(new_path, 'JPEG')