# Simulação de eventos e serviços que reagem
event_queue = []

def publicar_evento(evento):
    event_queue.append(evento)

def servico_pedidos(evento):
    if evento == "INICIAR_PEDIDO":
        print("Serviço de Pedidos: Pedido criado.")
        publicar_evento("PEDIDO_CRIADO")

def servico_estoque(evento):
    if evento == "PEDIDO_CRIADO":
        print("Serviço de Estoque: Estoque reservado.")
        publicar_evento("ESTOQUE_RESERVADO")

def servico_pagamento(evento):
    if evento == "ESTOQUE_RESERVADO":
        print("Serviço de Pagamento: Erro na cobrança!")
        publicar_evento("PAGAMENTO_FALHOU")

def servico_compensacoes(evento):
    if evento == "PAGAMENTO_FALHOU":
        print("Serviço de Compensações: Liberar estoque e cancelar pedido.")

# Loop de processamento de eventos (simples)
publicar_evento("INICIAR_PEDIDO")

while event_queue:
    evento = event_queue.pop(0)
    servico_pedidos(evento)
    servico_estoque(evento)
    servico_pagamento(evento)
    servico_compensacoes(evento)