# Exemplo basico socket (lado passivo)

import socket
import re
import unidecode
from collections import Counter

def data_extracao(filename):
    '''
    Essa função extrai o texto do arquivo especificado por filename. 
    Se não for encontrado retorna False.
    '''
    #tenta abrir arquivo
    try:
      f = open(filename, "r", encoding='utf-8')
    except IOError:
      return False

    #lê arquivo de uma só vez
    texto = f.read()
    f.close()
    return texto

def processamento(conteudo):
    '''
    Essa função limpa o texto removendo números, simbolos especiais, pontuação
    e transformando em minusculo.
    Em seguida conta o número de ocorrências de palavras, ignorando vogais e 
    conectores (de, da, do, etc).
    A saída é uma string com as 10 palavras que mais aparecem
    '''

    
    texto_sem_pontuacao = re.sub(r'[^\w\s]','',conteudo)
    texto_sem_numeros = re.sub(r'[0-9]', ' ', texto_sem_pontuacao)
    texto_sem_acento = unidecode.unidecode(texto_sem_numeros)
    texto_minusculo = texto_sem_acento.lower()
    texto_sem_simbolos_especiais = texto_minusculo.replace('\n', '').replace('\x0c', '')
    
    #Contando as palavras
    d = Counter()
    
    palavras = texto_sem_simbolos_especiais.split(" ")
    nao_contar= ['a','e','i','o','u','','um','de','em','do']
    
    for palavra in palavras: 
        if palavra in d:
            if palavra not in nao_contar:
                d[palavra] = d[palavra] + 1
        else:
            d[palavra] = 1
    
    return str(d.most_common(10))


HOST = '127.0.0.1'   
PORTA = 5008  

# cria um socket para comunicacao
print("Criando socket...")
sock = socket.socket() 

print("Binding Endereço e Porta....")
sock.bind((HOST, PORTA))

print("Definindo limite máximo de conexão e entrando em modo de espera de conexão..")
sock.listen(5) 

# aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
print("Em espera por primeira conexão na fila...")

novoSock, endereco = sock.accept() 
print ('Conectado com: ', endereco)

while True:

    filename = novoSock.recv(1024)
    if not filename: 
        break 
    else:
        #Extração do texto completo
        conteudo=data_extracao(filename)
            
        if not conteudo: #quando há erro
            msg = "Arquivo não encontrado"
        else:
            #Texto extraído é processado e é retornado a string já pronta para envio.
            msg = processamento(conteudo)

        #Envia mensagem de resposta
        novoSock.send(bytes(msg,'utf-8')) 

novoSock.close() 

sock.close() 