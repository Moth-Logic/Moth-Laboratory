# My First Calculator

Calculadora de escritorio con interfaz gráfica moderna, hecha en Python.
Empieza simple (`+ - * /` con paréntesis) y hoy incluye funciones
científicas completas (trig, log, potencias, hiperbólicas, redondeo),
historial persistente, modo grados/radianes, conversor de bases, tabla
ASCII y notepad. Está diseñada para seguir creciendo — el evaluator ya
fue migrado a C++ vía pybind11 para máximo rendimiento, y el core tiene
suite de tests propia. Próximas entregas van a sumar memoria (M+ / MR)
y más optimizaciones.

---

## Tabla de contenidos

1. [Requisitos previos](#1-requisitos-previos)
2. [Descargar el proyecto](#2-descargar-el-proyecto)
3. [Instalación](#3-instalación)
4. [Uso — correr la app desde código fuente](#4-uso--correr-la-app-desde-código-fuente)
5. [Cómo usar la calculadora](#5-cómo-usar-la-calculadora)
6. [Generar el .exe standalone](#6-generar-el-exe-standalone)
7. [Estructura del proyecto](#7-estructura-del-proyecto)
8. [Solución de problemas](#8-solución-de-problemas)
9. [Tests](#9-tests)
10. [Roadmap](#10-roadmap)

---

## 1. Requisitos previos

Necesitás **Python 3.10 o superior** instalado en Windows.

1. Descargalo de [python.org/downloads](https://www.python.org/downloads/).
2. Al instalar, **marcá la casilla "Add Python to PATH"** en la primera
   pantalla del instalador — si no la marcás, los comandos de abajo no
   van a funcionar desde la terminal.
3. Verificá la instalación abriendo **PowerShell** (o CMD) y corriendo:

   ```powershell
   python --version
   ```

   Deberías ver algo como `Python 3.12.x`. Si el comando no se reconoce,
   reiniciá la terminal (o la PC) después de instalar Python.

---

## 2. Descargar el proyecto

Si lo descargaste como `.zip`: extraelo en cualquier carpeta, por ejemplo
`C:\Users\TuUsuario\Documents\my_first_calculator`.

Si lo vas a manejar como repositorio Git desde el inicio:

```powershell
cd Documents
git init my_first_calculator
cd my_first_calculator
# copiá el contenido del zip acá dentro
git add .
git commit -m "Primera version: calculadora basica con GUI"
```

---

## 3. Instalación

Abrí PowerShell **dentro de la carpeta del proyecto** (click derecho →
"Abrir en Terminal", o `cd` hasta ahí) y corré:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Qué hace cada línea:

- `python -m venv venv` — crea un entorno virtual aislado (una copia
  local de Python solo para este proyecto, para no ensuciar tu Python
  global con dependencias).
- `venv\Scripts\activate` — activa ese entorno. Vas a ver `(venv)` al
  inicio de la línea de la terminal si funcionó.
- `pip install -r requirements.txt` — instala `customtkinter` (la
  librería de la interfaz), `pyinstaller` (para generar el `.exe`),
  y `pybind11` / `setuptools` (para compilar el evaluador C++).

> **Nota:** cada vez que abras una terminal nueva para trabajar en este
> proyecto, tenés que volver a correr `venv\Scripts\activate` primero.

---

## 4. Uso — correr la app desde código fuente

Con el entorno virtual activado (`(venv)` visible en la terminal):

```powershell
python main.py
```

Se abre la ventana de la calculadora. Cerrala como cualquier ventana de
Windows (la X de la esquina) para terminar el programa.

> **Nota sobre el evaluador C++**: la app funciona tanto con el backend
> C++ compilado como con el fallback puro en Python. Si no compilaste
> el `.pyd`, el evaluator usa Python automáticamente. Para compilarlo:
>
> ```powershell
> python setup.py build_ext --inplace
> ```

---

## 5. Cómo usar la calculadora

- **Botones numéricos** (`0`-`9`) y **`.`** para decimales.
- **Operadores**: `+`, `-`, `*`, `/`, `^` (potencia), `%` (módulo).
- **Paréntesis** `(` `)`: para agrupar operaciones, ej. `(2 + 3) * 4`.
- **Notación científica**: `1e6`, `2.5E-3`, `1E+6` se escriben y
  evalúan directamente (y `e` solo sigue siendo la constante de Euler:
  `2 * e` funciona como siempre).
- **Funciones científicas** (botones púrpura):
  - Trigonométricas: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
    (respetan el modo de ángulo — ver "Modo de ángulo" más abajo).
  - Hiperbólicas: `sinh`, `cosh`, `tanh` (trabajan en radianes).
  - Raíces: `√` (raíz cuadrada).
  - Logaritmos: `log` (base 10), `ln` (natural).
  - Redondeo: `ceil`, `floor`, `round`.
  - Otros: `abs` (valor absoluto).
- **Constantes**: `π` (pi), `e` (euler).
- **Modo de ángulo**: el botón `Angle: DEG / RAD` del panel superior
  cambia si las funciones trigonométricas trabajan en **grados** (DEG,
  por defecto) o **radianes** (RAD). El resto de las funciones no cambia.
  Ej.: en DEG, `sin(30)` = `0.5`; en RAD, `sin(pi/2)` = `1`.
- **Historial**: el panel de la derecha guarda las últimas operaciones
  (las más recientes arriba, hasta 100). Click en una entrada para reusar
  su expresión en la pantalla; el botón 🗑 lo limpia. Persiste entre
  sesiones en `~/.everything_app/history.json`.
- **`=`**: evalúa la expresión completa y muestra el resultado.
- **`C`**: borra todo (empezar de cero).
- **`←`**: borra el último carácter escrito.
- **Teclado físico**: todos los botones también funcionan con el
  teclado — números, letras (puedes escribir `sin(30)` a mano),
  `+ - * / ( ) ^ %`, `Enter` (=), `Backspace` (←) y `Esc` (limpia todo).
  Los atajos del teclado solo actúan cuando la pestaña visible es la de
  la calculadora (o la del notepad, para sus atajos), así escribir en
  otra pestaña no afecta a las demás.

**Ejemplos de expresiones válidas:**

| Escribís                     | Resultado |
|------------------------------|-----------|
| `2 + 3 * 4`                  | `14`      |
| `(2 + 3) * 4`                | `20`      |
| `10 / 2 / 5`                 | `1`       |
| `2 * (3 + (4 - 1))`          | `12`      |
| `2^10`                       | `1024`    |
| `sin(30)`                    | `0.5`     |
| `cos(60)`                    | `0.5`     |
| `sqrt(16) + log(100)`        | `6`       |
| `ceil(3.2) * floor(4.8)`     | `16`      |
| `pi * 2`                     | `6.28...` |
| `10 % 3`                     | `1`       |
| `2^3^2`                      | `512`     |
| `1e6 / 1000`                 | `1000`    |

Si escribís algo inválido (ej. `5 / 0` o paréntesis sin cerrar), la
pantalla muestra **el motivo del error** en rojo — ej.
`✗ División entre cero` o `✗ Se esperaba ')'` — y la expresión se
limpia para que corrijas desde cero.

---

## 6. Generar el .exe standalone

Esto empaqueta la app en **un solo archivo `.exe`** que corre en
cualquier PC con Windows, **sin necesidad de tener Python instalado**.
Ideal para compartir el programa con alguien más o entregarlo como
proyecto.

Con el entorno virtual activado:

```powershell
pyinstaller build.spec
```

Al terminar, el ejecutable queda en:

```
dist\MyFirstCalculator.exe
```

Podés mover ese único archivo a cualquier lado (Escritorio, un USB,
otra PC) y correrlo con doble click — no necesita el resto de la
carpeta del proyecto ni Python instalado.

> Este `.spec` ya fue probado (build + arranque de la GUI) antes de
> entregarte el proyecto, así que no debería haber sorpresas. Si algo
> falla, mirá la sección [Solución de problemas](#8-solución-de-problemas).

---

## 7. Estructura del proyecto

```
my_first_calculator/
├── core/                   <- Lógica de cálculo (sin dependencias de GUI)
│   ├── lexer.py             string -> Tokens (incl. notación científica)
│   ├── parser.py            Tokens -> AST (recursive descent, respeta precedencia)
│   ├── evaluator.py         AST -> float  (usa C++ si está compilado, si no Python;
│   │                        incluye el modo de ángulo DEG/RAD)
│   ├── evaluator.cpp        Implementación C++ del evaluator (pybind11)
│   ├── errors.py            CalculatorError — base de todos los errores del core
│   ├── history.py           Historial persistente de operaciones (JSON)
│   ├── calculator.py        Facade: une lexer + parser + evaluator
│   ├── base_converter.py    Conversión DEC/BIN/OCT/HEX (lógica pura)
│   └── ascii_table.py       Tabla ASCII 0-127 + búsqueda (lógica pura)
├── gui/
│   └── app.py                CustomTkinter — solo dibuja, delega todo el cálculo a core.Calculator
├── tests/                    Tests unitarios del core (python -m unittest)
├── setup.py                   Build del evaluador C++ (python setup.py build_ext --inplace)
├── main.py                    Punto de entrada (python main.py)
├── build.spec                 Config de PyInstaller para generar el .exe
├── requirements.txt            Dependencias (customtkinter, pyinstaller, pybind11)
└── README.md                   Este archivo
```

**Por qué está partido así (y no todo en un solo archivo):**

- `core/` no importa nada de `gui/`. El día de mañana se puede escribir
  un CLI, una API web, o correr tests sobre el core sin abrir ninguna
  ventana.
- `evaluator.py` está aislado a propósito: es el punto exacto donde,
  cuando llegue el momento de optimizar, se reemplaza por un módulo
  en C++ compilado con `pybind11`. El AST que produce `parser.py` es
  el "contrato" que cruza esa frontera — el resto del programa no se
  entera del cambio. Esto ya está hecho: `evaluator.cpp` implementa
  toda la lógica en C++ y `evaluator.py` lo usa automáticamente si
  el `.pyd` está compilado, o cae al fallback puro en Python (y en ese
  fallback vive el modo DEG/RAD, que el C++ no conoce).
- El parser es recursive-descent real (no `eval()` de Python), porque
  `eval()` es un riesgo de seguridad y no enseña nada reusable para
  cursos de compiladores o para AXIOMA.

---

## 8. Solución de problemas

**"python no se reconoce como un comando"**
Python no quedó en el PATH. Reinstalalo marcando "Add Python to PATH",
o buscá "Python" en el instalador de Microsoft Store como alternativa.

**`pip install` falla con errores de permisos**
Asegurate de haber activado el entorno virtual (`venv\Scripts\activate`)
antes de instalar — así no necesitás permisos de administrador.

**La ventana no abre / se cierra sola al hacer doble click en el .exe**
Corré el `.exe` desde una terminal (`cmd` o PowerShell) en vez de doble
click, para ver el error real:
```powershell
cd dist
.\MyFirstCalculator.exe
```
Si no muestra nada porque `console=False` en `build.spec`, cambialo
temporalmente a `console=True`, volvé a correr `pyinstaller build.spec`,
y ejecutá de nuevo — ahí vas a ver el traceback completo.

**Antivirus/Windows Defender marca el .exe como sospechoso**
Es un falso positivo común con ejecutables generados por PyInstaller
(el empaquetado se parece, en estructura, al de algunos droppers de
malware, aunque el contenido sea inofensivo). Si pasa, agregá una
excepción para `dist\MyFirstCalculator.exe` en Windows Defender.

---

## 9. Tests

El core (`core/`) tiene una suite de tests con `unittest` — sin
dependencias extra. Desde la raíz del proyecto:

```powershell
python -m unittest        # resumen
python -m unittest -v     # detallado, test por test
```

Los tests cubren lexer, parser, evaluator (incluido el modo DEG/RAD),
conversor de bases, historial y tabla ASCII, y de paso dejan registradas
como regresiones las cosas que se arreglaron en la última revisión:
números malformados que escapaban como `ValueError`, desbordamientos
(`exp(1000)`, `10^400`) que no se convertían en `EvaluationError`, y
negativos que no volvían a parsearse en el conversor de bases.

---

## 10. Roadmap

- [x] Potencias (`^`) — asociativa por la derecha, precedencia sobre `*` y `/`
- [x] Funciones científicas: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `sqrt`, `cbrt`, `log`, `ln`, `abs`, `exp`, `ceil`, `floor`, `round`
- [x] Constantes: `pi`, `e`
- [x] Modo "científica" (filas de botones púrpura)
- [x] Operador módulo (`%`) — misma precedencia que `*` y `/`
- [x] Historial de operaciones — panel lateral, click para reusar, persistente
- [x] Migrar `Evaluator` a C++ vía pybind11 — con fallback a Python si no está compilado
- [x] Modo grados / radianes toggle para funciones trigonométricas
- [x] Notación científica (`1e6`, `2.5E-3`)
- [x] Mensajes de error detallados en la pantalla
- [x] Suite de tests del core (`python -m unittest`)
- [ ] Variables/memoria (`M+`, `M-`, `MR`) — requiere una tabla de símbolos
- [ ] Números complejos / fracciones exactas (`Fraction` en vez de `float`)
