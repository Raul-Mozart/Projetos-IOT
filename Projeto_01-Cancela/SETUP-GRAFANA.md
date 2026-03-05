# Dashboard Grafana - Sistema de Cancela Automática

## Subindo o Grafana + TimescaleDB

```bash
cd "Projeto_01-Cancela/api"
docker compose up -d
```

Isso sobe dois containers:
- **TimescaleDB** na porta `5432`
- **Grafana** na porta `3001`

## Acessando o Grafana

```
URL: http://localhost:3001
Usuário: admin
Senha: admin
```

> No GitHub Codespace, a porta `3001` será encaminhada automaticamente. Acesse pela aba **Ports**.

## Populando com Dados Mock

Para ver o dashboard preenchido, rode o script de dados mock:

```bash
docker exec -i timescaledb-cancela psql -U cancela -d cancela_db < mock_data.sql
```

## Dashboard

O dashboard **"Sistema de Cancela Automática - IoT Dashboard"** já é carregado automaticamente como home page.

### Painéis incluídos

| # | Painel | Tipo | O que mostra |
|---|--------|------|-------------|
| 1 | **Total de Aberturas** | Stat | Quantidade total de aberturas no período selecionado |
| 2 | **Distância Média** | Gauge | Distância média dos objetos detectados (cm) |
| 3 | **Último Evento** | Stat | Data/hora do evento mais recente |
| 4 | **Dispositivos Ativos** | Stat | Quantidade de ESP32 que enviaram dados nas últimas 24h |
| 5 | **Aberturas ao Longo do Tempo** | Time Series (barras) | Histograma temporal de aberturas da cancela |
| 6 | **Distância ao Longo do Tempo** | Time Series (linha) | Evolução da distância medida pelo sensor, com linha de threshold em 100cm |
| 7 | **Aberturas por Localização** | Pie Chart (donut) | Distribuição proporcional por local (Entrada Principal, Estacionamento B, etc.) |
| 8 | **Aberturas por Hora do Dia** | Bar Chart | Em quais horários a cancela é mais utilizada |
| 9 | **Últimos Eventos** | Tabela | Lista dos 20 eventos mais recentes com status colorido |

### Filtro de Tempo

Use o seletor de tempo no canto superior direito do Grafana:
- **Last 7 days** (padrão) — mostra todos os dados mock
- **Last 24 hours** — dados recentes
- **Last 1 hour** — dados "ao vivo"

O dashboard tem **auto-refresh de 10 segundos**.

---

## Queries SQL usadas

### Total de Aberturas
```sql
SELECT COUNT(*) AS "Total Aberturas"
FROM eventos_cancela
WHERE cancela_aberta = true
  AND $__timeFilter("timestamp");
```

### Distância Média
```sql
SELECT AVG(distancia) AS "Distância Média"
FROM eventos_cancela
WHERE $__timeFilter("timestamp");
```

### Último Evento
```sql
SELECT TO_CHAR(
  MAX("timestamp") AT TIME ZONE 'America/Sao_Paulo',
  'DD/MM/YYYY HH24:MI:SS'
) AS "Último Evento"
FROM eventos_cancela;
```

### Dispositivos Ativos (24h)
```sql
SELECT COUNT(DISTINCT device_id) AS "Dispositivos"
FROM eventos_cancela
WHERE "timestamp" > NOW() - INTERVAL '24 hours';
```

### Aberturas ao Longo do Tempo
```sql
SELECT
  $__timeGroupAlias("timestamp", $__interval) AS time,
  COUNT(*) AS "Aberturas"
FROM eventos_cancela
WHERE $__timeFilter("timestamp")
  AND cancela_aberta = true
GROUP BY 1
ORDER BY 1;
```

### Distância ao Longo do Tempo
```sql
SELECT
  "timestamp" AS time,
  distancia AS "Distância",
  device_id
FROM eventos_cancela
WHERE $__timeFilter("timestamp")
ORDER BY 1;
```

### Aberturas por Localização
```sql
SELECT
  localizacao AS "Localização",
  COUNT(*) AS "Aberturas"
FROM eventos_cancela
WHERE $__timeFilter("timestamp")
  AND cancela_aberta = true
GROUP BY localizacao
ORDER BY 2 DESC;
```

### Aberturas por Hora do Dia
```sql
SELECT
  EXTRACT(HOUR FROM "timestamp" AT TIME ZONE 'America/Sao_Paulo')::text || 'h' AS "Hora",
  COUNT(*) AS "Aberturas"
FROM eventos_cancela
WHERE $__timeFilter("timestamp")
  AND cancela_aberta = true
GROUP BY 1
ORDER BY EXTRACT(HOUR FROM "timestamp" AT TIME ZONE 'America/Sao_Paulo');
```

### Últimos Eventos (Tabela)
```sql
SELECT
  TO_CHAR("timestamp" AT TIME ZONE 'America/Sao_Paulo', 'DD/MM/YYYY HH24:MI:SS') AS "Data/Hora",
  device_id AS "Dispositivo",
  ROUND(distancia::numeric, 2) AS "Distância (cm)",
  cancela_aberta::text AS "Status",
  localizacao AS "Localização"
FROM eventos_cancela
ORDER BY "timestamp" DESC
LIMIT 20;
```

---

## Estrutura de Arquivos do Grafana

```
api/
├── docker-compose.yml
├── mock_data.sql
└── grafana/
    ├── dashboards/
    │   └── cancela-dashboard.json    ← Dashboard provisionado
    └── provisioning/
        ├── dashboards/
        │   └── dashboards.yml        ← Config de provisioning
        └── datasources/
            └── timescaledb.yml       ← Datasource automático
```

## Parando tudo

```bash
docker compose down       # mantém dados
docker compose down -v    # apaga dados dos volumes
```
