import smtplib
import ssl
from email.message import EmailMessage
import os
import mimetypes

#dados de acesso dos emails
email_senha = open('passwords/token', 'r').read()
email_origem = 'rodrigo@asimov.academy' #se alterar o email origem, é necessário alterar também a senha no arquivo "mail_password"
email_destino = ('rodrigo.tadewald@gmail.com')

#textos do email
assunto = 'Orçamento de produtos'
body = open('corpo_email.txt', 'r').read()

#variável para simplificar as chamadas posteriores da função 'EmailMessage()'
mensagem = EmailMessage()

#dados do email
mensagem['From'] = email_origem
mensagem['To'] = email_destino
mensagem['Subject'] = assunto

#estruturação de um arquivo anexo
anexo_path = "imagem.png"
anexo_arquivo = os.path.basename(anexo_path)
mime_type, _ = mimetypes.guess_type(anexo_path)
mime_type, mime_subtype = mime_type.split('/', 1)

#estruturação do email (se o corpo do email for do tipo html, incluir o parâmetro subtype='html', ao lado do parâmetro body.
mensagem.set_content(body)

#adiciona SSL ao código para garantir a segurança dos dados
safe = ssl.create_default_context()

#adiciona o arquivo anexo ao email
with open(anexo_path, 'rb') as ap:
     mensagem.add_attachment(ap.read(), maintype=mime_type, subtype=mime_subtype,
                            filename=os.path.basename(anexo_path))

#acesso e envio do email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=safe) as smtp:
    smtp.login(email_origem, email_senha)
    smtp.sendmail(email_origem, email_destino, mensagem.as_string())