def comparar_ofertas(ofertas_bd, ofertas_sheet):

    # Indexar por IdOferta
    bd_dict = {int(o["ID_OFERTA_FORMATIVA"]): o for o in ofertas_bd}
    sheet_dict = {int(o["IdOferta"]): o for o in ofertas_sheet}

    cambios = []

    for nombre, sheet_row in sheet_dict.items():

        if nombre not in bd_dict:
            continue  # No existe en BD (no actualizamos aqui)        
        bd_row = bd_dict[nombre]

        if (
            str(bd_row["NOMBRE_OFERTA"]).strip() != str(sheet_row["NombreOferta"]).strip()
            or int(bd_row["HORAS_LECTIVAS"]) != int(sheet_row["Horas"])
            or str(bd_row["NOMBRE_TIPO_OFERTA"]).strip() != str(sheet_row["TipoOferta"]).strip()
            or str(bd_row["NOMBRE_PERIODO"]).strip() != str(sheet_row["Periodo"]).strip()
        ):

            cambios.append(sheet_row)

    return cambios

def separar_resultados(estado_validacion):
    validados = []
    pendientes = []

    for (id_oferta, grupo), datos in estado_validacion.items():

        if datos["estado"] == "VALIDADO":
            validados.append((id_oferta, grupo))
        else:
            pendientes.append((id_oferta, grupo))

    return validados, pendientes