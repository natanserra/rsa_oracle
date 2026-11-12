# RSA Oracle — ataque de maleabilidade multiplicativa (CCA)

Este script quebra um esquema onde um servidor ("oráculo") cifra e decifra
qualquer coisa a pedido, **exceto** o ciphertext exato de uma senha
protegida. A falha explorada é uma propriedade matemática do RSA "puro"
(sem padding robusto): ele é **multiplicativamente homomórfico**.

---

## 1. A ideia por trás do ataque

### A propriedade explorada

No RSA, cifrar é elevar a mensagem a `e` módulo `N`:

```
c = m^e mod N
```

Isso tem uma propriedade matemática importante:

```
(m · x)^e mod N = (m^e mod N) · (x^e mod N) mod N
```

Ou seja: cifrar o **produto** de duas mensagens é o mesmo que multiplicar
os dois ciphertexts (módulo N). Isso é o que chamamos de **maleabilidade**
— um atacante consegue manipular um ciphertext de forma previsível, sem
nunca descobrir a chave privada.

### Como isso quebra o oráculo

O servidor se recusa a decifrar o ciphertext **exato** da senha protegida
(`c_senha`). Mas:

1. Escolhemos um valor conhecido `x` (por exemplo, `97`, o ASCII de `'a'`).
2. Pedimos ao oráculo para **cifrar** `x`, obtendo `cx = x^e mod N`.
3. Calculamos um novo ciphertext:
   ```
   c_novo = (c_senha · cx) mod N
   ```
   Esse número é **diferente** do `c_senha` original, então o oráculo
   aceita decifrá-lo.
4. O oráculo decifra `c_novo` e devolve `(senha · x) mod N` — ou seja, a
   senha original multiplicada por `x`, sem nunca revelar a senha
   diretamente.
5. Como sabemos `x`, basta dividir o resultado por `x` para recuperar a
   senha original.

### Recuperando N (quando o servidor não mostra)

Se o oráculo não informa `N` diretamente, dá para recuperá-lo cifrando
dois valores conhecidos `m1` e `m2` e usando:

```
N = gcd(m1^e - c1, m2^e - c2)
```

Isso funciona porque tanto `m1^e - c1` quanto `m2^e - c2` são múltiplos
exatos de `N` (pela definição de módulo), então o maior divisor comum
entre eles tende a isolar exatamente `N` (às vezes multiplicado por um
pequeno fator, que pode ser removido testando `pow(m1, e, N) == c1`).

---

## 2. Estrutura do código

### `recuperar_N(m1, c1, m2, c2, e=65537)`

Implementa a fórmula do `gcd` descrita acima. Recebe dois pares
(mensagem conhecida, ciphertext correspondente) e devolve o `N` provável.
O `e` default é `65537`, o valor mais comum em implementações RSA reais,
mas pode ser ajustado se o desafio usar outro.

### `calcular_c_novo(c_alvo, cx, N)`

Aplica a propriedade multiplicativa: multiplica o ciphertext protegido
(`c_alvo`, normalmente `c_senha`) pelo ciphertext de um valor conhecido
(`cx`), módulo `N`. O resultado é o valor que deve ser enviado ao oráculo
para decifrar.

### `extrair_mensagem(resultado_decifrado, x)`

Depois que o oráculo decifra `c_novo` e devolve `m · x`, essa função
divide pelo `x` escolhido para isolar a mensagem original `m`, e converte
o resultado em bytes. Inclui uma checagem (`resultado_decifrado % x == 0`)
que ajuda a detectar erros de digitação ou de conversão de formato (hex
vs decimal) antes de seguir adiante.

### `main()`

Um exemplo guiado de como encadear as três funções acima, com comentários
indicando onde preencher os valores obtidos manualmente ao interagir com
o oráculo via `nc`.

---

## 3. Como usar

Esse script **não se conecta sozinho ao servidor** — a parte de interagir
com o oráculo via `nc` é manual, porque o menu e o formato de cada desafio
podem variar. O fluxo é:

1. Conecte no oráculo (`nc host porta`).
2. Cifre dois valores conhecidos (ex: `97` e `98`, ou seus equivalentes
   em texto `'a'` e `'b'`) e anote os ciphertexts devolvidos.
3. Preencha `c1` e `c2` no script e rode `recuperar_N()` para obter `N`
   (pule esse passo se o servidor já informar `N` diretamente).
4. Obtenha o `c_senha` (o número dentro do arquivo de senha cifrada).
5. Preencha tudo no script e rode `calcular_c_novo()`.
6. Volte ao oráculo, peça para **decifrar** o `c_novo` calculado.
7. Pegue o resultado devolvido (convertendo de hex para int se necessário
   com `int(valor, 16)`) e passe para `extrair_mensagem()`.

---

## 4. Limitações e cuidados

- **Depende de o RSA não ter padding robusto** (como OAEP). RSA bem
  implementado adiciona aleatoriedade e estrutura à mensagem antes de
  cifrar, o que quebra a propriedade multiplicativa usada aqui. Esse
  ataque só funciona contra "RSA de livro-texto" (textbook RSA).
- **Formato das respostas do oráculo**: servidores diferentes devolvem
  números em decimal, hexadecimal, ou até como texto ASCII bruto. O
  script assume que você já converteu para `int` antes de passar para as
  funções — confira sempre o formato antes de usar `int(valor, 16)` ou
  `int(valor)`.
- **gcd pode trazer um N com fator extra**: se `recuperar_N()` devolver um
  número maior que o esperado, teste dividir por pequenos primos (2, 3,
  5...) até o tamanho em bits bater com o esperado para o desafio.
