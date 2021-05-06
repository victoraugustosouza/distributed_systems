#Ver documentação em: https://rpyc.readthedocs.io/en/latest/


import rpyc #modulo que oferece suporte a abstracao de RPC

# endereco do servidor de echo
SERVIDOR = 'localhost'
PORTA = 10004

def iniciaConexao():
	'''Conecta-se ao servidor.
	Saida: retorna a conexao criada.'''
	conn = rpyc.connect(SERVIDOR, PORTA) 
	print(type(conn.root)) # mostra que conn.root eh um stub de cliente
	print(conn.root.get_service_name()) # exibe o nome da classe (servico) oferecido

	return conn
def printt(texto):
	#Função de callback assíncrono. Será chamada quando houver retorno do servidor.
	print(texto)

def login(conn):
	''' Executa login do usuário no servidor. '''
    
	msg=input("Entre com o seu nome de usuário, sem espaços: ")
    
	#chama a função de login no servidor, passa a função de callback e o nome do usuário
	ret = conn.root.exposed_login(msg,printt)

    while ret=='Erro': #garante que não haverá cadastro se houver nome repetido. A verificação é no servidor.
        print("Nome já cadastrado\n")
        msg=input("Entre com o seu nome de usuário, sem espaços: ")
        ret = conn.root.exposed_login(msg, printt)
    print("\n"+ret+"\n")

def logout(conn, bgsrv):
	'''Executar o logout do usuário'''

	#informa servidor que cliente deseja se desconectar. 
	ret = conn.root.exposed_stop()
	bgsrv.stop() #para thread de background que escutava a chegada de mensagens e executava a função de callback
	conn.close() #fecha conexão

def listar_comandos(conn):
	'''Printa os comandos aceitos pelo servidor '''
	print(conn.root.exposed_listar_comandos())

def listar_usuarios(conn):
	'''Printa usuários atualmente ativos '''
	print(conn.root.exposed_listar_user())

def fazRequisicoes(conn, bgsrv):
	'''Faz requisicoes ao servidor e exibe o resultado. '''
	# le as mensagens do usuario ate ele digitar 'fim'
	while True: #checa se são comandos
		msg = input("Digite uma mensagem ou um comando:")
		if msg == '@fim': 
			logout(conn, bgsrv)
			break
		elif msg == '@help': 		
			listar_comandos(conn)
		elif msg == '@listar':
			listar_usuarios(conn)
		else:
			ret = conn.root.exposed_send(msg)	#solicita envio da mensagem ao servidor.
			if ret:
				print(ret)
	

def main():
	conn = iniciaConexao()
	bgsrv = rpyc.BgServingThread(conn) #backgroundthread: escuta a chegada de mensagens e executava a função de callback quando msg chega
	login(conn)
	listar_comandos(conn)
	#interage com o servidor ate encerrar
	fazRequisicoes(conn,bgsrv)

# executa o cliente
if __name__ == "__main__":
	main()
 
