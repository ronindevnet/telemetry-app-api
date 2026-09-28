# API de Telemetria

Este projeto é uma API REST para coleta de telemetria de jogo. Ele recebe os
dados de cada **partida** (sessão de jogo) e o **uso de armas** durante a
partida, validando e armazenando tudo em um banco SQLite através do SQLAlchemy.

A estrutura segue o material didático da disciplina **Desenvolvimento Full Stack
Básico**. O código é escrito em inglês. O modelo tem três tabelas:

- `Match` (partida): jogador, duração, valor gasto e data de registro da sessão
  de jogo.
- `Weapon` (catálogo de armas): apenas `id` e `name`. As armas são cadastradas
  automaticamente pelo `POST /session` quando a Unity envia uma arma nova. Os
  nomes cadastrados aqui são os mesmos utilizados pela Unity durante o jogo.
- `WeaponUsage` (uso de arma): tabela de junção entre partida e arma, com as
  estatísticas de cada arma usada na partida (tiros, precisão e recargas). A
  chave primária é composta por `(match_id, weapon_id)`.

### Tipos de dados

- `duration`: **inteiro**, duração total da partida em **segundos**. O front-end
  exibe formatado como `HH:mm:ss`.
- `money_spent`: **inteiro**, valor gasto em **reais inteiros** (sem centavos). O
  front-end exibe formatado como moeda brasileira (`R$`).
- `accuracy` (por arma): número entre `0` e `1`; `shots_fired` e `reloads` são
  inteiros não negativos.
- `insertion_date`: data e hora em que a partida foi registrada, preenchida
  automaticamente pela API e retornada em ISO 8601 (`2026-09-27T14:03:12`). O
  front-end exibe como `dd/mm/aaaa hh:mm`.

---
## Como executar

### Pré-requisitos

- [Python 3](https://www.python.org/downloads/) instalado e disponível no terminal.

### Atalho no Windows: `run.bat` e `stop.bat`

Para simplificar, este diretório tem dois atalhos que substituem os passos 2 a 4
abaixo. Basta dar um duplo-clique:

| Arquivo | O que faz |
|---|---|
| `run.bat` | Na primeira execução, cria o ambiente virtual (`.venv`) e instala as dependências do `requirements.txt`. Em seguida, sobe a API em uma janela própria em `http://127.0.0.1:5000` e abre a documentação Swagger no navegador. |
| `stop.bat` | Encerra o servidor, finalizando o processo que estiver escutando na porta `5000`. |

> Também é possível parar a API fechando a janela **Telemetria API** aberta pelo
> `run.bat`. Em outros sistemas operacionais, siga o passo a passo abaixo.

### 1. Acessar o diretório do projeto

Após clonar o repositório, abra um terminal no diretório raiz (`telemetry_app_api`).
Todos os comandos abaixo são executados a partir dele.

### 2. Criar e ativar o ambiente virtual

É fortemente indicado o uso de um ambiente virtual, para que as dependências
fiquem isoladas do Python do sistema.

```
python -m venv .venv
```

Ative o ambiente virtual:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Linux/macOS:** `source .venv/bin/activate`

Com o ambiente ativo, o terminal passa a exibir `(.venv)` no início da linha.

### 3. Instalar as dependências

```
(.venv)$ pip install -r requirements.txt
```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

### 4. Executar a API

Para executar a API basta executar:

```
(.venv)$ flask run --host 0.0.0.0 --port 5000
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte.

```
(.venv)$ flask run --host 0.0.0.0 --port 5000 --reload
```

> O comando `flask` só existe com o ambiente virtual **ativado**. Se aparecer
> `flask : The term 'flask' is not recognized...`, o venv não está ativo. Nesse
> caso, chame o interpretador do venv diretamente (não precisa ativar):
>
> ```
> .venv\Scripts\python.exe app.py
> ```

Abra o [http://localhost:5000/](http://localhost:5000/) no navegador para
acessar a documentação da API (Swagger, Redoc ou RapiDoc).

> O banco de dados (`database/db.sqlite3`) é criado automaticamente na primeira
> execução da API.

---
## Rotas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Redireciona para a documentação (Swagger/Redoc/RapiDoc) |
| GET | `/health` | Verifica se a API está online (`{"status":"ok"}`) |
| POST | `/match` | Adiciona uma nova partida (form) |
| GET | `/matches` | Lista todas as partidas cadastradas |
| GET | `/match` | Busca uma partida pelo `id` (partida + armas utilizadas) |
| DELETE | `/match` | Remove uma partida pelo `id` |
| DELETE | `/matches` | Remove todas as partidas (e seus usos de arma) |
| GET | `/weapons` | Lista o catálogo de armas (cadastradas sob demanda pelo `POST /session`) |
| DELETE | `/weapons` | Limpa o catálogo e remove todos os usos de arma |
| POST | `/usage` | Registra o uso de uma arma (do catálogo) em uma partida (form) |
| POST | `/session` | Registra uma sessão completa (partida + armas) em uma única requisição JSON — usado pela Unity |

### Sessão completa (endpoint da Unity)

`POST /session` recebe a partida inteira em um único corpo JSON e cria a partida
e todos os usos de arma de forma atômica (tudo ou nada). Armas que ainda não
existem no catálogo são adicionadas automaticamente. As armas são identificadas
pelo nome.

```json
{
  "player": "ana",
  "duration": 1110,
  "money_spent": 13,
  "weapons": [
    { "weapon": "Rifle",    "shots_fired": 80, "accuracy": 0.62, "reloads": 4 },
    { "weapon": "Escopeta", "shots_fired": 40, "accuracy": 0.35, "reloads": 2 }
  ]
}
```

Obs: `duration` é em segundos inteiros, e `money_spent` é em reais inteiros. O front-end vai apresentar os dados com a formatação adequada.

---
## Catálogo de armas

Não há rota específica para cadastrar armas: elas entram no catálogo **sob
demanda**, pelo `POST /session`. Sempre que a Unity (ou o botão *Simular sessão
da Unity* do front-end) envia uma arma que ainda não existe, ela é cadastrada
automaticamente. A busca pelo nome ignora maiúsculas/minúsculas.

Se quiser popular o catálogo antes de qualquer sessão (por exemplo, para usar o
formulário de *Adicionar arma* do front-end com o banco vazio), execute a partir
do diretório `telemetry_app_api`, com a API já executada ao menos uma vez:

```
(.venv)$ python -c "from model import Session, Weapon; s=Session(); s.add_all([Weapon(name='Escopeta'), Weapon(name='Rifle'), Weapon(name='Carabina'), Weapon(name='Pistola'), Weapon(name='Sniper')]); s.commit()"
```
