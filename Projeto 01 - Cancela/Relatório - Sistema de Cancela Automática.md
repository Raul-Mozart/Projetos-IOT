# Relatório - Sistema de Cancela Automática

## Arquitetura Provável - TLDRAW
https://www.tldraw.com/f/xpVVI-Gz455l_6xPOy2wm?d=v32.-325.1751.1001.page

## Diagrama de Fluxo de Dados

       ┌─────────────────────────┐
       │     Sensor HC-SR04      │
       └────────────┬────────────┘
                    │
                    │ (1) Distância em cm (float)
                    ▼
       ┌─────────────────────────┐
       │      (Processo 1)       │
       │  Edge Computing ESP32   │
       │  Leitura/Decisão Local  │
       └────────────┬────────────┘
                    │
                    │ (2) Comando (boolean)
                    ▼
       ┌─────────────────────────┐
       │      (Processo 2)       │
       │  Controle Servo Motor   │
       │   Abertura/Fechamento   │
       └────────────┬────────────┘
                    │
                    │ (3) Conversão para JSON
                    ▼
       ┌─────────────────────────┐
       │      (Processo 3)       │
       │     Envio HTTP POST     │
       └────────────┬────────────┘
                    │
                    │ (4) Requisição HTTP
                    ▼
       ┌─────────────────────────┐
       │      (Processo 4)       │
       │    Validação na API     │
       └────────────┬────────────┘
                    │
                    │ (5) Dado Validado
                    ▼
       ┌─────────────────────────┐
       │      (Processo 5)       │
       │      Persistência       │
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │    [Banco de Dados]     │
       └─────────────────────────┘


---

## API - Exemplo de JSON e Endpoint

### Endpoint:
```bash
POST /api/v1/cancela/eventos
Content-Type: application/json
```

### Body:
```json
{
  "deviceId": "esp32-cancela-01",
  "timestamp": "2026-02-11T19:30:00Z",
  "distancia": 85.5,
  "cancelaAberta": true,
  "tempoAbertura": 5000,
  "localizacao": "Entrada Principal"
}
```

## Identificação de Casos de Edge Computing

Neste projeto, o Edge Computing é implementado diretamente no ESP32, que realiza o processamento local das leituras do sensor HC-SR04 e toma decisões autônomas em tempo real. O microcontrolador analisa continuamente a distância medida e, quando detecta um objeto a menos de 100cm, aciona imediatamente o servo motor para abrir a cancela, sem depender de comunicação com servidores externos. Esta abordagem garante latência mínima e operação contínua mesmo em caso de falha na conexão de rede.

A comunicação com a API ocorre de forma assíncrona e não-bloqueante, apenas para registro histórico e monitoramento, enquanto a lógica crítica de controle permanece no dispositivo. Isso caracteriza um modelo de Edge-Cloud Computing, onde o ESP32 atua como nó inteligente na borda da rede, processando dados localmente, e a nuvem é utilizada para análise de padrões, armazenamento de longo prazo e dashboards de monitoramento.

---

## Relatório Explicando Brevemente

- **Ferramentas usadas**: ESP 32, sensor de movimento HC-SR04, servo motor, cabos macho e fêmea, led, resistor e protoboard.
- **Formato de dados**: JSON
- **Banco de dados**: Postgres
- **Stack API**: Python
- **Plataforma Prototipagem**: Wokwi, pois no TinkerCad não há ESP32