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

## 0. Estado del repo (última revisión: 2026-10-13)

**En `main` ahora mismo** (tras el PR #9):

| Archivo | Estado | De quién |
|:--|:--|:--|
| `mazegen/directions.py` | ✅ Terminado (A1) | Ale |
| `mazegen/pattern42.py` | ✅ Terminado (A4) | Ale |
| `mazegen/generator.py` | ✅ Validaciones, 42, backtracker `generate()`, `regenerate()` (A2–A6) | Ale |
| `app/config_parser.py` | ✅ `parse_config()` según contrato | joserome (ajustado por Ale) |
| `mazegen/solver.py` | ✅ `shortest_path()` con BFS | joserome |
| `app/writer.py` | ⬜ Solo docstring → **siguiente de joserome** | joserome |
| `app/display.py` | ⬜ Solo docstring (bloque 2, MLX) | joserome |
| `a_maze_ing.py` | ⬜ Solo shebang + docstring → **S1, juntos** | ambos |
| `configs/` | ❌ No existe | joserome |
| `tests/` | ⬜ Vacío → Ale en `test/maze-checks` (A7) | Ale |

**`make lint` y `mypy --strict` en `main`: ✅ limpios.**

### Comprobado el 2026-10-13

- Cadena completa a mano: `config.txt` → `parse_config` → `MazeGenerator`
  → `generate()` → `shortest_path` ✅ **todo conecta sin tocar nada**.
- Generador: 20×15 con semilla 42 → 280 celdas, 279 pasos (perfecto),
  42 cerrado, misma semilla = mismo laberinto. 200×200 en 0,23 s.
- Solver: 300 laberintos aleatorios → 0 fallos (camino válido y siempre el
  más corto). Sin camino → `ValueError`.
- PRs #8 (Ale) y #9 (joserome) sin conflictos: cada uno en su rama y en
  sus archivos. ✅ El flujo de Git ya funciona.

### Historial de incidentes

- **2026-10-09:** joserome trabajó en su `main` local mientras Ale
  mergeaba → `main` divergió y el push falló. Resuelto con rama + PR #3.
- **2026-10-09:** PR #4 entró con lint en rojo (`pattern42` a medias).
  Resuelto en PR #6 y en el commit `pattern42`.
- **2026-10-09 y 12:** dos commits de Ale directos a `main` sin PR
  (`pattern42` y un commit hecho en `main` por error, movido a rama).

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
| `__init__` | — | Valida y guarda. **No genera.** Lanza `MazeGeneratorError` si algo es inválido (incluida entrada/salida dentro del 42) | ✅ |
| `generate()` | `-> None` | Construye el laberinto perfecto con `self.seed` (backtracker con pila) | ✅ |
| `regenerate()` | `-> None` | Semilla nueva + `generate()`. El display lo usa para "regenerar" | ✅ |
| `grid` | `list[list[int]]` | `grid[y][x]` con bits N1 E2 S4 W8. Vacía hasta `generate()` | ✅ |
| `seed` | `int` | Semilla usada (si no venía, una aleatoria). Nunca `None` | ✅ |
| `pattern_cells` | `set[tuple[int, int]]` | Celdas del 42. **Vacío si no cabe** | ✅ |
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

Antes de empezar, siempre:

```
git switch main
git pull
git switch -c <rama>
git status          ← "On branch <rama>"
```

### Paso 1 — `app/writer.py` (rama `feat/writer`) 🔴 bloquea S1

- `write_maze(path, grid, entry, exit, solution) -> None` según el contrato
  (sección 2.2).
- Formato exacto del subject: una fila por línea en hex **minúscula**,
  línea vacía, `x,y` de entrada, `x,y` de salida, camino. `\n` al final de
  cada línea.
- Si no puede escribir, deja salir el `OSError` (lo captura
  `a_maze_ing.py`).
- **Prueba:** con la rejilla del ejemplo del subject, la salida tiene que
  ser idéntica byte a byte.

### Paso 2 — `configs/` con casos rotos (rama `feat/configs`)

Un archivo por error, cada uno con **un solo** problema:
`missing_key.txt`, `duplicate_key.txt`, `unknown_key.txt`, `width_not_int.txt`,
`empty_key.txt`, `line_without_equal.txt`, `empty.txt`, `perfect_invalid.txt`,
`coords_three_values.txt` → deben dar `ConfigError`.
Y los que pasan el parser pero rechaza el generador: `width_negative.txt`,
`entry_out_of_bounds.txt`, `entry_equals_exit.txt`, `entry_in_42.txt` → deben
dar `MazeGeneratorError`.

### Paso 3 — Cerrar decisiones pendientes de B6

Apuntarlas en la tabla de la sección 6 y en el registro:
- Espacios alrededor del `=`: el parser los acepta (`WIDTH = 20`). ¿Confirmado?
- `OUTPUT_FILE` no escribible: error claro desde `a_maze_ing.py`.

### Paso 4 — Conseguir `maze_analyzer.py`

De los adjuntos del proyecto en la intra. Hace falta para validar en S1.
Decidir si se guarda en el repo o fuera.

### Pendiente de la línea B (bloque 2)

- [ ] Probar que MLX abre una ventana vacía en el campus (30 min, **pronto**:
      es lo que más riesgo tiene)
- [ ] `app/display.py`: display MLX con regenerar, mostrar/ocultar camino y
      colores

### Detalles menores en `solver.py` (cuando se vuelva a tocar)

- El mensaje de error acaba en `.`; los del generador no.
- `(dx, dy) = DELTAS[...]`: los paréntesis sobran.

## 5. Próxima sesión — Ale (línea A)

- [x] **A1** `directions.py`
- [x] **A2** `__init__` con validaciones y `MazeGeneratorError`
- [x] **A3** `_fill_grid` y `_open_wall`
- [x] **A4** `pattern42.py` + entrada/salida fuera del 42
- [x] **A5** backtracker `generate()` (con `_inside`, `_neighbours`,
      `_unvisited_neighbours`)
- [x] **A6** semilla aleatoria y `regenerate()`
- [ ] **A7** tests con pytest en `tests/` (rama `test/maze-checks`):
      bordes cerrados, coherencia entre vecinas, 42 a 15, laberinto perfecto
      (celdas − 1 pasos), misma semilla = mismo laberinto
- [ ] Revisar el PR de `writer.py` de joserome

### Punto de unificación S1 (juntos, cuando esté `writer.py`)

1. Escribir `a_maze_ing.py` (sección 2.3): `sys.argv` → `parse_config` →
   `MazeGenerator` → `generate()` → `shortest_path` → `write_maze`.
   Captura `ConfigError`, `MazeGeneratorError` y `OSError` sin traceback.
   Avisa si el 42 no cabe. Muestra la semilla si no venía en el config.
2. Comprobar:
   - `make run` → `maze.txt` con el 42.
   - `maze_analyzer.py maze.txt` → coherente y perfecto.
   - Todos los `configs/` dan un error claro, sin traceback.
   - Misma `SEED` → mismo `maze.txt`.
   - `make lint` limpio.
3. Planificar el bloque 2: Ale → modo Pac-Man (`perfect=False`);
   joserome → display MLX.

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
| 1 — Núcleo mínimo (hasta S1) | | | En curso: generador, parser y solver listos (2026-10-13); faltan writer y `a_maze_ing.py` |
| 2 — 42 + solver + display | | | |
| 3 — Modo Pac-Man | | | |
| 4 — Interacción | | | |
| 5 — Empaquetado y entrega | | | |
| 6 — Bonus | | | |

### Puntos de sincronización

- [x] **S0** — contrato y repo funcionando → nos separamos
- [ ] **S1** — generador perfecto + parser + solver + writer integrados en
      `a_maze_ing.py`, `maze_analyzer.py` OK
      (2026-10-13: parser → generador → solver ya conectan; falta writer)
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
| 2026-10-12 | `pattern42`: constantes `PATTERN_WIDTH/HEIGHT` y `MIN_WIDTH/HEIGHT` calculadas del dibujo | Ale | Cambiar el dibujo recalcula todo |
| 2026-10-12 | `pattern_cells` se calcula en el `__init__` | Ale | Hace falta para validar entrada/salida |
| 2026-10-13 | `_inside()` reutilizado por `_check_coord` y `_neighbours` | Ale | La condición de límites vive en un solo sitio |
| 2026-10-13 | `generate()` empieza en `entry` y usa `random.Random(self.seed)` propio | Ale | Reproducible sin tocar el `random` global |
| 2026-10-13 | Semilla aleatoria con `random.randrange(2**32)` si `seed is None` | Ale | `seed` siempre es `int`; `seed=0` válido |
| 2026-10-13 | Solver BFS con `deque` y diccionario `previous` | joserome | Camino más corto garantizado |
| | | | |

---

## 9. Retrospectiva (rellenar al final)

- **Qué funcionó bien:**
- **Qué mejoraríamos:**