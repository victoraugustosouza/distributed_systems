
#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading
import socket
import select
import sys
import threading
import re
import unidecode
from collections import Counter

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10001 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena as conexoes ativas
conexoes = {}
#lock para acesso do dicionario 'conexoes'
lock = threading.Lock()


def data_extracao(filename):
    '''
    Essa função extrai o texto do arquivo especificado por filename. 
    Se não for encontrado retorna False.
	Se encontrado, retorna o texto.
    '''
    #tenta abrir arquivo e captura erro caso não encontre
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
    #transforma texto em lista
    palavras = texto_sem_simbolos_especiais.split(" ")

	#lista de palavras a serem ignoradas por serem muito comuns
	# e portanto atrapalharem a contagem 
    nao_contar= ['a','e','i','o','u','','um','de','em','do']
    
	#contador de palavras
    for palavra in palavras: 
        if palavra in d:
            d[palavra] = d[palavra] + 1
        else:
	        if palavra not in nao_contar:
		        d[palavra]=1
			
    return str(d.most_common(10))

def iniciaServidor():
	'''Cria um socket de servidor e o coloca em modo de espera por conexoes
	Saida: o socket criado'''
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

	# vincula a localizacao do servidor
	sock.bind((HOST, PORT))

	# coloca-se em modo de espera por conexoes
	sock.listen(5) 

	# configura o socket para o modo nao-bloqueante
	sock.setblocking(False)

	# inclui o socket principal na lista de entradas de interesse
	entradas.append(sock)

	return sock

def aceitaConexao(sock):
	'''Aceita o pedido de conexao de um cliente
	Entrada: o socket do servidor
	Saida: o novo socket da conexao e o endereco do cliente'''

	# estabelece conexao com o proximo cliente
	clisock, endr = sock.accept()

	# registra a nova conexao
	lock.acquire()
	conexoes[clisock] = endr 
	lock.release()

	return clisock, endr

def atendeRequisicoes(clisock, endr):
	'''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
	Entrada: socket da conexao e endereco do cliente
	Saida: '''

	while True:
		#recebe nome do arquivo
		filename = clisock.recv(1024)
		if not filename: 
			print(str(endr) + '-> encerrou')
			lock.acquire()
			del conexoes[clisock] #retira o cliente da lista de conexoes ativas
			lock.release()
			clisock.close() # encerra a conexao com o cliente
			return 

        #Extração do texto completo
		conteudo=data_extracao(filename)
            
		if not conteudo: #quando há erro
			msg = "Arquivo não encontrado"
		else:
            #Texto extraído é processado e é retornado a string já pronta para envio.
			msg = processamento(conteudo)

        #Envia mensagem de resposta
		print(str(endr) + ': ' + str(msg))
		clisock.send(bytes(msg,'utf-8')) 


def main():
	'''Inicializa e implementa o loop principal (infinito) do servidor'''
	sock = iniciaServidor()
	print("Pronto para receber conexoes...")
	print("Digite 'fim' para terminar o servidor caso não aja mais conexões ativas")
	print("Digite 'listar' para listar as conexões ativas")
	while True:
		#espera por qualquer entrada de interesse
		leitura, escrita, excecao = select.select(entradas, [], [])
		#tratar todas as entradas prontas
		for pronto in leitura:
			if pronto == sock:  #pedido novo de conexao
				clisock, endr = aceitaConexao(sock)
				print ('Conectado com: ', endr)
				#cria nova thread para atender o cliente
				cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr))
				cliente.start()
			elif pronto == sys.stdin: #entrada padrao
				cmd = input()
				if cmd == 'fim': #solicitacao de finalizacao do servidor
					if not conexoes: #somente termina quando nao houver clientes ativos
						sock.close()
						sys.exit()
					else: 
						print("Existem conexoes ativas.")
				elif cmd=='listar': #lista conexões ativas
					print("Lista de Conexões Ativas:")
					for i in conexoes:
						print(str(i.getpeername()))
			

main()


