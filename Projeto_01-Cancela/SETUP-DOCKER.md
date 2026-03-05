# Configuração do TimescaleDB com Docker

## Pré-requisitos

- Docker e Docker Compose instalados

## Subindo o TimescaleDB

```bash
cd "Projeto_01-Cancela/api"

# Sobe o container (primeira vez cria o banco e executa o init.sql automaticamente)
docker compose up -d
```

O container vai:
1. Criar o banco `cancela_db` com usuário `cancela` e senha `cancela123`
2. Executar o [init.sql](api/init.sql) automaticamente, que cria a extensão TimescaleDB, a tabela `eventos_cancela` como hypertable e os índices

## Verificando se está rodando

```bash
# Status do container
docker compose ps

# Ver logs
docker compose logs -f timescaledb

# Conectar no banco via psql
docker exec -it timescaledb-cancela psql -U cancela -d cancela_db
```

### Comandos úteis no psql

```sql
-- Verificar se a tabela foi criada
\dt

-- Verificar se é hypertable
SELECT * FROM timescaledb_information.hypertables;

-- Ver os eventos salvos
SELECT * FROM eventos_cancela ORDER BY timestamp DESC LIMIT 10;

-- Contagem de eventos por dispositivo
SELECT device_id, COUNT(*) FROM eventos_cancela GROUP BY device_id;
```

## Subindo a API

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a API (porta 3000)
python main.py
```

A API conecta automaticamente no TimescaleDB usando:
```
postgresql://cancela:cancela123@localhost:5432/cancela_db
```

## Parando tudo

```bash
# Para o container (mantém os dados)
docker compose down

# Para e APAGA os dados do volume
docker compose down -v
```

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `postgresql://cancela:cancela123@localhost:5432/cancela_db` | String de conexão com o banco |
| `PORT` | `3000` | Porta da API |
