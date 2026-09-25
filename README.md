# Automação Robô Status SIATE

## Visão Geral

Esta automação lê uma planilha de entrada (`enviar.xlsx`) contendo uma lista de PEs e executa uma sequência de ações automatizadas na interface do SIATE (via `pyautogui` e `pynput`). Para cada PE, o script tenta localizar imagens na tela, inserir valores, confirmar janelas e gravar um log com o resultado de cada execução.

O projeto contém dois pontos principais de código:
- [main.py](main.py): orquestra a leitura da planilha, execução dos passos e gravação do log.
- [internal/__init__.py](internal/__init__.py): funções utilitárias para criação/escrita do arquivo de log e definição de caminhos.

## O que a automação faz, passo a passo

1. Carrega a planilha `enviar.xlsx` (esperada ao lado do executável ou do script).
2. Cria (ou abre) um arquivo de log em `log/log.xlsx` com a aba `log` e colunas `PE`, `FINALIZADO`, `DATA_HORA`.
3. Lê os PEs já finalizados com sucesso no log para evitar reprocessamento.
4. Para cada PE não-finalizado, executa uma sequência de passos baseada em imagens (localizar e clicar, digitar valores, confirmar diálogos etc.).
5. Registra no log o resultado de cada PE — sucesso ou descrição do erro.

## Requisitos

- Python 3.8+ (recomendado 3.10+)
- Dependências (instalar com `pip`):

```bash
pip install pyautogui pynput pandas openpyxl
```

- Ter a pasta `Images/` com os arquivos de imagem usados para localizar elementos na tela (por exemplo `N_Projeto.png`, `enter.png`, `tipoGD.png`, `HdeOS.png`, `gravarInfos.png`, `sim.png`).
- Deixar `enviar.xlsx` com a coluna `PE` ao lado do executável (ou no diretório do projeto durante desenvolvimento).

## Como rodar em desenvolvimento (VS Code)

1. Abra a pasta do projeto no VS Code.
2. Garanta que `enviar.xlsx` e a pasta `Images/` existam no diretório do projeto.
3. Execute:

```bash
python main.py
```

Observações: rodando em modo script, os caminhos são resolvidos em relação ao diretório do projeto, portanto `enviar.xlsx` e `Images/` devem estar acessíveis a partir daí.

## Estrutura de arquivos (resumo)

- `main.py` — lógica principal (entrada do programa)
- `internal/__init__.py` — funções de log e utilitárias de caminho
- `Images/` — imagens de referência para `pyautogui`
- `enviar.xlsx` — planilha de entrada com coluna `PE`
- `log/log.xlsx` — arquivo de log gerado (criado ao lado do exe em modo empacotado)

## Dicas para usuários

- Sempre feche ou minimize janelas que possam sobrepor os elementos a serem localizados por imagem.
- Use telas com resolução e escala consistentes com as imagens de referência.
- Teste com poucos PEs na planilha antes de rodar em lote grande.

## Dicas para desenvolvedores

- Padrões de caminho:
  - `internal._get_writable_base_dir()` controla onde o `log/` será criado (script vs exe empacotado).
  - `main.resource_path()` tenta `sys._MEIPASS` e depois cai para a pasta do aplicativo.
- Pontos principais de edição:
  - [main.py](main.py): ajuste de imagens, delays (`time.sleep`) e tratamento de exceções.
  - [internal/__init__.py](internal/__init__.py): formato do log, nome da aba e local de armazenamento.

## Troubleshooting (problemas comuns)

- Problema: o log não persiste entre execuções do `.exe`.
  - Causa comum: empacotamento em onefile sem lógica de caminho para persistência.
  - Solução: o código atual já resolve isso — verifique se `main.exe` está gravando `log/log.xlsx` ao lado do exe.

- Problema: imagens não são encontradas quando empacotado.
  - Causa comum: imagens não embutidas e não copiadas para a mesma pasta do exe.
  - Solução: ou empacote com `--add-data "Images;Images"` ou mantenha a pasta `Images` externa ao exe.

## Comandos úteis

Gerar exe (sem embutir imagens):

```powershell
pyinstaller --onefile main.py
```

Gerar exe (embutindo a pasta Images):

```powershell
pyinstaller --onefile --add-data "Images;Images" main.py
```

Reusar o spec gerado:

```powershell
pyinstaller main.spec
```