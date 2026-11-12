#!/usr/bin/env python3
"""
RSA Oracle: servidor que cifra e decifra qualquer coisa, exceto o
ciphertext exato da senha protegida. Exploramos a propriedade
multiplicativa do RSA: (m * x)^e mod N = (m^e mod N) * (x^e mod N) mod N.

Passo a passo:
    1. Use a funcao recuperar_N() com dois pares (mensagem, cifrado)
       obtidos cifrando valores conhecidos no oraculo, para descobrir N
       (caso o servidor nao mostre N diretamente).
    2. Cifre um valor conhecido x (ex: 97, o ASCII de 'a') no oraculo
       para obter cx = x^e mod N.
    3. Use calcular_c_novo() para disfarcar o ciphertext da senha.
    4. Mande c_novo para o oraculo decifrar.
    5. Use extrair_mensagem() no resultado para recuperar a senha original.

Este script nao se conecta sozinho ao oraculo (a interacao via `nc` e
manual); ele so faz os calculos. Preencha os valores medida que forem
obtidos na sessao com o servidor.
"""
from math import gcd


def recuperar_N(m1, c1, m2, c2, e=65537):
    """
    Recupera o modulo N a partir de dois pares (mensagem, cifrado)
    conhecidos, usando o fato de que tanto m1^e - c1 quanto m2^e - c2
    sao multiplos de N.
    """
    N = gcd(pow(m1, e) - c1, pow(m2, e) - c2)
    return N


def calcular_c_novo(c_alvo, cx, N):
    """
    Disfarca o ciphertext protegido (c_alvo) multiplicando por um
    ciphertext conhecido (cx = x^e mod N), de forma que o resultado
    seja diferente do ciphertext original e o oraculo aceite decifrar.
    """
    return (c_alvo * cx) % N


def extrair_mensagem(resultado_decifrado, x):
    """
    O oraculo devolve m*x (nao m). Divide por x para obter a mensagem
    original. resultado_decifrado pode ser passado como int ja
    convertido (ex: int(hex_str, 16)).
    """
    if resultado_decifrado % x != 0:
        raise ValueError(
            "resultado nao divisivel por x - confira se c_novo, cx e N "
            "estao corretos"
        )
    m = resultado_decifrado // x
    return m.to_bytes((m.bit_length() + 7) // 8, "big")


def main():
    # ── Exemplo de uso; preencha com os valores reais da sessao ──
    e = 65537
    m1, c1 = 97, 0   # TODO: cifrado de 'a' (97) obtido no oraculo
    m2, c2 = 98, 0   # TODO: cifrado de 'b' (98) obtido no oraculo

    if c1 == 0 or c2 == 0:
        raise SystemExit(
            "Preencha c1 e c2 (cifrados de 'a' e 'b') antes de rodar, "
            "ou pule recuperar_N() se ja tiver o N."
        )

    N = recuperar_N(m1, c1, m2, c2, e)
    print("N candidato:", N)
    print("bits:", N.bit_length())
    print("confere a:", pow(m1, e, N) == c1)
    print("confere b:", pow(m2, e, N) == c2)

    c_senha = 0   # TODO: numero dentro de password.enc
    cx = c1       # reusa o cifrado de 'a' como x=97 conhecido
    x = 97

    if c_senha == 0:
        raise SystemExit("Preencha c_senha (valor de password.enc) antes de continuar.")

    c_novo = calcular_c_novo(c_senha, cx, N)
    print()
    print("Mande este valor para o oraculo decifrar:")
    print(c_novo)

    print()
    print("Depois de decifrar no oraculo, preencha 'resultado_hex' abaixo")
    print("e rode novamente so a parte de extracao, ou use extrair_mensagem()")
    print("diretamente no interpretador interativo.")


if __name__ == "__main__":
    main()