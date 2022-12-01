# pip install pillow
#NOTE Recomendo sempre ir executando os códigos no jupyter e rodando o objeto "imagem" pra ver o output logo na sequencia
# Classe de imagem da biblioteca pillow

# python3 -m pip install --upgrade Pillow
from PIL import Image, ImageDraw, ImageFilter

# Abrindo a imagem com o comando .open()
imagem = Image.open("image.jpg")

# A partir do momento que abrimos essa imagem, iremos operar todos comandos em cima desse objeto de imagem
imagem.show()           # para mostrar a imagem - ira mostrar a imagem com o 

# Se quiser ver a imagem no jupyter, basta rodar o comando no objeto

# Tipo, formato
imagem.format
imagem.mode

# Tamanho
imagem.width
imagem.height
imagem.size     # retorna uma tupla contendo (altura, largura)

# Se quiser todas as informações contidas naquela imagem (dificil acontecer)
imagem.info

# Salvando a foto com as alterações feitas e alterando o formato JPG -> PNG
imagem.save('image_save.png')
# Provando que o formato foi alterado
im_aux = Image.open('image_save.png')
im_aux.format

# Dar um novo tamanho para a imagem
imagem.resize((400, 300))

# Como cortar a imagem
# args, esquerda, em cima, direita, embaixo
imagem.crop((0,0,300,300))
imagem.show()

# Rotacionar imagens
imagem.transpose(Image.Transpose.FLIP_LEFT_RIGHT)     # Horizontalmente
imagem.transpose(Image.Transpose.FLIP_TOP_BOTTOM)     # Verticalmente
imagem.rotate(45)  # para rotacionar a imagem - fugindo do canva
imagem.transpose(Image.Transpose.ROTATE_90)     # Graus possíveis abaixo
# ROTATE_90
# ROTATE_180
# ROTATE_270



# É possivel criar thumbnails - pequena representação de uma imagem grande
# Basta enviar como argumento o tamanho que se quer da thumbnail, em pixels
imagem = Image.open('image.jpg')
imagem.thumbnail((90,90))
imagem.save('thumbnail.jpg')
im_aux = Image.open('thumbnail.jpg')
im_aux.show()

# É possivel dar merge em duas imagens, para criar uma nova imagem
# Trabalhando com RGB
image = Image.open("maca.jpg")
r, g, b = image.split()
# r         São objetos de imagem também, mas com a separação de intensidade
# g             das respectivas cores
# b
image.show()
image = Image.merge("RGB", (b, g, r)) # Nesse caso invertemos o azul com vermelho, usando o comando merge
image.show()


# Como trabalhar com duas imagens ==================

imagem = Image.open("maca.jpg")
imagem2 = Image.open("image.jpg")

# Colando uma em cima da outra, primeiro a imagem, depois as coordenadas
imagem.paste(imagem2)               # Sem as coordenadas 
imagem.paste(imagem2, (400, 800))   # x,y

# É possível usar mascaras para colar a imagem
imagem = Image.open("maca.jpg")
imagem2 = Image.open("image.jpg")

# Estamos fazendo uma mascara para cortar a segunda imagem
mascara = Image.new("L", imagem2.size, 0)   # "L" significa greyscale
tam = imagem2.size
draw = ImageDraw.Draw(mascara)
draw.ellipse((20, 20, tam[0]-20, tam[1]-20), fill=255) # Fazendo uma elipse no centro do desenho, e pintando de branco
# As coordenadas são referentes aos dois extremos da elipse

# O draw é um objeto do tipo ImageDraw. Não é de fato uma imagem, mas é possível salva-la para ver o resultado
mascara.save('mask.jpg', quality=95)

# Colando a imagem com a mascara
imagem.paste(imagem2, (0, 0), mascara)

# É possivel fazer um blur na mascara para aplicar na colagem
mascara_blur = mascara.filter(ImageFilter.GaussianBlur(10))
mascara_blur.save('mask_blur.jpg', quality=95)
imagem.paste(imagem2, (0, 0), mascara_blur)

