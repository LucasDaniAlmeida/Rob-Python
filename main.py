import os
import sys
import time
import pyautogui
import pandas as pd
from internal import create_excel_file, write_log
from pynput.keyboard import Key, Controller

def get_app_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_base_dir():
    # In PyInstaller onefile, bundled resources are extracted to _MEIPASS.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return get_app_base_dir()


APP_BASE_DIR = get_app_base_dir()
RESOURCE_BASE_DIR = get_resource_base_dir()


def app_path(*parts):
    return os.path.join(APP_BASE_DIR, *parts)


def resource_path(*parts):
    bundled_path = os.path.join(RESOURCE_BASE_DIR, *parts)
    if os.path.exists(bundled_path):
        return bundled_path
    return os.path.join(APP_BASE_DIR, *parts)


file_path = app_path("enviar.xlsx")
if not os.path.exists(file_path):
    print(f"Erro: O arquivo {file_path} não existe.")
    os._exit(1)

# Carregar a planilha
try:
    df = pd.read_excel(file_path, dtype=str, engine="openpyxl")
except Exception as e:
    print(f"Erro ao carregar a planilha: {e}")
    os._exit(1)

# Criar ou carregar o arquivo de log
arquivo_log = create_excel_file()


def carregar_pes_finalizados(arquivo):
    """
    Lê o arquivo de log e retorna os PEs que já foram concluídos com sucesso.
    """
    finalizados = set()

    if arquivo is None:
        return finalizados

    try:
        planilha = arquivo["log"]
        for pe, finalizado, *_ in planilha.iter_rows(min_row=2, values_only=True):
            if pe is None or finalizado is None:
                continue

            if str(finalizado).strip() == "Todos os passos concluídos com sucesso.":
                finalizados.add(str(pe).strip())
    except Exception as e:
        print(f"Erro ao ler o arquivo de log: {e}")

    return finalizados

def localizar_e_clicar(imagem, confidence=0.8, timeout=30, offset_x=0, offset_y=0):
    """
    Localiza uma imagem na tela e clica nela.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            localizacao = pyautogui.locateCenterOnScreen(imagem, confidence=confidence)
            if localizacao:
                pyautogui.click(localizacao.x + offset_x, localizacao.y + offset_y)
                return True
        except Exception:
            pass
    print(f"Ícone {imagem} não encontrado na tela dentro do tempo limite.")
    return False

def localizar_e_clicar_duas_vezes(imagem, confidence=0.8, timeout=30, offset_x=0, offset_y=0):
    """
    Localiza uma imagem na tela e clica duas vezes rapidamente nela.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            localizacao = pyautogui.locateCenterOnScreen(imagem, confidence=confidence)
            if localizacao:
                pyautogui.click(localizacao.x + offset_x, localizacao.y + offset_y, clicks=2)
                return True
        except Exception:
            pass
    print(f"Ícone {imagem} não encontrado na tela dentro do tempo limite.")
    return False    

def executar_passos_para_linha(pe):
    """
    Executa os passos necessários para processar uma linha específica.
    """
    print(f"Iniciando execução para PE: {pe}")

    # Passo 1: Localizar e clicar na imagem 'N_Projeto.png'
    if not localizar_e_clicar(resource_path("Images", "N_Projeto.png"), confidence=0.7):
        return "Falha no Passo 1: Não foi possível localizar a imagem 'N_Projeto.png'."
    print("Passo 1 concluído.")
    time.sleep(0.5)

    # Passo 2: Inserir o valor de PE e clicar no botão de pesquisa
    try:
        pyautogui.write(str(pe))
        time.sleep(1)
        if not localizar_e_clicar(resource_path("Images", "enter.png")):
            return "Falha no Passo 2: Botão de pesquisa não encontrado."
        print("Passo 2 concluído: Informação colada e botão de pesquisa clicado.")
    except Exception as e:
        return f"Falha no Passo 2: {e}"

    # Passo 3: Localizar e clicar no ícone 'tipoGD.png'
    if not localizar_e_clicar(resource_path("Images", "tipoGD.png"), offset_x=-100, offset_y=0):
        return "Falha no Passo 3: Ícone de tipoGD não encontrado."
    print("Passo 3 concluído: Ícone de tipoGD clicado.")

    # Passo 4: Inserir 
    keyboard = Controller()
    keyboard.type("U")
    time.sleep(0.5)
    pyautogui.hotkey("enter")
    print("Passo 4 concluído: UCGD Conectada inserida.")

    time.sleep(3)
    # Passo 5: Localizar e clicar na imagem 'HdeOS.png' - Comentado para ver se dá certo
    #time.sleep(0.5)
    #if not localizar_e_clicar(resource_path("Images", "HdeOS.png")):
    #    print("Falha no Passo 5: Imagem HdeOS.png não encontrada.")
    #else:
    #    print("Passo 5 concluído: Imagem HdeOS.png encontrada e clicada.")
    #   time.sleep(0.5)
    # Passo 6: Localizar e clicar na imagem 'gravarInfos.png'
    if not localizar_e_clicar(resource_path("Images", "gravarInfos.png")):
        print("Falha no Passo 6: Imagem gravarInfos.png não encontrada.")
    else:
        print("Passo 6 concluído: Imagem gravarInfos.png encontrada e clicada.")
        time.sleep(1.5)
    time.sleep(0.5)
    # Passo 7: Lidar com a imagem 'sim.png'
    while True:
        try:
            time.sleep(0.5)
            if pyautogui.locateOnScreen(resource_path("Images", "sim.png"), confidence=0.8):
                localizar_e_clicar(resource_path("Images", "sim.png"))
                print("Passo 7 concluído: Imagem sim.png encontrada e clicada.")
                time.sleep(0.5)
            else:
                print("Imagem sim.png não encontrada, prosseguindo.")
                break
        except pyautogui.ImageNotFoundException:
            print("Imagem sim.png não encontrada, prosseguindo.")
            break

    # Passo 9: Apagar informações
    pyautogui.press("delete")
    pyautogui.press("backspace")
    print("Passo 9 concluído: Botão de Apagar pressionado.")

    return "Todos os passos concluídos com sucesso."

def iniciar_automacao():
    pes_finalizados = carregar_pes_finalizados(arquivo_log)

    for index, row in df.iterrows():
        try:
            pe = str(row["PE"]).strip()  # Certifique-se de que a coluna "PE" existe na planilha

            if pe in pes_finalizados:
                print(f"PE {pe} já foi finalizado com sucesso no log. Execução interrompida.")
                break

            resultado = executar_passos_para_linha(pe)
            print(f"Linha {index + 1}: {resultado}")
            write_log(arquivo_log, {"PE": pe, "FINALIZADO": resultado})

        except KeyError:
            print("Erro: Coluna 'PE' não encontrada na planilha.")
            break
        except Exception as e:
            print(f"Erro inesperado na linha {index + 1}: {e}")
            write_log(arquivo_log, {"PE": row.get("PE", ""), "FINALIZADO": f"Erro inesperado: {e}"})

# Iniciar automação
iniciar_automacao()