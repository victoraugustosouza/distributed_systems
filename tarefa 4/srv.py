#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC 
import rpyc #modulo que oferece suporte a abstracao de RPC
import time
#servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import ForkingServer,ThreadedServer 
from threading import Thread

# porta de escuta do servidor de echo
PORTA = 10001
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

	# executa quando uma conexao eh fechada
	def on_disconnect(self, conn):
		print("Conexao finalizada:")

	# imprime e ecoa a mensagem recebida
	def exposed_echo(self, msg):
		print(msg)
		return msg

	def exposed_login(self, msg,callback):
		self.callback = rpyc.async_(callback)   # create an async callback
		self.name=msg
		dicionario[msg]=list()
		self.active = True
		self.thread = Thread(target = self.work)
		self.thread.start()

		if msg in lista_user:
			msg="Erro"
		else:
			self.name=msg
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
		temp = msg.split()[0]
		if temp in dicionario.keys():
			dicionario[temp]=dicionario[temp].append(msg)
			return
		else:
			return "Usuário não encontrado"


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
