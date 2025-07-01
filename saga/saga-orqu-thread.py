import threading
import time

def criar_pedido():
    print("[Pedido] Pedido criado.")
    time.sleep(1)  # Simula tempo de execução

def reservar_estoque():
    print("[Estoque] Estoque reservado.")
    time.sleep(0)

def cobrar_pagamento():
    print("[Pagamento] Falha ao cobrar pagamento.")  # Simula falha
    time.sleep(2)
    raise Exception("Erro ao cobrar pagamento")

def cancelar_pedido():
    print("[Compensação] Pedido cancelado.")

def liberar_estoque():
    print("[Compensação] Estoque liberado.")

def etapa_pagamento():
    try:
        cobrar_pagamento()
    except Exception as e:
        print(f"[Saga] Falha detectada: {e}")
        liberar_estoque()
        cancelar_pedido()

def executar_saga_assincrona():
    print("[Saga] Iniciando saga assíncrona...")

    t1 = threading.Thread(target=criar_pedido)
    t2 = threading.Thread(target=reservar_estoque)
    t3 = threading.Thread(target=etapa_pagamento)

    # Executa as etapas em paralelo (simulando serviços independentes)
    t1.start()
    t2.start()

    # Aguarda pedidos e estoque para iniciar pagamento
    t1.join()
    t2.join()

    t3.start()
    t3.join()

    print("[Saga] Fim do fluxo.")

executar_saga_assincrona()
