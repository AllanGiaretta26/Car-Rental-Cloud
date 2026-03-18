param(
    [string]$ResourceGroup = "rg-car-rental-demo",
    [string]$Location = "eastus",
    [string]$ContainerAppsEnv = "cae-car-rental-demo",
    [string]$LogAnalyticsWorkspace = "log-car-rental-demo",
    [string]$RedisAppName = "redis-car-rental-demo",
    [string]$ApiAppName = "api-car-rental-demo",
    [string]$PaymentAppName = "payment-car-rental-demo",
    [string]$NotificationAppName = "notification-car-rental-demo",
    [string]$FrontendAppName = "frontend-car-rental-demo",
    [string]$ApiImage = "docker.io/SEU_USUARIO/car-rental-api:latest",
    [string]$PaymentImage = "docker.io/SEU_USUARIO/car-rental-payment:latest",
    [string]$NotificationImage = "docker.io/SEU_USUARIO/car-rental-notification:latest",
    [string]$FrontendImage = "docker.io/SEU_USUARIO/car-rental-frontend:latest",
    [string]$InternalServiceToken = "troque-esta-chave-interna"
)

# ATENCAO:
# Este script cria recursos no Azure e pode gerar custo.
# Revise todos os nomes, imagens e limites antes de executar.
# A recomendacao para custo zero garantido continua sendo a execucao local via Docker.

# Autenticacao no Azure.
az login

# Habilita a extensao necessaria para Azure Container Apps.
az extension add --name containerapp --upgrade

# Garante que os provedores usados pelo script estejam registrados.
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

# Cria o Resource Group.
# Este comando cria um recurso logico no Azure.
az group create `
  --name $ResourceGroup `
  --location $Location

# Cria o Log Analytics Workspace.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
az monitor log-analytics workspace create `
  --resource-group $ResourceGroup `
  --workspace-name $LogAnalyticsWorkspace `
  --location $Location

# Captura os identificadores do workspace para o ambiente do Container Apps.
$LogAnalyticsCustomerId = az monitor log-analytics workspace show `
  --resource-group $ResourceGroup `
  --workspace-name $LogAnalyticsWorkspace `
  --query customerId `
  --output tsv

$LogAnalyticsSharedKey = az monitor log-analytics workspace get-shared-keys `
  --resource-group $ResourceGroup `
  --workspace-name $LogAnalyticsWorkspace `
  --query primarySharedKey `
  --output tsv

# Cria o ambiente do Azure Container Apps.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
az containerapp env create `
  --name $ContainerAppsEnv `
  --resource-group $ResourceGroup `
  --location $Location `
  --logs-workspace-id $LogAnalyticsCustomerId `
  --logs-workspace-key $LogAnalyticsSharedKey

# Cria o Redis como container interno para a fila local simulada.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
az containerapp create `
  --name $RedisAppName `
  --resource-group $ResourceGroup `
  --environment $ContainerAppsEnv `
  --image redis:7-alpine `
  --ingress internal `
  --target-port 6379 `
  --transport tcp `
  --min-replicas 1 `
  --max-replicas 1 `
  --cpu 0.25 `
  --memory 0.5Gi

# Cria a API principal.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
# Observacao: o SQLite fica em /tmp neste modo de demo, entao os dados nao sao persistidos entre reinicios.
az containerapp create `
  --name $ApiAppName `
  --resource-group $ResourceGroup `
  --environment $ContainerAppsEnv `
  --image $ApiImage `
  --ingress external `
  --target-port 8000 `
  --min-replicas 0 `
  --max-replicas 1 `
  --cpu 0.5 `
  --memory 1.0Gi `
  --env-vars `
    APP_ENV=production `
    DATABASE_URL=sqlite:////tmp/rental.db `
    REDIS_URL=redis://$RedisAppName:6379/0 `
    PAYMENT_QUEUE_NAME=payments:pending `
    NOTIFICATION_QUEUE_NAME=notifications:pending `
    INTERNAL_SERVICE_TOKEN=$InternalServiceToken `
    NOTIFICATION_SERVICE_URL=http://$NotificationAppName:8002 `
    CORS_ORIGINS=*

# Cria o servico interno de pagamentos.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
az containerapp create `
  --name $PaymentAppName `
  --resource-group $ResourceGroup `
  --environment $ContainerAppsEnv `
  --image $PaymentImage `
  --ingress internal `
  --target-port 8001 `
  --min-replicas 1 `
  --max-replicas 1 `
  --cpu 0.25 `
  --memory 0.5Gi `
  --env-vars `
    APP_ENV=production `
    REDIS_URL=redis://$RedisAppName:6379/0 `
    PAYMENT_QUEUE_NAME=payments:pending `
    API_INTERNAL_URL=http://$ApiAppName:8000/internal/payments/process-result `
    INTERNAL_SERVICE_TOKEN=$InternalServiceToken `
    SIMULATED_PAYMENT_DELAY_SECONDS=4

# Cria o servico interno de notificacoes.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
az containerapp create `
  --name $NotificationAppName `
  --resource-group $ResourceGroup `
  --environment $ContainerAppsEnv `
  --image $NotificationImage `
  --ingress internal `
  --target-port 8002 `
  --min-replicas 1 `
  --max-replicas 1 `
  --cpu 0.25 `
  --memory 0.5Gi `
  --env-vars `
    APP_ENV=production `
    REDIS_URL=redis://$RedisAppName:6379/0 `
    NOTIFICATION_QUEUE_NAME=notifications:pending

# Cria o front-end publico.
# ESTE COMANDO CRIA RECURSO E PODE GERAR CUSTO BAIXO.
az containerapp create `
  --name $FrontendAppName `
  --resource-group $ResourceGroup `
  --environment $ContainerAppsEnv `
  --image $FrontendImage `
  --ingress external `
  --target-port 80 `
  --min-replicas 0 `
  --max-replicas 1 `
  --cpu 0.25 `
  --memory 0.5Gi

# Exibe as URLs publicas provisionadas ao final.
az containerapp show `
  --name $ApiAppName `
  --resource-group $ResourceGroup `
  --query properties.configuration.ingress.fqdn `
  --output tsv

az containerapp show `
  --name $FrontendAppName `
  --resource-group $ResourceGroup `
  --query properties.configuration.ingress.fqdn `
  --output tsv
