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

consulta = """
SELECT 
    ID_TIPO_DOCUMENTO AS tipoDocumento,
    USUARIO_DOCUMENTO AS numeroDocumento,
    ID_OFERTA_FORMATIVA,
    NOMBRE_GRUPO
FROM dbo.tb_pendientes_constancia_2026
"""

#QUERY PARA OBTENER EL NÚMERO DE CONSTANCIAS A GENERAR SEGÚN APROBADOS POR OFERTA Y GRUPO (VISTA)
QUERY_POR_GRUPO_VISTA = """
        SELECT ID_OFERTA_FORMATIVA as id_oferta, NOMBRE_GRUPO as grupo, count(*) as numero_constancias from [dbo].[tb_pendientes_constancia_2026]
        group by ID_OFERTA_FORMATIVA, NOMBRE_GRUPO
    """

#QUERY PARA OBTENER EL NÚMERO DE CONSTANCIAS GENERÁNDOSE SEGÚN APROBADOS POR OFERTA Y GRUPO (TABLA)
QUERY_POR_GRUPO_TABLA = """
        select id_oferta as id_oferta, grupo as grupo, numero_constancias as numero_constancias from oferta_constancias
    """