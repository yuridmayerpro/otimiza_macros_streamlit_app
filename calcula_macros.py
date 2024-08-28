def calcula_tmb(peso, idade, sexo):
    '''
    Cálculo da taxa metabólica basal
    Fórmula de Harris-Benedict
    '''
    if sexo == 'm':
        tmb = 88.362 + (13.397 * peso) + (4.799 * idade) - (5.677 * idade)
    elif sexo == 'f':
        tmb = 447.593 + (9.247 * peso) + (3.098 * idade) - (4.330 * idade)
    else:
        raise ValueError("O sexo deve ser 'm' ou 'f'")
    return tmb

def calcula_metas_macronutrientes1(peso, idade, sexo, objetivo):
    '''
    Método de Mifflin-St Jeor
    '''
    tmb = calcula_tmb(peso, idade, sexo)

    if objetivo == 'hipertrofia':
        calorias_alvo = (1.2 * tmb) + 500
        proteina_percentual = 0.3
        carboidrato_percentual = 0.5
        gordura_percentual = 0.2
    else:
        raise ValueError("Objetivo não suportado")

    calorias_proteina = calorias_alvo * proteina_percentual
    calorias_carboidrato = calorias_alvo * carboidrato_percentual
    calorias_gordura = calorias_alvo * gordura_percentual

    gramas_proteina = calorias_proteina / 4
    gramas_carboidrato = calorias_carboidrato / 4
    gramas_gordura = calorias_gordura / 9

    return calorias_alvo, gramas_proteina, gramas_carboidrato, gramas_gordura

def calcula_metas_macronutrientes2(peso, idade, objetivo):
    '''
    Método de Katch-McArdle
    '''
    constante = 370 if objetivo == 'hipertrofia' else 0
    tmb = constante + (21.6 * (peso * (1 - 0.01 * 0)))  # Ajuste a gordura corporal se conhecida

    proteina_percentual = 0.3
    carboidrato_percentual = 0.5
    gordura_percentual = 0.2

    calorias_alvo = tmb * 1.2

    calorias_proteina = calorias_alvo * proteina_percentual
    calorias_carboidrato = calorias_alvo * carboidrato_percentual
    calorias_gordura = calorias_alvo * gordura_percentual

    gramas_proteina = calorias_proteina / 4
    gramas_carboidrato = calorias_carboidrato / 4
    gramas_gordura = calorias_gordura / 9

    return calorias_alvo, gramas_proteina, gramas_carboidrato, gramas_gordura

def calcula_metas_macronutrientes3(peso, idade, sexo, objetivo):
    '''
    Método de Harris-Benedict
    '''
    tmb = calcula_tmb(peso, idade, sexo)

    if objetivo == 'hipertrofia':
        fator_atividade = 1.55
    else:
        raise ValueError("Objetivo não suportado")

    calorias_alvo = tmb * fator_atividade

    proteina_percentual = 0.3
    carboidrato_percentual = 0.5
    gordura_percentual = 0.2

    calorias_proteina = calorias_alvo * proteina_percentual
    calorias_carboidrato = calorias_alvo * carboidrato_percentual
    calorias_gordura = calorias_alvo * gordura_percentual

    gramas_proteina = calorias_proteina / 4
    gramas_carboidrato = calorias_carboidrato / 4
    gramas_gordura = calorias_gordura / 9

    return calorias_alvo, gramas_proteina, gramas_carboidrato, gramas_gordura
