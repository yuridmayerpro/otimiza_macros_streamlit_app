import pandas as pd
import numpy as np
import optuna

def objective(trial, Energia_kcal_100g, Proteina_g_100g, Carbohidratos_g_100g, id_intervalos, calorias_alvo, gramas_proteina, gramas_carboidrato):
    id_values = {id: trial.suggest_int(f'id_{id}', interval[0], interval[1]) for id, interval in id_intervalos.items()}

    lista_valores_gramas = np.array(list(id_values.values()))
    calorias_total = np.sum((Energia_kcal_100g * lista_valores_gramas) / 100)
    proteinas_total = np.sum((Proteina_g_100g * lista_valores_gramas) / 100)
    carboidratos_total = np.sum((Carbohidratos_g_100g * lista_valores_gramas) / 100)

    calorias_total_desvio = abs(calorias_total - calorias_alvo)
    proteinas_total_desvio = abs(proteinas_total - gramas_proteina)
    carboidratos_total_desvio = abs(carboidratos_total - gramas_carboidrato)

    return calorias_total_desvio + proteinas_total_desvio + carboidratos_total_desvio

def early_stopping_callback(study, trial):
    if study.best_value is not None and study.best_value < 0.9:
        study.stop()

def otimiza(alimentos, peso, idade, sexo, objetivo, calorias_add, proteina_add, carboidrato_add, n_trials, df_taco):
    alimentos_selecionados = list(alimentos.keys())
    intervalos = list(alimentos.values())
    order_dict = {alimento: index for index, alimento in enumerate(alimentos_selecionados)}

    df_ = df_taco[df_taco.Alimento.isin(alimentos_selecionados)].copy()
    df_['order'] = df_['Alimento'].map(order_dict)
    df_ = df_.sort_values('order')

    alimentos_selecionados_IDs = df_.ID_Alimento.values.tolist()
    id_intervalos = {id: intervalos[i] for i, id in enumerate(alimentos_selecionados_IDs)}

    Energia_kcal_100g = df_.Energia_kcal_100g.values
    Proteina_g_100g = df_.Proteina_g_100g.values
    Carbohidratos_g_100g = df_.Carbohidratos_g_100g.values

    calorias_alvo1, gramas_proteina1, gramas_carboidrato1, gramas_gordura1 = calcula_metas_macronutrientes1(peso, idade, sexo, objetivo)
    calorias_alvo2, gramas_proteina2, gramas_carboidrato2, gramas_gordura2 = calcula_metas_macronutrientes2(peso, idade, objetivo)
    calorias_alvo3, gramas_proteina3, gramas_carboidrato3, gramas_gordura3 = calcula_metas_macronutrientes3(peso, idade, sexo, objetivo)

    calorias_alvo = int(round(np.average([calorias_alvo1, calorias_alvo2, calorias_alvo3]), 0))
    gramas_proteina = int(round(np.average([gramas_proteina1, gramas_proteina2, gramas_proteina3]), 0))
    gramas_carboidrato = int(round(np.average([gramas_carboidrato1, gramas_carboidrato2, gramas_carboidrato3]), 0))

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    study = optuna.create_study(direction='minimize')
    study.optimize(lambda trial: objective(trial, Energia_kcal_100g, Proteina_g_100g, Carbohidratos_g_100g, id_intervalos, calorias_alvo, gramas_proteina, gramas_carboidrato), n_trials=n_trials, n_jobs=-1, show_progress_bar=True)

    best_params = study.best_params
    best_validity = study.best_value

    lista_valores_gramas = list(best_params.values())
    calorias_ = (Energia_kcal_100g * lista_valores_gramas) / 100
    proteinas_ = (Proteina_g_100g * lista_valores_gramas) / 100
    carboidratos_ = (Carbohidratos_g_100g * lista_valores_gramas) / 100

    df_final = pd.DataFrame({
        'ID_Alimento': df_['ID_Alimento'].astype(str),
        'Alimento': df_['Alimento'],
        'massa': best_params.values(),
        'calorias': calorias_,
        'proteinas': proteinas_,
        'carboidratos': carboidratos_
    })

    return study, best_params, best_validity, calorias_alvo, gramas_proteina, gramas_carboidrato, df_final
