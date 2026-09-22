-- Tablas de auditoría técnica requeridas por 008_suscripciones.sql y por el resto del sistema.
-- Mismo esquema mínimo que usa el pipeline de CI (.github/workflows/CI_CD.yml).
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS auditoria_cambios (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    usuario_bd VARCHAR(255) NOT NULL,
    usuario_app_id INT UNSIGNED NULL,
    ip_app VARCHAR(45) NULL,
    correlacion_id CHAR(36) NULL,
    tabla VARCHAR(64) NOT NULL,
    registro_id BIGINT UNSIGNED NULL,
    operacion VARCHAR(16) NOT NULL,
    datos_anteriores JSON NULL,
    datos_nuevos JSON NULL,
    PRIMARY KEY (id),
    KEY idx_auditoria_cambios_fecha (fecha_evento),
    KEY idx_auditoria_cambios_tabla (tabla, registro_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auditoria_eventos (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    usuario_app_id INT UNSIGNED NULL,
    ip_app VARCHAR(45) NULL,
    correlacion_id CHAR(36) NULL,
    tipo_evento VARCHAR(80) NOT NULL,
    entidad VARCHAR(64) NOT NULL,
    entidad_id BIGINT UNSIGNED NULL,
    detalle JSON NULL,
    PRIMARY KEY (id),
    KEY idx_auditoria_eventos_fecha (fecha_evento),
    KEY idx_auditoria_eventos_entidad (entidad, entidad_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
