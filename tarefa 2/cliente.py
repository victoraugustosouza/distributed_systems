# Exemplo basico socket (lado ativo)
import socket

HOST = '127.0.0.1' 
PORTA = 5008       

# cria socket
sock = socket.socket() 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

#recebe nome do arquivo ou stop, este último sinaliza uma parada da aplicação
texto = input("Entre com o nome do arquivo. Caso finalizar a aplicação digite stop.\n")

while texto != "stop":
    #envia o input obtido para o servidor
    sock.send(bytes(texto,'utf-8'))

    #espera a resposta do par conectado
    msg = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
    
    #printa a reposta
    print("\nLista das 10 Palavras mais encontradas no arquivo:\t"+str(msg,  encoding='utf-8')+"\n")
    
    #espera novo input
    texto = input("Entre com o nome do arquivo. Caso finalizar a aplicação digite stop.\n")

print("Aplicação Finalizada")
# encerra a conexao
sock.close() 