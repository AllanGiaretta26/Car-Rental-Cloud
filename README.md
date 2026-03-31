# Car Rental Cloud

Aplicacao simples, funcional e pronta para evolucao, criada para demonstrar um fluxo moderno de aluguel de carros com separacao entre front-end, API principal e servicos de processamento assincrono.

O sistema permite:

- Cadastro de clientes
- Cadastro de veiculos
- Criacao de reservas
- Processamento assincrono de pagamento
- Atualizacao do status da reserva apos pagamento
- Envio de notificacoes simuladas

## Problema que o sistema resolve

Em um sistema de aluguel de carros, o front-end nao deve ficar bloqueado esperando o processamento do pagamento nem misturar regras de cadastro, reserva, pagamento e notificacao em um unico bloco de codigo.

Este projeto resolve isso com:

- API principal para operacoes de negocio e persistencia
- Fila Redis para desacoplar o processamento
- Servico de pagamento consumindo eventos de forma assincrona
- Servico de notificacao reagindo ao resultado final
- Front-end simples para operacao por clientes ou administradores

## Usuarios finais

- Clientes que desejam consultar disponibilidade e realizar reservas
- Administradores que gerenciam frota, clientes e reservas

## Arquitetura da solucao

### Visao geral

```text
Frontend (Nginx + HTML/CSS/JS)
        |
        v
API Principal (FastAPI)
        |
        +--> SQLite
        |
        +--> Redis Queue --------------------+
                                             |
                                             v
                                 Payment Service (FastAPI Worker)
                                             |
                                             v
                         Callback interno para API atualizar reserva
                                             |
                                             v
                                   Redis Queue de notificacoes
                                             |
                                             v
                              Notification Service (FastAPI Worker)
```

### Servicos implementados

#### 1. `frontend`

- Interface web estatica servida por Nginx
- Consome a API por proxy reverso
- Exibe dashboard, formularios, tabelas e notificacoes recentes

#### 2. `api`

- API principal em FastAPI
- Centraliza regras de negocio
- Persiste dados em SQLite
- Publica eventos de pagamento e notificacao no Redis
- Recebe callback interno do servico de pagamento

#### 3. `payment-service`

- Worker FastAPI com loop em background
- Consome a fila Redis de pagamentos
- Simula o processamento de pagamento
- Atualiza a API principal via webhook interno protegido por token

#### 4. `notification-service`

- Worker FastAPI com loop em background
- Consome a fila Redis de notificacoes
- Simula envio de notificacao ao cliente
- Mantem as ultimas notificacoes em memoria para consulta

#### 5. `redis`

- Simula a infraestrutura de mensageria entre servicos
- Mantem desacoplado o fluxo de reserva, pagamento e notificacao

## Fluxo da aplicacao

### Reserva -> Pagamento -> Notificacao

1. O usuario cria uma reserva pelo front-end ou pela API.
2. A API valida cliente, veiculo e datas.
3. A API grava a reserva com status `pending_payment`.
4. A API cria o pagamento com status `pending`.
5. A API marca o veiculo como `reserved`.
6. A API envia um evento para a fila Redis de pagamentos.
7. O `payment-service` consome esse evento e simula o processamento.
8. O `payment-service` chama o endpoint interno da API com o resultado.
9. A API atualiza:
   - pagamento para `paid` ou `failed`
   - reserva para `confirmed` ou `payment_failed`
   - veiculo volta para `available` em caso de falha
10. A API publica um evento na fila de notificacoes.
11. O `notification-service` consome o evento e registra a notificacao simulada.

### Simulacao de falha

O formulario de reserva possui a opcao `Simular falha no pagamento desta reserva`. Quando ela e marcada, o worker de pagamento conclui a reserva com falha, o veiculo volta a ficar disponivel e a notificacao reflete isso.

## Tecnologias utilizadas

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Redis
- Docker
- Docker Compose
- Nginx
- PowerShell
- Azure CLI no script opcional de deploy

## Estrutura do projeto

```text
.
|-- frontend/
|   |-- Dockerfile
|   |-- app.js
|   |-- index.html
|   |-- nginx.conf
|   `-- styles.css
|-- services/
|   |-- api/
|   |   |-- Dockerfile
|   |   |-- requirements.txt
|   |   `-- app/
|   |       |-- api/routes/
|   |       |-- core/
|   |       |-- repositories/
|   |       |-- services/
|   |       |-- db.py
|   |       |-- main.py
|   |       |-- models.py
|   |       `-- schemas.py
|   |-- notification/
|   |   |-- Dockerfile
|   |   |-- requirements.txt
|   |   `-- app/
|   `-- payment/
|       |-- Dockerfile
|       |-- requirements.txt
|       `-- app/
|-- .env.example
|-- .gitignore
|-- README.md
|-- deploy-azure.ps1
|-- docker-compose.yml
`-- setup-local.ps1
```

## Como rodar localmente

### Opcao recomendada: Docker local

Este e o caminho com custo zero garantido de nuvem.

1. Gere o arquivo de ambiente:

```powershell
Copy-Item .env.example .env
```

2. Suba tudo com Docker Compose:

```powershell
docker compose up --build
```

3. Acesse:

- Front-end: `http://localhost:3000`
- API principal: `http://localhost:8000`
- Swagger da API: `http://localhost:8000/docs`
- Health do pagamento: `http://localhost:8001/health`
- Health da notificacao: `http://localhost:8002/health`
- Notificacoes simuladas: `http://localhost:8002/notifications`

### Opcao com script PowerShell

```powershell
.\setup-local.ps1 -Action up
```

Acoes disponiveis:

- `install`: cria `.venv` e instala dependencias locais
- `build`: monta as imagens Docker
- `up`: sobe todos os servicos
- `down`: para os containers
- `logs`: acompanha os logs
- `restart`: reinicia o ambiente completo

## Como cada servico funciona

### API principal

Principais responsabilidades:

- cadastrar clientes
- cadastrar veiculos
- criar reservas
- criar registros de pagamento
- publicar eventos de pagamento
- receber callback interno do worker
- publicar eventos de notificacao
- consolidar dados para o dashboard

Principais endpoints:

- `GET /health`
- `GET /api/customers`
- `POST /api/customers`
- `GET /api/vehicles`
- `POST /api/vehicles`
- `PATCH /api/vehicles/{vehicle_id}/status`
- `GET /api/reservations`
- `POST /api/reservations`
- `GET /api/dashboard/summary`
- `GET /api/notifications/preview`
- `POST /internal/payments/process-result`

### Payment service

- Fica escutando a lista Redis `payments:pending`
- Aguarda alguns segundos para simular processamento
- Envia o resultado para a API principal com `X-Internal-Token`
- Faz reenvio do callback em caso de falha temporaria

### Notification service

- Fica escutando a lista Redis `notifications:pending`
- Registra em memoria as ultimas notificacoes processadas
- Exibe as notificacoes por endpoint HTTP para consulta

### Front-end

- Carrega dashboard com dados agregados
- Permite criar clientes, veiculos e reservas
- Permite atualizar o status administrativo do veiculo
- Atualiza automaticamente o painel a cada 10 segundos

## Variaveis de ambiente

Arquivo base: `.env.example`

Variaveis principais:

- `APP_ENV`: ambiente da aplicacao
- `DATABASE_URL`: string de conexao do banco
- `REDIS_URL`: conexao da fila Redis
- `PAYMENT_QUEUE_NAME`: nome da fila de pagamentos
- `NOTIFICATION_QUEUE_NAME`: nome da fila de notificacoes
- `NOTIFICATION_SERVICE_URL`: URL interna do servico de notificacoes
- `INTERNAL_SERVICE_TOKEN`: token de autenticacao entre servicos
- `CORS_ORIGINS`: origens permitidas no front-end
- `SEED_DEMO_DATA`: popula dados iniciais
- `SIMULATED_PAYMENT_DELAY_SECONDS`: atraso artificial do pagamento

## Banco de dados

Por padrao o projeto usa SQLite, o que reduz custo e simplifica execucao local.

No `docker-compose`, o banco fica em um volume Docker:

- caminho interno: `/data/rental.db`
- persistencia: volume `api_data`

Se desejar evoluir o projeto, o `DATABASE_URL` pode ser trocado por PostgreSQL sem alterar a arquitetura geral.

## Boas praticas aplicadas

- Separacao clara entre front-end, API e workers
- Uso de variaveis de ambiente
- Token interno entre servicos para callback de pagamento
- Camada de repositorio e camada de servico na API
- Persistencia centralizada na API principal
- Fila desacoplando operacoes assincronas
- Seeds de dados para facilitar demonstracao
- Comentarios pontuais apenas onde agregam contexto

## Como adaptar para Azure

O projeto foi pensado para rodar localmente com custo zero e, opcionalmente, ser adaptado para Azure com custo baixo.

### Estrategia usada no script `deploy-azure.ps1`

O script provisiona uma versao demonstrativa com:

- Azure Container Apps para API, pagamento, notificacao e front-end
- Redis em um container app interno para simular a fila
- Log Analytics Workspace para observabilidade minima

### Premissas do script

- As imagens ja devem estar publicadas em um registry acessivel, como Docker Hub ou GHCR
- O script nao faz build local nem push de imagem
- O banco no Azure fica como SQLite em `/tmp`, apenas para demo
- Para persistencia real, o proximo passo natural seria:
  - Azure Files
  - Azure Database for PostgreSQL
  - Azure Service Bus ou Azure Storage Queue no lugar do Redis

### Executando

```powershell
.\deploy-azure.ps1 `
  -ApiImage "docker.io/seuusuario/car-rental-api:latest" `
  -PaymentImage "docker.io/seuusuario/car-rental-payment:latest" `
  -NotificationImage "docker.io/seuusuario/car-rental-notification:latest" `
  -FrontendImage "docker.io/seuusuario/car-rental-frontend:latest" `
  -InternalServiceToken "troque-esta-chave"
```

## Explicacao detalhada de custos

### Caminho com uso gratuito garantido

Use apenas a execucao local com Docker:

- custo de nuvem: zero
- custo Azure: zero
- ideal para avaliacao, estudo, portifolio e demonstracao

Esse e o modo recomendado para cumprir a restricao de nao depender de servicos pagos.

### Caminho Azure opcional e de baixo custo

O script `deploy-azure.ps1` existe para demonstrar como a arquitetura pode ser levada para a nuvem, mas ele nao deve ser tratado como caminho de custo zero garantido.

Recursos que podem gerar custo:

- Azure Container Apps Environment
- Container Apps das aplicacoes
- Log Analytics Workspace

Observacoes importantes:

- A pagina oficial do Azure Container Apps informa existencia de franquia gratuita mensal para consumo.
- A pagina oficial do Azure Monitor informa ingestao gratuita inicial para logs em certos cenarios de billing.
- A pagina oficial de servicos gratuitos do Azure explica que parte dos beneficios depende de conta nova e parte e sempre gratuita.
- Mesmo assim, este projeto de demo usa workers internos e um Redis em execucao continua. Se esses recursos ficarem ativos 24x7, podem ultrapassar a franquia gratuita dependendo da conta e do uso.
- Por isso, a recomendacao pratica e: testar, validar e depois remover os recursos.

### Recomendacao de controle de custo

1. Use Docker local para desenvolvimento e avaliacao.
2. So execute o `deploy-azure.ps1` se realmente quiser demonstrar a topologia em nuvem.
3. Revise a calculadora oficial do Azure antes de provisionar.
4. Ao terminar os testes, remova o Resource Group criado.

### Referencias oficiais de custo

- Azure free services: <https://azure.microsoft.com/en-us/pricing/free-services>
- Azure Container Apps pricing: <https://azure.microsoft.com/en-us/pricing/details/container-apps>
- Azure Monitor pricing: <https://azure.microsoft.com/en-us/pricing/details/monitor>
- Cost management para contas gratuitas: <https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/avoid-charges-free-account>

## Sugestoes de evolucao

- Adicionar autenticacao para administradores
- Trocar SQLite por PostgreSQL
- Substituir Redis local por Azure Service Bus ou Storage Queue
- Persistir notificacoes em banco
- Criar testes automatizados
- Adicionar CI/CD

## Observacoes finais

- O projeto ja nasce com separacao de responsabilidades e com um fluxo assincrono realista.
- O setup local atende ao requisito de baixo custo porque roda 100% em containers locais.
- O deploy Azure foi deixado como caminho opcional, documentado e com alertas explicitos de custo.

## Autor
Desenvolvido por Allan Giaretta.

