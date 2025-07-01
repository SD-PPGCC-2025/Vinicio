def criar_pedido():
    print("Pedido criado.")
    return True

def reservar_estoque():
    print("Estoque reservado.")
    return True

def cobrar_pagamento():
    print("Falha ao cobrar pagamento.")  # Simulando falha
    return False

def cancelar_pedido():
    print("Pedido cancelado.")

def liberar_estoque():
    print("Estoque liberado.")

def executar_saga():
    try:
        if not criar_pedido():
            raise Exception("Erro ao criar pedido")

        if not reservar_estoque():
            raise Exception("Erro ao reservar estoque")

        if not cobrar_pagamento():
            raise Exception("Erro ao cobrar pagamento")

        print("Saga concluída com sucesso.")
    
    except Exception as e:
        print(f"Saga falhou: {e}")
        liberar_estoque()
        cancelar_pedido()

executar_saga()
