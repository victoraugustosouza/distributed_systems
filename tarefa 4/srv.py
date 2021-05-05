#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC 
import rpyc #modulo que oferece suporte a abstracao de RPC
import time
#servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import ForkingServer,ThreadedServer 
from threading import Thread

# porta de escuta do servidor de echo
PORTA = 10004
lista_user = []
dicionario = {}

# classe que implementa o servico de echo
class Echo(rpyc.Service):

    
	# executa quando uma conexao eh criada
	def on_connect(self, conn):
		print("Conexao iniciada:")

	def exposed_stop(self):   # this method has to be exposed too
		self.active = False
		self.thread.join()
		dicionario.pop(self.name)
		lista_user.remove(self.name)
		for i in range (0, len(lista_user)):
			dicionario[lista_user[i]].append("\nUsuário " + self.name + " saiu do chat.")

	# executa quando uma conexao eh fechada
	def on_disconnect(self, conn):
		print("\nConexao com " + self.name + " finalizada")

	# imprime e ecoa a mensagem recebida
	def exposed_echo(self, msg):
		print(msg)
		return msg

	def exposed_login(self, msg,callback):

		self.name=msg

		if msg in lista_user:
			print("Usuário " + str(msg) + " já cadastrado.")
			msg="Erro"
		else:
			self.callback = rpyc.async_(callback)   # create an async callback
			dicionario[msg]=list()
			self.active = True
			self.thread = Thread(target = self.work)
			self.thread.start()
			lista_user.append(msg)
			msg="Cadastro Realizado com Sucesso"
			print(lista_user)

		return msg

	def exposed_listar_comandos(self):
		msg = "Comandos:\nEnviar mensagem(@usuário mensagem)\nListar usuário(@listar)\nListar Possibilidades(@help)\nFechar conexão(close_conn)\n\n"
		return msg

	def exposed_listar_user(self):
		msg = ''
		for i in lista_user:
			msg=msg+i+','
		return msg  

	def exposed_send(self,msg):

		temp_lista = msg.split()
		temp = []
		verifica_usuarios = []
		tamanho_string_usuario = 0

		if temp_lista[0][0] != '@':
			return "Comando inválido\nTente digitar @NomeDoUsuario mensagem sem espaços antes do @"
		else:
			for i in range (0, len(temp_lista)):
				if temp_lista[i][0] == "@":
					temp.append(temp_lista[i][1:].strip())
				else:
					break
		
		for i in range(0, len(temp)):
			if temp[i] not in lista_user:
				verifica_usuarios.append(temp[i])
			else:
				tamanho_string_usuario += (len(temp[i]) + 2)

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

		msg = msg[tamanho_string_usuario:]

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
