-- =============================================
-- Dados mock para o dashboard Grafana
-- Simula 7 dias de eventos da cancela
-- =============================================

-- Limpa dados antigos antes de inserir novos
DELETE FROM eventos_cancela;

-- Gera 200 eventos distribuídos nos últimos 7 dias (sem dados no futuro)
INSERT INTO eventos_cancela (timestamp, device_id, distancia, cancela_aberta, tempo_abertura, localizacao)
SELECT
    NOW() - (random() * INTERVAL '7 days'),
    CASE WHEN random() > 0.3 THEN 'esp32-cancela-01' ELSE 'esp32-cancela-02' END,
    ROUND((random() * 90 + 5)::numeric, 2),
    true,
    (3000 + (random() * 5000))::int,
    CASE
        WHEN random() < 0.45 THEN 'Entrada Principal'
        WHEN random() < 0.75 THEN 'Estacionamento B'
        ELSE 'Portão Lateral'
    END
FROM generate_series(1, 200);

-- Adiciona eventos nas últimas 2 horas para dados "ao vivo"
INSERT INTO eventos_cancela (timestamp, device_id, distancia, cancela_aberta, tempo_abertura, localizacao)
SELECT
    NOW() - (random() * INTERVAL '2 hours'),
    'esp32-cancela-01',
    ROUND((random() * 50 + 10)::numeric, 2),
    true,
    5000,
    CASE
        WHEN random() < 0.5 THEN 'Entrada Principal'
        ELSE 'Estacionamento B'
    END
FROM generate_series(1, 30);
