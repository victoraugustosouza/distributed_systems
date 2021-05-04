#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Cliente de echo usando RPC
import rpyc #modulo que oferece suporte a abstracao de RPC

# endereco do servidor de echo
SERVIDOR = 'localhost'
PORTA = 10001

def iniciaConexao():
	'''Conecta-se ao servidor.
	Saida: retorna a conexao criada.'''
	conn = rpyc.connect(SERVIDOR, PORTA) 
	print(type(conn.root)) # mostra que conn.root eh um stub de cliente
	print(conn.root.get_service_name()) # exibe o nome da classe (servico) oferecido

	return conn
def printt(texto):
	print(texto)

def login(conn):
    msg=input("entre com o seu nome de usuário, sem espaços: ")
    ret = conn.root.exposed_login(msg,printt)
    while ret=='Erro':
        print("Nome já cadastrado\n")
        msg=input("Entre com o seu nome de usuário, sem espaços")
        ret = conn.root.exposed_login(msg)
    print("\n"+ret+"\n")

def listar_comandos(conn):
	print(conn.root.exposed_listar_comandos())

def listar_usuarios(conn):
	print(conn.root.exposed_listar_user())

def fazRequisicoes(conn):
	'''Faz requisicoes ao servidor e exibe o resultado.
	Entrada: conexao estabelecida com o servidor'''
	# le as mensagens do usuario ate ele digitar 'fim'
	while True: 
		msg = input("Digite uma mensagem ou um comando('fim' para terminar):")
		if msg == '@fim': break 
		if msg == '@help': 		
			listar_comandos(conn)
		if msg == '@listar':
			listar_usuarios(conn)
		else:
			ret = conn.root.exposed_send(msg)	
			if ret:
				print(ret)
		# envia a mensagem do usuario para o servidor
		#ret = conn.root.exposed_echo(msg)

		# imprime a mensagem recebida
		#print(ret)

	# encerra a conexao
	conn.root.exposed_stop()
	bgsrv.stop()
	conn.close()
	

def main():
	conn = iniciaConexao()
	bgsrv = rpyc.BgServingThread(conn)
	login(conn)
	listar_comandos(conn)
	#interage com o servidor ate encerrar
	fazRequisicoes(conn)

# executa o cliente
if __name__ == "__main__":
	main()
 
