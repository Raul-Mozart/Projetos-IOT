-- =============================================
-- Script de inicialização do TimescaleDB
-- Projeto: Sistema de Cancela Automática
-- =============================================

-- Habilita a extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tabela principal de eventos da cancela
CREATE TABLE IF NOT EXISTS eventos_cancela (
    timestamp     TIMESTAMPTZ    NOT NULL,
    device_id     VARCHAR(50)    NOT NULL,
    distancia     DOUBLE PRECISION NOT NULL,
    cancela_aberta BOOLEAN       NOT NULL,
    tempo_abertura INTEGER       NOT NULL,
    localizacao   VARCHAR(100)   NOT NULL
);

-- Converte a tabela em hypertable do TimescaleDB (particionada por tempo)
SELECT create_hypertable('eventos_cancela', 'timestamp', if_not_exists => TRUE);

-- Índice para consultas por dispositivo
CREATE INDEX IF NOT EXISTS idx_device_id ON eventos_cancela (device_id, timestamp DESC);
