# Exemplo basico socket (lado ativo)

import socket

HOST = '127.0.0.1' 
PORTA = 5000       

# cria socket
sock = socket.socket() 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

# envia uma mensagem para o par conectado
texto = input("Entre com o texto a ser enviado para o servidor. Caso não deseje mais enviar textos digite stop.\n")

while texto != "stop":

    sock.send(bytes(texto,'utf-8'))

    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    msg = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
    print("\nRetorno  do Servidor:\t"+str(msg,  encoding='utf-8')+"\n")
    texto = input("Entre com o texto a ser enviado para o servidor. Caso não deseje mais enviar textos digite stop.\n")


# imprime a mensagem recebida

# encerra a conexao
sock.close() 
