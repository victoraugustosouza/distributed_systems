import rpyc #modulo que oferece suporte a abstracao de RPC
import time
from rpyc.utils.server import ThreadedServer 
from threading import Thread

# porta de escuta do servidor de echo
PORTA = 10004

#contém o nome dos usuários conectados
lista_user = []

#contém as mensagens enviadas para o usuários que ainda não foram entregues. 
dicionario = {}

# classe que implementa o servico de bate papo
class Echo(rpyc.Service):

    
	def on_connect(self, conn):
		''' 	Executa quando uma conexao eh criada '''
		print("Conexao iniciada:")

	def exposed_stop(self):  
		'''
		É chamada pelo cliente quando o mesmo deseja encerrar a conexão.
		'''
		#Encerra execução da thread que checa constantemente se há mensagens para o cliente.
		self.active = False
		self.thread.join()
		
		#Remove a lista de mensagens do cliente.
		dicionario.pop(self.name)
		
		#Remove o cliente da liste de conectados.
		lista_user.remove(self.name)
		
		#Adiciona uma mensagem avisando que o cliente saiu na lista de mensagens de todos os outros usuários.
		for i in range (0, len(lista_user)):
			dicionario[lista_user[i]].append("\nUsuário " + self.name + " saiu do chat.")

	
	def on_disconnect(self, conn):
	# executa quando uma conexao eh fechada
		print("\nConexao com " + self.name + " finalizada")


	def exposed_login(self, msg,callback):
		'''
		Executa o login do cliente.
		'''
		self.name=msg

		#checa se nome já foi utilizado
		if msg in lista_user:
			print("Usuário " + str(msg) + " já cadastrado.")
			msg="Erro"
		else:
			#Guarda na classe a função de callback, que será chamada quando ouver mensagem para cliente. Essa função
			#será executada no cliente, assíncronamente. No cliente essa função é print.
			self.callback = rpyc.async_(callback)   
			
			#Cria no dicionario uma lista para guardar as mensagens do cliente.
			dicionario[msg]=list()

			#Cria nova thread para ficar checando se há novas mensagens para o cliente.
			self.active = True
			self.thread = Thread(target = self.work)
			self.thread.start()
			
			#Adiciona o cliente na lista de usuários.
			lista_user.append(msg)
			
			msg="Cadastro Realizado com Sucesso"
			print(lista_user)

		return msg

	def exposed_listar_comandos(self):
		'''
		Retorna os comandos disponíveis.
		'''
		msg = "Comandos:\nEnviar mensagem(@usuário mensagem)\nListar usuário(@listar)\nListar Possibilidades(@help)\nFechar conexão(@fim)\n\n"
		return msg

	def exposed_listar_user(self):
		'''
		Listar os usuários onlines no momento.
		'''
		msg = ''
		for i in lista_user:
			msg=msg+i+','
		return msg  

	def exposed_send(self,msg):
		'''
		Envia a mensagem.
		'''
		temp_lista = msg.split()
		temp = []
		verifica_usuarios = []
		tamanho_string_usuario = 0
		
		#checa se o indicador de comando(@) está presente .
		if temp_lista[0][0] != '@':
			return "Comando inválido\nTente digitar @NomeDoUsuario mensagem sem espaços antes do @"
		else:  #checa se há outros destinatários para a mensagem, se houver, adiciona na variável temp
			for i in range (0, len(temp_lista)):
				if temp_lista[i][0] == "@":
					temp.append(temp_lista[i][1:].strip())
				else:
					break
		#se cliente destinatário não está na lista de clientes do servidor então cliente é adicionado na lista verifica_usuarios,
		#se está na lista de clientes então seu tamanho é contabilizado.
		for i in range(0, len(temp)):
			if temp[i] not in lista_user:
				verifica_usuarios.append(temp[i])
			else:
				tamanho_string_usuario += (len(temp[i]) + 2)

		#verifica se usuários na lista verifica_usuarios realmente são clientes ativos.
		if len(verifica_usuarios) > 0:
			if len(verifica_usuarios) == 1:
				msg = "\nUsuário : \n"
			else:
				msg = "\nUsuários : \n"
			for i in range(0, len(verifica_usuarios)):
				msg += verifica_usuarios[i] + "\n"
			
			if len(verifica_usuarios) == 1:
				msg += "Não está no chat \n"
			else:
				msg += "Não estão no chat \n"

			return msg

		#pega parte da mensagem, excluindo nomes do destinatários.
		msg = msg[tamanho_string_usuario:]

		#salva mensagem no dicionário, com nome de quem enviou na frente
		for i in range (0, len(temp)):
			if temp[i] in dicionario.keys():
				dicionario[temp[i]].append(self.name + " : " + msg)
			
		return

		# if temp in dicionario.keys():
		# 	msg = msg[len(temp):]
		# 	dicionario[temp].append(self.name + ":" + msg)
		# 	return
		# else:
		# 	return "Usuário não encontrado"


	def work(self):
		'''
		Verifica constantemente se há mensagem para o cliente. Se ouver, retorna a última mensagem da lista, e remove
		a mesma da lista.
		A função callback será chamada assíncronamente no cliente quando houver mensagem para o cliente.
		'''
		while self.active:
			if len(dicionario[self.name]) > 0:
				msg = dicionario[self.name][-1]
				del dicionario[self.name][-1]
				self.callback(msg)   # notify the client of the change


# dispara o servidor
if __name__ == "__main__":
	srv = ThreadedServer(Echo, port = PORTA)
	srv.start()


### Tipos de servidores
#https://rpyc.readthedocs.io/en/latest/api/utils_server.html

#servidor que dispara uma nova thread a cada conexao
#from rpyc.utils.server import ThreadedServer

#servidor que atende uma conexao e termina
#from rpyc.utils.server import OneShotServer

### Configuracoes do protocolo RPC
#https://rpyc.readthedocs.io/en/latest/api/core_protocol.html#rpyc.core.protocol.DEFAULT_CONFIG
