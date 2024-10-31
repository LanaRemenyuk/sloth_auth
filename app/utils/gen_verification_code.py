import random

def generate_verification_code() -> str:
    """Генерация случайного шестизначного кода"""
    return str(random.randint(100000, 999999))