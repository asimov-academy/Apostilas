from PIL import Image
import os

# Lendo a watermark e pegando o seu tamanho
watermark = Image.open('watermark.png')
width_w, height_w = watermark.size

# Criando a pasta das files com marca d'agua
image_path = "watermark_ok"
if image_path not in os.listdir():
    os.mkdir(image_path)

# Coletando as files
files_path = 'fotos'
files = [i for i in os.listdir(files_path) if 'jpg' in i]

# Iterando sobre as fotos e inserindo a marca dagua
for file in files:
    file_path = os.path.join(files_path, file)
    new_path = os.path.join(image_path, file)

    # Abrindo a file e coletando o seu tamanho para calculos
    image = Image.open(file_path)
    width, height = image.size

    # Recalculando o tamanho da marca dagua relativo ao tamanho da imagem
    base_width = width*0.2
    wpercent = (base_width/float(width_w))
    hsize = int((float(height_w)*float(wpercent)))
    base_width = int(base_width)
    watermark = watermark.resize((base_width,hsize))

    # Colando a watermark no canto inferior direito e salvando a imagem na pasta
    image.paste(watermark, (width-base_width, height-hsize), watermark)
    image.save(new_path, 'JPEG')
