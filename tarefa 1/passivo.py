# Exemplo basico socket (lado passivo)

import socket

HOST = '127.0.0.1'   
PORTA = 5000  

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
	# depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
        msg = novoSock.recv(1024)
        if not msg: 
            break 
        else:
            print("Mensagem do Cliente: "+str(msg,  encoding='utf-8'))
	# envia mensagem de resposta
        novoSock.send(msg) 

novoSock.close() 

sock.close() 
