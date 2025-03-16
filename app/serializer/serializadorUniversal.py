class SerializadorUniversal():

    def serializar_lista(datos, campos_requeridos):
        if datos:
            return [
                {campo: getattr(dato, campo) for campo in campos_requeridos}
                for dato in datos
            ]
        return None
    
    def serializar_unico(dato, campos_requeridos):
        if dato:
            return {campo: getattr(dato, campo) for campo in campos_requeridos}
        return None