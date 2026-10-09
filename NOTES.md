# A-Maze-ing — Notas y decisiones del equipo

> Documento interno. Aquí apuntamos cada decisión técnica y de organización
> **antes** de programar sobre ella. Si algo del contrato (sección 2) cambia,
> se habla entre los dos y se actualiza aquí primero.
>
> Al final del proyecto, parte de este contenido pasa al README
> (algoritmo y por qué, formato del config, gestión del equipo, planificación).

**Equipo:** alvicent (Ale, GitHub `Alexxvr8`) · joserome (GitHub `Joositoo`)
**Inicio:** 2026-10-07

---

## 0. Estado del repo (última revisión: 2026-10-09)

**En `main` ahora mismo:**

| Archivo | Estado | De quién |
|:--|:--|:--|
| `mazegen/directions.py` | ✅ Terminado (A1) | Ale |
| `mazegen/generator.py` | 🟡 `__init__` + validaciones + `_fill_grid` + `_open_wall` (A2–A3). Falta generar | Ale |
| `app/config_parser.py` | ✅ Ajustado al contrato por Ale en `fix/lint-and-dedupe` (joserome lo revisa, sección 4 paso 2) | joserome |
| `mazegen/pattern42.py` | 🟡 Dibujo hecho, función a medias (rompe el lint). Ale la termina en `fix/lint-and-dedupe` | Ale |
| `mazegen/solver.py` | ⬜ Solo docstring | — |
| `app/writer.py`, `app/display.py` | ⬜ Solo docstring | — |
| `a_maze_ing.py` | ⬜ Solo shebang + docstring | — |
| `configs/` | ❌ No existe | — |

**`make lint` en `main`: ❌ FALLA** (lo arregla Ale en `fix/lint-and-dedupe`)

```
./app/config_parser.py:100:13: E117 over-indented
./mazegen/pattern42.py:12:1: E302 expected 2 blank lines, found 1
./mazegen/pattern42.py:13:15: W292 no newline at end of file
mazegen/pattern42.py:12: error: Missing return statement  [empty-body]
```

**Regla nueva:** nunca se mergea a `main` un PR con `make lint` en rojo ni
con funciones a medias.

### Qué pasó (2026-10-09)

joserome trabajó directamente sobre su copia local de `main` mientras Ale
mergeaba sus PRs. Los dos `main` se separaron y el push falló. Se resolvió
moviendo el trabajo a la rama `feat/config-parse` y mergeando (PR #3). No se
perdió nada. Para que no vuelva a pasar: **reglas de Git de la sección 1**.

---

## 1. Reglas de Git (obligatorias para los dos)

1. **Nunca se trabaja en `main`.** `main` solo cambia con `git pull` y con PRs.
2. **Antes de empezar cualquier cosa:**
   ```
   git switch main
   git pull
   git switch -c <tipo>/<que-vas-a-hacer>
   git status          ← debe decir "On branch <tu rama>"
   ```
3. **Una rama por meta**, corta. Tipos: `feat/` (algo nuevo), `fix/`
   (arreglo), `docs/` (documentación), `test/` (tests).
4. **Antes de cada push:** `make lint` en verde. Sin excepciones.
5. **Mensajes de commit:** `<área>: <qué>` y que describan **ese** commit.
   Ej.: `parser: reject PERFECT values other than true/false`.
   Nada de `Init`, `Init2`, ni repetir el mensaje del commit anterior.
6. **PR → lo revisa el otro → merge.** No mergear tu propio PR sin que el otro
   le haya echado un vistazo (aunque sean 2 minutos).
7. **Después del merge:** borrar la rama (botón "Delete branch" en GitHub, y
   `git branch -d <rama>` en local).
8. **Si `git push` falla con `rejected`:** NO usar `--force`. Avisar al otro.
9. **Si cambia `poetry.lock`** (alguien añadió una dependencia): `make install`.

---

## 2. Contrato entre las dos líneas ✅

Esto es lo que cada parte **recibe y devuelve**. Es lo único que conecta el
trabajo de los dos: mientras se respete, cada uno puede programar sin esperar
al otro.

### 2.1 Lo que Ale entrega a joserome

**`mazegen/directions.py`** (✅ ya en `main`) — constantes compartidas:

| Nombre | Tipo | Contenido |
|:--|:--|:--|
| `NORTH`, `EAST`, `SOUTH`, `WEST` | `int` | `1`, `2`, `4`, `8` |
| `ALL_DIRECTIONS` | `tuple[int, ...]` | `(NORTH, EAST, SOUTH, WEST)`, orden fijo |
| `ALL_WALLS` | `int` | `15` (los 4 muros cerrados) |
| `DELTAS` | `dict[int, tuple[int, int]]` | Dirección → `(dx, dy)`. Norte = `(0, -1)` |
| `OPPOSITE` | `dict[int, int]` | Dirección → su opuesta |
| `LETTERS` | `dict[int, str]` | Dirección → `"N"`, `"E"`, `"S"`, `"W"` |

**`mazegen/generator.py`** — clase `MazeGenerator`:

```python
MazeGenerator(width: int, height: int,
              entry: tuple[int, int], exit: tuple[int, int],
              perfect: bool = True, seed: int | None = None)
```

| Miembro | Tipo | Qué es | Estado |
|:--|:--|:--|:--|
| `__init__` | — | Valida y guarda. **No genera.** Lanza `MazeGeneratorError` si algo es inválido | ✅ (falta validar el 42) |
| `generate()` | `-> None` | Construye el laberinto con `self.seed` | ⬜ A5 |
| `regenerate()` | `-> None` | Semilla nueva + `generate()`. El display lo usa para "regenerar" | ⬜ A6 |
| `grid` | `list[list[int]]` | `grid[y][x]` con bits N1 E2 S4 W8. Vacía hasta `generate()` | ✅ |
| `seed` | `int` | Semilla usada (si no venía, una aleatoria) | 🟡 A6 |
| `pattern_cells` | `set[tuple[int, int]]` | Celdas del 42. **Vacío si no cabe** | ⬜ A4 |
| `width`, `height`, `entry`, `exit`, `perfect` | — | Los parámetros, públicos | ✅ |
| `MazeGeneratorError` | `ValueError` | Excepción del paquete | ✅ |

**`mazegen/pattern42.py`:** `pattern_42_cells(width, height) -> set[tuple[int, int]]`
(vacío si el laberinto es menor que **9×7**). Nunca hace `print`.

### 2.2 Lo que joserome entrega a Ale (y a `a_maze_ing.py`)

**`app/config_parser.py`:**

```python
class ConfigError(Exception): ...

@dataclass
class MazeConfig:
    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None

def parse_config(path: str) -> MazeConfig: ...
```

- **`parse_config(path)` es la ÚNICA función pública** que usará
  `a_maze_ing.py`: lee + valida + devuelve `MazeConfig`. Por dentro puede usar
  `read_config` y `cast_config`.
- Recibe la **ruta**. Leer `sys.argv` **no** es trabajo del parser: va en
  `a_maze_ing.py` (la antigua `get_path()` se ha quitado).
- Valida **solo el formato del archivo**: que se pueda leer, claves
  obligatorias / duplicadas / desconocidas / vacías, tipos (`int`, `x,y`,
  `true`/`false`, `yes`/`no`, `1`/`0`) y `OUTPUT_FILE` no vacío.
- **No valida valores** (tamaño positivo, entrada/salida dentro del
  laberinto, entrada ≠ salida, 42): eso lo hace **solo** el generador, que lo
  necesita igualmente por ser reutilizable. Así no se repite código y los
  mensajes salen de un único sitio. `a_maze_ing.py` captura
  `MazeGeneratorError` igual que `ConfigError`.
- Nombre del campo: el parser usa `exit_` y el generador `exit`. Se queda así;
  `a_maze_ing.py` hace `MazeGenerator(..., exit=config.exit_, ...)`.

**`mazegen/solver.py`:**

```python
def shortest_path(grid: list[list[int]],
                  entry: tuple[int, int],
                  exit: tuple[int, int]) -> str: ...
```

- BFS con `collections.deque`. Devuelve letras, p. ej. `"ESSEN"`.
- Solo cruza donde el bit del muro **no** está activo. Usa `DELTAS`,
  `LETTERS` y `ALL_DIRECTIONS` de `directions.py`.
- Si no hay camino: `ValueError`.
- No importa nada de `app/` (es parte del paquete reutilizable).

**`app/writer.py`:**

```python
def write_maze(path: str, grid: list[list[int]],
               entry: tuple[int, int], exit: tuple[int, int],
               solution: str) -> None: ...
```

- Formato exacto del subject: una fila por línea en hex **minúscula**, línea
  vacía, `x,y` de entrada, `x,y` de salida, camino. `\n` al final de cada línea.
- Si no puede escribir, deja salir el `OSError`.

### 2.3 `a_maze_ing.py` (juntos, en la unificación S1)

`sys.argv` → `parse_config` → `MazeGenerator` → `generate()` →
`shortest_path` → `write_maze`. Captura `ConfigError`, `MazeGeneratorError` y
`OSError` y los muestra **sin traceback**. Si `pattern_cells` está vacío,
avisa. Si la semilla no venía en el config, la muestra.

---

## 3. Reparto ✅

| Línea | Responsable | Piezas |
|:--|:--|:--|
| **A — Motor** (`mazegen/` menos el solver) | **alvicent** | `directions`, `generator`, `pattern42`, backtracker, modo Pac-Man |
| **B — Consumo** | **joserome** | `config_parser`, `configs/`, `solver`, `writer`, display MLX + interacción, tests |
| Juntos | ambos | `a_maze_ing.py`, empaquetado, LICENSE, README, ensayo de defensa |

Cada uno revisa los PRs del otro. En la defensa **los dos** tienen que saber
explicar todo.

---

## 4. Próxima sesión — joserome (línea B) 👈

### Paso 0 — Git (antes de tocar nada)

```
git switch main
git pull
git status
```

Si `git status` dice que tu `main` y el de GitHub han divergido
(`have diverged`), **no hagas nada y avisa a Ale**. Si está limpio, crea la
rama de tu primera tarea (paso 3):

```
git switch -c feat/configs
```

### Paso 1 — Comprobar que `main` está en verde

Después del `git pull`: `make lint` y `poetry run mypy . --strict` → sin
errores. Si falla, avisar a Ale antes de seguir.

### Paso 2 — Revisar los cambios que hizo Ale en `app/config_parser.py`

Para dejar `main` en verde y no repetir código, Ale ha tocado el parser en
`fix/lint-and-dedupe`. **Léelo antes de seguir** (es tu archivo y tienes que
poder defenderlo):

| Cambio | Por qué |
|:--|:--|
| Sangría de la línea 100 (E117) | Rompía `make lint` |
| Quitadas las comprobaciones de tamaño, límites y entrada ≠ salida | Ya las hace el generador (sección 2.2). No volver a añadirlas |
| Nueva `parse_config(path)` | Es la función pública del contrato |
| Quitada `get_path()` | Leer `sys.argv` va en `a_maze_ing.py` (S1) |
| `parse_bool` compara contra dos conjuntos (`TRUE_VALUES`, `FALSE_VALUES`) | Mismos valores que antes (true/false, yes/no, 1/0), sin seis `if` seguidos |
| Clave vacía (`=5`) con error propio | Antes daba `Unknown key: ` vacío |
| `raise ... from error` al leer el archivo | Conserva el error original |
| Claves obligatorias en `sorted(...)` | Mensaje siempre igual si faltan varias |
| Constantes con `Final` | Estilo B7 |
| Docstrings estilo Google | Estilo B7 |

Si no estás de acuerdo con algo, se habla y se apunta en el registro.

### Paso 3 — `configs/` con casos rotos

Un archivo por error, cada uno con **un solo** problema:
`missing_key.txt`, `duplicate_key.txt`, `unknown_key.txt`, `width_not_int.txt`,
`width_negative.txt`, `entry_out_of_bounds.txt`, `entry_equals_exit.txt`,
`line_without_equal.txt`, `empty_key.txt`, `empty.txt`, `perfect_invalid.txt`,
`coords_three_values.txt`.

Comprobar con cada uno:

```
poetry run python -c "from app.config_parser import parse_config; parse_config('configs/<archivo>')"
```

→ debe salir `ConfigError` con un mensaje distinto y claro. Y con `config.txt`,
un `MazeConfig` correcto.

### Paso 4 — Cerrar decisiones pendientes de B6

Apuntar la decisión en la tabla de la sección 5 y en el registro:

- **Espacios alrededor del `=`**: el código ya los acepta (`WIDTH = 20`).
  Confirmar que es lo que queremos.
- **Tamaño mínimo del laberinto** (el del 42 es 9×7, lo lleva Ale).
- **`OUTPUT_FILE` no escribible**: error claro desde `a_maze_ing.py`.

→ **PR `feat/configs` → `main`**, lo revisa Ale.

### Paso 5 — `mazegen/solver.py` (rama nueva `feat/solver`)

- `shortest_path` según el contrato (2.2).
- Probar con rejillas **escritas a mano**, sin esperar al generador:
  2×2, 3×3 con un solo camino, y una con dos caminos de distinta longitud.

### Paso 6 — `app/writer.py` (rama nueva `feat/writer`)

- `write_maze` según el contrato (2.2).
- Probar con el ejemplo del subject: la salida tiene que ser **idéntica byte a
  byte**.

### Pendiente de la línea B (después de lo anterior)

- [ ] Probar que MLX abre una ventana vacía en el campus (30 min, **pronto**:
      es lo que más riesgo tiene)
- [ ] Cambiar el docstring de `app/display.py` ("terminal" → "window")

---

## 5. Próxima sesión — Ale (línea A)

- [ ] **A4** terminar `pattern_42_cells`: medir con `len`, `set()` si no
      cabe (9×7 mínimo), centrar con `//`, set por comprensión → en
      `fix/lint-and-dedupe`, junto con el E117 y la limpieza del parser
- [ ] En `generator.py`: `self.pattern_cells = pattern_42_cells(...)` en el
      `__init__` + error si `entry`/`exit` están en el 42
- [ ] **A5** backtracker con pila (`generate()`), sin entrar en el 42,
      con `random.Random(seed)` → rama `feat/backtracker`
- [ ] **A6** semilla aleatoria si `seed is None` (y guardarla) + `regenerate()`
- [ ] **A7** autocomprobación: bordes cerrados, coherencia entre vecinas,
      celdas del 42 a `15`, misma semilla → misma rejilla
- [ ] `app/display.py`: docstring "terminal" → "window" (MLX)

### Punto de unificación S1

Cuando A5 y los pasos 1–6 de joserome estén en `main`:
juntos escribimos `a_maze_ing.py` (2.3) y comprobamos:
`make run` → `maze.txt` con el 42 · `maze_analyzer.py` dice coherente y
perfecto · todos los `configs/` dan error claro · misma `SEED` → mismo
`maze.txt` · `make lint` limpio.

---

## 6. Decisiones técnicas

### B1. Representación de la rejilla ✅

- `list[list[int]]`, bits N = `1`, E = `2`, S = `4`, W = `8`
- Estado inicial: todos los muros cerrados (`ALL_WALLS` = `15`)
- Constantes en `mazegen/directions.py`
- **Motivo:** coincide bit a bit con el formato hex de salida.

### B2. Sistema de coordenadas ✅

- Externo (config / salida): `(x, y)` → x = columna, y = fila
- Interno: `grid[y][x]` · Origen arriba-izquierda · Norte = `y - 1`

```
      x=0   x=1   x=2
y=0  (0,0) (1,0) (2,0)
y=1  (0,1) (1,1) (2,1)
```

### B3. Contrato ✅ → ver sección 2

### B4. Algoritmo de generación ✅

- **Perfecto:** backtracker (DFS) con **pila explícita**, no recursión
  (límite de ~1000 llamadas de Python)
- **Por qué:** el más fácil de explicar; pasillos largos; sin límite de tamaño
- **Pac-Man (idea):** partir del perfecto y tumbar muros para crear bucles y
  quitar callejones, **sin crear zonas 3×3 abiertas**
- **Bonus:** pendiente (candidato: Kruskal)

### B5. Visualización ✅ MiniLibX

- **Por qué:** `<completar>`
- **Interacciones:** regenerar · mostrar/ocultar camino · rotar colores ·
  `<otras>`
- Pendientes:
  - [ ] Conseguir el paquete Python de MLX (intra) y probarlo en el campus
  - [ ] Cómo lo instala `make install` sin meterlo en las dependencias de
        `mazegen`
  - [ ] `make lint-strict` con el import de MLX
  - [ ] Tamaño de celda en píxeles y tamaño máximo de ventana

### B6. Casos límite

| Caso | Decisión |
|:--|:--|
| Tamaño mínimo del laberinto | ⏳ (joserome, paso 4) |
| Tamaño mínimo para el 42 | **9×7** (dibujo 7×5 + 1 de margen por lado). Si no cabe: se genera sin 42 y se avisa |
| WIDTH / HEIGHT ≤ 0 | **error** (generador) |
| ENTRY o EXIT dentro del 42 | **error** (generador) |
| ENTRY == EXIT | **error** (generador) |
| ENTRY / EXIT fuera de límites | **error** (generador) |
| Clave obligatoria ausente | **error** |
| Clave duplicada | **error** |
| Clave desconocida | **error** |
| Clave vacía (`=5`) | **error** (parser) |
| Espacios alrededor del `=` | ⏳ se aceptan hoy (joserome, paso 4) |
| Valores de PERFECT | `true`/`yes`/`1` → True · `false`/`no`/`0` → False, sin distinguir mayúsculas; otro valor = error |
| SEED ausente | aleatoria y se **muestra** |
| `OUTPUT_FILE` vacío | **error** |
| `OUTPUT_FILE` no escribible | ⏳ error claro, sin traceback |
| Config inexistente / sin argumento | error claro, sin traceback |

**Claves extra:** `SEED` (entero, opcional; si falta, aleatoria y se muestra).

### B7. Estilo común ✅

- Shebang solo en `a_maze_ing.py`
- Docstring de módulo en todos (`"""archivo.py: ..."""`; en `__init__.py`, el
  nombre del paquete)
- Docstrings en inglés, PEP 257, **estilo Google**, también en clases
- Sin comentarios `#` en los `.py`
- Type hints en todas las firmas; Python 3.10+
- Constantes en MAYÚSCULAS con `Final`; auxiliares internas con `_`
- `...` para cuerpos de contrato; `pass` para bloques vacíos ejecutables
- `a_maze_ing.py` con la estructura fija y `=== End of Program ===`
- `mazegen/` y `app/`: sin `main`, sin `if __name__`, sin `print` al importar
- Un único salto de línea al final de cada archivo

---

## 7. Planificación

Plazo de entrega: **por decidir**.

| Fase | Prevista | Real | Notas |
|:--|:--|:--|:--|
| 0 — Acuerdos y entorno | | 2026-10-09 | |
| 1 — Núcleo mínimo (hasta S1) | | | En curso |
| 2 — 42 + solver + display | | | |
| 3 — Modo Pac-Man | | | |
| 4 — Interacción | | | |
| 5 — Empaquetado y entrega | | | |
| 6 — Bonus | | | |

### Puntos de sincronización

- [x] **S0** — contrato y repo funcionando → nos separamos
- [ ] **S1** — generador perfecto + parser + solver + writer integrados en
      `a_maze_ing.py`, `maze_analyzer.py` OK
- [ ] **S2** — 42 + Pac-Man + display MLX con interacción
- [ ] **S3** — paquete `.whl`, LICENSE, README, `lint-strict`, ensayo de defensa

### Herramientas

- Git / GitHub (ramas y PRs), `<editor>`, Poetry, flake8, mypy, pytest,
  build, pdb, MiniLibX
- IA: `<para qué tareas y qué partes>`

---

## 8. Registro de decisiones

| Fecha | Decisión | Quién | Motivo |
|:--|:--|:--|:--|
| 2026-10-07 | Empezamos el proyecto, equipo de 2 | ambos | — |
| 2026-10-08 | Gestor: Poetry; sin `requirements.txt` | ambos | Una sola fuente de dependencias + lockfile |
| 2026-10-08 | `mazegen` sin dependencias; herramientas en grupo `dev` | ambos | Quien reutilice el paquete no se lleva nuestro lint |
| 2026-10-08 | Config de flake8 en `.flake8`, de mypy en `pyproject.toml` | ambos | flake8 no lee `pyproject.toml` |
| 2026-10-09 | Venv dentro del repo con `poetry.toml` | ambos | Mismo entorno para los dos |
| 2026-10-09 | Shebang solo en el punto de entrada | ambos | Los módulos importados no se ejecutan |
| 2026-10-09 | Rejilla `list[list[int]]`, bits N1 E2 S4 W8, `grid[y][x]` | ambos | Coincide con el formato de salida |
| 2026-10-09 | Backtracker DFS con pila | ambos | Fácil de explicar, sin límite de recursión |
| 2026-10-09 | Visualización con MiniLibX | ambos | `<motivo>` |
| 2026-10-09 | Claves duplicadas/desconocidas = error | ambos | Detectar errores de escritura del config |
| 2026-10-09 | SEED opcional; si falta, aleatoria y se muestra | ambos | Reproducibilidad |
| 2026-10-09 | ENTRY/EXIT dentro del 42 = error | ambos | Config inválido, mensaje claro |
| 2026-10-09 | Docstrings Google; licencia MIT | ambos | — |
| 2026-10-09 | Trabajo en GitHub, entrega en vogsphere | ambos | Ramas y PRs para revisarnos |
| 2026-10-09 | Reparto: Ale línea A, joserome línea B | ambos | — |
| 2026-10-09 | Atributos del generador públicos (sin getters) | Ale | Contrato simple; `@property` posible más adelante |
| 2026-10-09 | `ALL_WALLS` calculado en `directions.py` con `\|` | Ale | Un solo sitio para "todos los muros" |
| 2026-10-09 | 42 = dígitos 3×5, mínimo de laberinto 9×7 | Ale | 1 celda de margen para no aislar celdas |
| 2026-10-09 | `MazeConfig.exit_` / `MazeGenerator(exit=...)` | ambos | Se mapea en `a_maze_ing.py` |
| 2026-10-09 | Incidente: trabajo en `main` local → push rechazado; resuelto con rama + PR #3 | ambos | Nueva regla: nunca trabajar en `main` (sección 1) |
| 2026-10-09 | El parser valida solo formato; los valores (tamaño, límites, entrada ≠ salida, 42) solo el generador | Ale (pendiente OK de joserome) | No repetir código; el generador debe validar igualmente por ser reutilizable |
| 2026-10-09 | PERFECT acepta true/false, yes/no y 1/0 (sin distinguir mayúsculas) | ambos | Más tolerante con el usuario; sustituye a "solo true/false" |
| 2026-10-09 | `get_path()` fuera del parser; nueva `parse_config()` | Ale (pendiente OK de joserome) | Cumplir el contrato |
| 2026-10-09 | PR #4 entró en `main` con lint en rojo; se arregla en `fix/lint-and-dedupe` | Ale | Nueva regla: nunca mergear con lint en rojo |
| | | | |

---

## 9. Retrospectiva (rellenar al final)

- **Qué funcionó bien:**
- **Qué mejoraríamos:**