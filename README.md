# 🚗 Car Rental Cloud

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?logo=dotnet)
![ASP.NET Core](https://img.shields.io/badge/ASP.NET_Core-MVC-512BD4?logo=dotnet)
![Entity Framework](https://img.shields.io/badge/Entity_Framework_Core-10-blue)
![Azure](https://img.shields.io/badge/Azure-App_Service-0089D6?logo=microsoftazure)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap)
![Status](https://img.shields.io/badge/status-concluído-brightgreen)

> Sistema web para gerenciamento de aluguel de veículos, com cadastro de clientes, frota e reservas, autenticação segura via Azure Entra ID e deploy em nuvem no Azure App Service.

🔗 **Demo pausada:** [aluguel-carros-app-efc2fsa5hwabf6et.westus2-01.azurewebsites.net](https://aluguel-carros-app-efc2fsa5hwabf6et.westus2-01.azurewebsites.net/)

---

## Descrição

A **Aplicação de Aluguel de Carros** é um sistema web fullstack desenvolvido com ASP.NET Core MVC e .NET 10. Permite que usuários autenticados gerenciem toda a operação de uma locadora: cadastro de veículos da frota, clientes e reservas com cálculo automático do valor total.

O acesso ao sistema é protegido por autenticação via **Azure Entra ID** (OpenID Connect), garantindo segurança corporativa. Os dados são armazenados em um banco **Azure SQL Database**, e a aplicação está publicada no **Azure App Service**.

---

## Status do Projeto

![Status](https://img.shields.io/badge/status-concluído-brightgreen)

---

## Funcionalidades

- Autenticação e autorização via Azure Entra ID (Microsoft Identity)
- CRUD completo de **Veículos** (marca, modelo, ano, placa, valor da diária, disponibilidade)
- CRUD completo de **Clientes** (nome, e-mail, CPF, telefone)
- Gerenciamento de **Reservas** com datas de início/fim, cálculo de valor total e status
- Interface responsiva com Bootstrap 5
- Proteção de todas as rotas com `[Authorize]`

---

## Tecnologias

| Tecnologia | Versão |
|---|---|
| .NET / ASP.NET Core MVC | 10.0 |
| Entity Framework Core | 10.0.5 |
| Microsoft Identity Web (Azure Entra ID) | 4.8.0 |
| SQL Server / Azure SQL Database | — |
| Bootstrap | 5 |
| Azure App Service | — |

---

## Como Instalar e Rodar

### Pré-requisitos

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)
- SQL Server local ou Azure SQL Database
- Uma aplicação registrada no [Azure Entra ID](https://portal.azure.com) (para autenticação)

### Clonar o repositório

```bash
git clone https://github.com/AllanGiaretta26/Car-Rental-Cloud.git
cd Car-Rental-Cloud
```

### Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp AluguelCarros/appsettings.example.json AluguelCarros/appsettings.json
```

Edite `appsettings.json` com os seus dados (veja a seção [Variáveis de Ambiente](#variáveis-de-ambiente)).

### Aplicar as migrations

```bash
cd AluguelCarros
dotnet ef database update
```

### Rodar a aplicação

```bash
dotnet run
```

Acesse em: `https://localhost:5000`

---

## Variáveis de Ambiente

Configure o arquivo `appsettings.json` com base no exemplo abaixo. **Nunca versione este arquivo com dados reais.**

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=SEU_SERVIDOR;Initial Catalog=SEU_BANCO;User ID=SEU_USUARIO;Password=SUA_SENHA;..."
  },
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "SEU_TENANT_ID",
    "ClientId": "SEU_CLIENT_ID",
    "ClientSecret": "SEU_CLIENT_SECRET",
    "CallbackPath": "/signin-oidc"
  }
}
```

| Variável | Descrição |
|---|---|
| `DefaultConnection` | String de conexão com o banco SQL Server |
| `TenantId` | ID do tenant do Azure Entra ID |
| `ClientId` | ID da aplicação registrada no Azure |
| `ClientSecret` | Segredo da aplicação no Azure |

---

## Deploy

A aplicação está configurada para deploy contínuo no **Azure App Service** via GitHub Actions. O workflow está definido em `.github/workflows/`.

Para realizar o deploy manualmente:

```bash
dotnet publish -c Release -o ./publish
```

---

## Licença

Este projeto está sob a licença [MIT](./LICENSE).

---

Desenvolvido por [Allan Giaretta](https://github.com/AllanGiaretta26).
