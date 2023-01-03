import pandas as pd
import sqlite3

# TESTES PARA O SQL =========================
# Criando o Conn
conn = sqlite3.connect('sistema.db')
c = conn.cursor()

# create table if not exists TableName (col1 typ1, ..., colN typN)
c.execute("""CREATE TABLE IF NOT EXISTS processos (
            'No Processo' number,
            Empresa text,
            Tipo text,
            Ação text,
            Vara text,
            Fase text,
            Instância number,
            'Data Inicial' text,
            'Data Final' text,
            'Processo Concluído' number,
            'Processo Vencido' number,
            Advogados text,
            Cliente text,
            'Cpf Cliente' number,
            'Descrição' text)""")

c.execute("""CREATE TABLE IF NOT EXISTS advogados (
            Advogado text,
            OAB number,
            CPF number)""")

df_adv = pd.read_sql("SELECT * FROM advogados", conn)
df_proc = pd.read_sql("SELECT * FROM processos", conn)

conn.commit()
conn.close()