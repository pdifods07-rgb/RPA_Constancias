QUERY_S2 = """SELECT DISTINCT 
ID_OFERTA_FORMATIVA, NOMBRE_OFERTA, HORAS_LECTIVAS, NOMBRE_TIPO_OFERTA, NOMBRE_PERIODO FROM tb_pendientes_constancia_2026"""

#ACTUALIZAR VALORES OFERTA FORMATIVA
QUERY_UPDATEOFERTAFORMATIVA = """
    UPDATE tb_pendientes_constancia_2026
    SET 
        NOMBRE_OFERTA = ?,
        HORAS_LECTIVAS = ?,
        NOMBRE_TIPO_OFERTA = ?,
        NOMBRE_PERIODO = ?
WHERE ID_OFERTA_FORMATIVA = ?"""

# ======================================================================
# CONSULTA PARA OBTENER INFORMACIÓN DE LOS PARTICIPANTES, OFERTA Y GRUPO
# ======================================================================
consulta = """
SELECT 
    ID_TIPO_DOCUMENTO AS tipoDocumento,
    USUARIO_DOCUMENTO AS numeroDocumento,
    ID_OFERTA_FORMATIVA,
    NOMBRE_GRUPO
FROM dbo.tb_pendientes_constancia_2026
"""

# ===========================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO AL SUBPROCESO 1, 2 Y 3
# ===========================================================
QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA = """  
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
	id_estado
)
VALUES (
    ?,
    ?,
    ?,
    ?
)
"""

# =====================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO SI CAEN EN ERROR
# =====================================================
QUERY_INSERTAR_ERROR = """  
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
	id_estado,
    id_error
)
VALUES (
    ?,
    ?,
    ?,
    ?,
    ?
)
"""

# ========================================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO DE SUBP2 COMPLETADO (VALIDACIÓN OK)
# ========================================================================
QUERY_INSERT_SUBP2_COMPLETADO = """
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
    id_estado,
    fecha_carga
)
VALUES (?, ?, 2, 3, GETDATE())
"""

# ========================================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO DE SUBP2 ERROR (VALIDACIÓN NOK)
# ========================================================================
QUERY_INSERT_SUBP2_ERROR = """
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
    id_estado,
    id_error,
    fecha_carga
)
VALUES (?, ?, 2, 4, 6, GETDATE())
"""

# ====================================================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO (A PARTIR DE SUBP3 COMPLETADO A SUBP4 PENDIENTE)
# ====================================================================================
QUERY_CREAR_SUBP4_PENDIENTE = """
WITH estado_actual AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY id_oferta, grupo, id_subproceso
               ORDER BY fecha_carga DESC, id_log DESC
           ) rn
    FROM tabla_log
)

INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
    id_estado,
    fecha_carga
)
SELECT 
    s3.id_oferta,
    s3.grupo,
    4,
    1,
    GETDATE()
FROM estado_actual s3
WHERE s3.rn = 1
  AND s3.id_subproceso = 3
  AND s3.id_estado = 3
  AND NOT EXISTS (
        SELECT 1
        FROM estado_actual s4
        WHERE s4.id_oferta = s3.id_oferta
          AND s4.grupo = s3.grupo
          AND s4.id_subproceso = 4
          AND s4.rn = 1
  );
"""

# ======================================================
# OBTENER REGISTROS DE OFERTA Y GRUPO DE SUBP4 PENDIENTE
# ======================================================
QUERY_OBTENER_SUBP4_PENDIENTES = """
WITH estado_actual AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY id_oferta, grupo, id_subproceso
               ORDER BY fecha_carga DESC, id_log DESC
           ) rn
    FROM tabla_log
)

SELECT id_oferta, grupo
FROM estado_actual
WHERE rn = 1
  AND id_subproceso = 4
  AND id_estado = 1;
"""

# ====================================================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO DE SUBP4 PENDIENTE INCLUYENDO NRO_CONSTANCIAS
# ====================================================================================
QUERY_CREAR_SUBP4_EN_EJECUCION = """
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
    id_estado,
    nro_constancias,
    fecha_carga
)
VALUES (?, ?, 4, 2, ?, GETDATE())
"""

# =========================================================
# OBTENER REGISTROS DE OFERTA Y GRUPO DE SUBP4 EN EJECUCION
# =========================================================
QUERY_OBTENER_SUBP4_EN_EJECUCION = """
WITH estado_actual AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY id_oferta, grupo, id_subproceso
               ORDER BY fecha_carga DESC, id_log DESC
           ) rn
    FROM tabla_log
)

SELECT id_oferta, grupo
FROM estado_actual
WHERE rn = 1
  AND id_subproceso = 4
  AND id_estado = 2;
"""

# =====================================================================================
# OBTENER REGISTROS DE OFERTA Y GRUPO DE LA VISTA (NRO_CONSTANCIAS QUE DEBEN GENERARSE)
# =====================================================================================
QUERY_POR_GRUPO_VISTA = """
WITH filtros(id_oferta, grupo) AS (
    SELECT * FROM (VALUES {valores})
    AS v(id_oferta, grupo)
)
SELECT 
    t.ID_OFERTA_FORMATIVA,
    t.NOMBRE_GRUPO,
    COUNT(*) AS numero_constancias
FROM [dbo].[tb_pendientes_constancia_2026] t
INNER JOIN filtros f
    ON t.ID_OFERTA_FORMATIVA = f.id_oferta
   AND t.NOMBRE_GRUPO = f.grupo
GROUP BY 
    t.ID_OFERTA_FORMATIVA,
    t.NOMBRE_GRUPO
"""

# ========================================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO DE SUBP4 COMPLETADO (VALIDACIÓN OK)
# ========================================================================
QUERY_INSERT_SUBP4_COMPLETADO = """
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
    id_estado,
    nro_constancias,
    fecha_carga
)
VALUES (?, ?, 4, 3, ?, GETDATE())
"""

# ==========================================================================
# INSERTAR REGISTROS DE OFERTA Y GRUPO DE SUBP4 PENDIENTE (VALIDACIÓN NO OK)
# ==========================================================================
QUERY_INSERTAR_PENDIENTE = """
INSERT INTO tabla_log (
    id_oferta,
    grupo,
    id_subproceso,
    id_estado,
    fecha_carga
)
VALUES (?, ?, 4, 1, GETDATE());
"""

# ==========================================================================
# OBTENER REGISTROS DE OFERTA Y GRUPO QUE SIGUEN PENDIENTES DE VALIDACIÓN
# ==========================================================================
QUERY_OFERTA_GRUPO_PENDIENTES_VALIDACION = """
WITH grupos_proceso(id_oferta, grupo) AS (
    SELECT * FROM (VALUES {valores}) v(id_oferta, grupo)
),
estado_actual AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY id_oferta, grupo, id_subproceso
               ORDER BY fecha_carga DESC, id_log DESC
           ) rn
    FROM tabla_log
)
SELECT 
    g.id_oferta,
    g.grupo
FROM grupos_proceso g
LEFT JOIN estado_actual e
       ON e.id_oferta = g.id_oferta
      AND e.grupo = g.grupo
      AND e.id_subproceso = 4
      AND e.rn = 1
WHERE e.id_estado IS NULL
   OR e.id_estado <> 3;
"""

# ==========================================================================
# OBTENER REGISTROS DE OFERTA Y GRUPO QUE YA COMPLETARON LA VALIDACIÓN
# ==========================================================================
QUERY_OBTENER_SUBP4_COMPLETADOS = """
WITH estado_actual AS (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY id_oferta, grupo, id_subproceso
               ORDER BY fecha_carga DESC, id_log DESC
           ) rn
    FROM tabla_log
)

SELECT 
    id_oferta,
    grupo
FROM estado_actual
WHERE rn = 1
AND id_subproceso = 4
AND id_estado = 3
"""