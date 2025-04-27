import random
import re
from sympy import sympify

def roll_simple_dice(dice_string):
    # Validar formato usando expressão regular. Só números positivos, sem zeros à esquerda
    match = re.fullmatch(r'([1-9]\d*)d([1-9]\d*)', dice_string.strip())
    if not match:
        raise ValueError(f"Formato inválido: {dice_string}. Use o formato 'XdY' sem zeros a esquerda ou números negativos, ex: '3d6'.")
    
    x, y = map(int, match.groups())
    resultados = [random.randint(1, y) for _ in range(x)]
    return sum(resultados)

def calculate_dice_expression(expression):
    """Calcula a expressão numérica com dados (ex.: '3d8 + 3', '1d10 + 3d6', etc.)."""
    
    # Regex para encontrar expressões de dados (ex: '2d6', '3d8')
    dice_matches = re.findall(r'\d+d\d+', expression)
    rolls = []
    # Substituir cada rolagem de dado pela soma dos resultados dos dados
    for dice_expr in dice_matches:
        roll_result = roll_simple_dice(dice_expr)
        rolls.append(roll_result)
        expression = expression.replace(dice_expr, str(roll_result), 1)
    
    # Agora a expressão está pronta para ser calculada, usamos sympify para isso
    try:
        total_result = sympify(expression)
        return total_result, rolls
    except Exception as e:
        raise ValueError(f"Erro ao calcular a expressão: {e}")
    
def roll_with_advantage_or_disadvantage(expression, advantage=True):
    """Rola a expressão com vantagem (maior valor) ou desvantagem (menor valor), 
    e retorna também os valores das rolagens."""
    
    # Rolando duas vezes a expressão
    result1, _ = calculate_dice_expression(expression)
    result2, _ = calculate_dice_expression(expression)
    
    if advantage:
        final_result = max(result1, result2)
    else:
        final_result = min(result1, result2)

    return {
        "result": final_result,
        "rolls": [result1, result2]
    }

def calculate_initiative(people_str, initiative_dice_expression="1d20"):
    """Calcula a iniciativa dos participantes, ordenando-os com base no valor final da rolagem + bônus."""
    
    # Separar as pessoas e bônus de iniciativa
    people = people_str.split("/")
    initiatives = []
    
    for person in people:
        parts = person.split(",")
        
        name = parts[0]
        bonus = int(parts[1]) if len(parts) > 1 else 0  # Se o bônus não existir, é 0
        
        # Rola o dado de iniciativa
        roll_result, _ = calculate_dice_expression(initiative_dice_expression)
        
        # Soma o bônus ao valor da rolagem
        total_initiative = roll_result + bonus
        
        # Adiciona o resultado à lista de iniciativas
        initiatives.append((name, total_initiative, roll_result))
    
    # Ordenar as iniciativas pela soma do dado + bônus (total_initiative)
    initiatives_sorted = sorted(initiatives, key=lambda x: x[1], reverse=True)
    
    # Retornar a lista ordenada apenas com nome e valor final da iniciativa
    return [(name, total_initiative) for name, total_initiative, _ in initiatives_sorted]


if __name__ == "__main__":
    # Testando rolagem simples
    print("roll_simple_dice:", roll_simple_dice("3d8"))
    print("roll_simple_dice:", roll_simple_dice("3d8"))
    print("roll_simple_dice:", roll_simple_dice("1d10"))
    print("roll_simple_dice:", roll_simple_dice("5d6"))
    print("roll_simple_dice:", roll_simple_dice("1d100"))
    print("roll_simple_dice:", roll_simple_dice("1000d1000"))


    # Testando o método com expressões
    print("calculate_dice_expression:", calculate_dice_expression("3d8 + 3"))
    print("calculate_dice_expression:", calculate_dice_expression("1d10 + 3d6"))
    print("calculate_dice_expression:", calculate_dice_expression("(1d10 + 5d8) * (5d10)^5"))

    resultado_vantagem = roll_with_advantage_or_disadvantage("3d8 + 3", advantage=True)
    print("Vantagem:", resultado_vantagem)

    resultado_desvantagem = roll_with_advantage_or_disadvantage("3d8 + 3", advantage=False)
    print("Desvantagem:", resultado_desvantagem)

    # Testando o método
    resultados_iniciativa = calculate_initiative("Jack,4/Alice,3/Johnattan/Boss,9", "1d20")
    print(resultados_iniciativa)