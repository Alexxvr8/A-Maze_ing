# A-Maze-ing — Notas y decisiones del equipo

> Documento interno. Aquí apuntamos cada decisión técnica y de organización
> **antes** de programar sobre ella. Si algo del contrato (sección 2) cambia,
> se habla entre los dos y se actualiza aquí primero.
>
> Al final del proyecto, parte de este contenido pasa al README
> (algoritmo y por qué, formato del config, gestión del equipo, planificación).

**Equipo:** alvicent (Ale, GitHub `Alexxvr8`) · joserome (GitHub `Joositoo`)
**Inicio:** 2026-10-07
**Objetivo:** proyecto **perfecto** → obligatoria completa + **los 3 bonus**

---

## 0. Estado del repo (última revisión: 2026-10-16)

**En `main` ahora mismo** (tras el PR #15):

| Archivo | Estado | De quién |
|:--|:--|:--|
| `mazegen/directions.py` | ✅ Terminado | Ale |
| `mazegen/pattern42.py` | ✅ Terminado | Ale |
| `mazegen/generator.py` | ✅ Perfecto (backtracker) + Pac-Man (trenzado) | Ale |
| `mazegen/solver.py` | ✅ `shortest_path()` con BFS | joserome |
| `mazegen/__init__.py` | ✅ API pública con `__all__` | Ale |
| `app/config_parser.py` | ✅ `parse_config()` según contrato | joserome (ajustado por Ale) |
| `app/writer.py` | ✅ Formato del subject (validado con `maze_analyzer.py`) | joserome |
| `app/display.py` | 🟡 MLX hecho: muros, entrada, salida, 42, camino, teclas R/P/C/ESC. **Rompe el lint** y aún sin probar en pantalla | joserome |
| `configs/` | ✅ 12 configs con errores | joserome |
| `tests/test_generator.py` | ✅ 76 tests (perfecto + Pac-Man) | Ale |
| `a_maze_ing.py` | ⬜ Solo shebang + docstring → **S1, juntos, lo más urgente** | ambos |

**Calidad en `main`:**
- pytest: ✅ 76 passed
- `make lint`: ❌ **falla por `app/display.py`** (2 de flake8 + 1 de mypy, ver
  sección 4, paso 1)
- `make lint-strict`: ❌ además `Cannot find module "mlx"`

### Comprobado el 2026-10-15 con `maze_analyzer.py`

240 laberintos (20×15, 9×7, 21×15, 10×10, 40×30, 5×5 · 2 modos · 20
semillas), generados con generador + solver + writer:
- `PERFECT=True` → 120/120 *"PERFECT maze: a single path, no loop"*.
- `PERFECT=False` con `--max-dead-ends 0` → 120/120 *"Pac-Man-USABLE … no
  real dead-end → bonus-grade (perfectly braided)"*.
- Muros coherentes, nada inalcanzable, esquinas y centro alcanzables.
- Los 3 callejones que deja el dibujo del 42 (huecos del "4" y del "2") el
  analizador los cuenta como **"enclosed by the '42' (tolerated)"** → **no hay
  que rediseñar el 42.**

### ⚠️ Fallo encontrado el 2026-10-16 (Ale, tarea A10)

En laberintos **pequeños** el modo Pac-Man a veces queda con **0 callejones
pero 1 solo bucle** (un anillo), y el subject pide al menos 2.

| Tamaño | Semillas que fallan (de 300) |
|:--|:--|
| 3×4 / 4×3 / 4×4 | 33 / 18 / 13 |
| 5×4, 6×4, 4×5, 6×6… | 1–4 |
| 7×7 o mayor (incl. 20×15) | 0 (salvo algún caso suelto en 8×4) |

Causa: el trenzado solo quita callejones, no garantiza bucles. Los tests no lo
vieron porque `test_pacman_has_loops` solo prueba 20×15.

### Historial de incidentes

- **2026-10-09:** joserome trabajó en su `main` local mientras Ale
  mergeaba → `main` divergió y el push falló. Resuelto con rama + PR #3.
- **2026-10-09:** PR #4 entró con lint en rojo (`pattern42` a medias).
  Resuelto en PR #6.
- **2026-10-09 y 12:** dos commits de Ale directos a `main` sin PR.
- **2026-10-16:** PR #15 (MLX) entró con `make lint` en rojo. Se arregla en
  el paso 1 de joserome.

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
4. **Antes de cada push y de cada merge:** `make lint` y los tests en verde.
   **Sin excepciones.**
5. **Mensajes de commit:** `<tipo>(<área>): <qué>` y que describan **ese**
   commit. Ej.: `feat(mazegen): braided Pac-Man mode for PERFECT=False`.
6. **PR → merge con los dos delante.** Trabajamos juntos en persona, así que el
   merge lo hace uno con el otro al lado revisándolo (no hace falta proteger
   `main` en GitHub).
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

**`mazegen/directions.py`** — constantes compartidas:

| Nombre | Tipo | Contenido |
|:--|:--|:--|
| `NORTH`, `EAST`, `SOUTH`, `WEST` | `int` | `1`, `2`, `4`, `8` |
| `ALL_DIRECTIONS` | `tuple[int, ...]` | `(NORTH, EAST, SOUTH, WEST)`, orden fijo |
| `ALL_WALLS` | `int` | `15` (los 4 muros cerrados) |
| `DELTAS` | `dict[int, tuple[int, int]]` | Dirección → `(dx, dy)`. Norte = `(0, -1)` |
| `OPPOSITE` | `dict[int, int]` | Dirección → su opuesta |
| `LETTERS` | `dict[int, str]` | Dirección → `"N"`, `"E"`, `"S"`, `"W"` |

**API pública del paquete** (`from mazegen import ...`): `MazeGenerator`,
`MazeGeneratorError`, `shortest_path`, `NORTH`, `EAST`, `SOUTH`, `WEST`.

**`mazegen/generator.py`** — clase `MazeGenerator`:

```python
MazeGenerator(width: int, height: int,
              entry: tuple[int, int], exit: tuple[int, int],
              perfect: bool = True, seed: int | None = None,
              algorithm: str = "backtracker")        ← algorithm: PENDIENTE (A11)
```

| Miembro | Tipo | Qué es | Estado |
|:--|:--|:--|:--|
| `__init__` | — | Valida y guarda. **No genera.** Lanza `MazeGeneratorError` si algo es inválido | ✅ |
| `generate()` | `-> None` | Construye con `self.seed`: perfecto con el algoritmo elegido y, si `perfect` es `False`, trenzado (0 callejones reales, ≥ 2 bucles, sin zonas 3×3) | ✅ (falta A10 y A11) |
| `regenerate()` | `-> None` | Semilla nueva + `generate()` | ✅ |
| `grid` | `list[list[int]]` | `grid[y][x]` con bits N1 E2 S4 W8. Vacía hasta `generate()` | ✅ |
| `seed` | `int` | Semilla usada. Nunca `None` | ✅ |
| `pattern_cells` | `set[tuple[int, int]]` | Celdas del 42. **Vacío si no cabe** | ✅ |
| `steps` | `list[tuple[tuple[int, int], int]]` | Muros abiertos durante `generate()`, en orden: `(celda, dirección)`. Para la animación | ⏳ A12 |
| `width`, `height`, `entry`, `exit`, `perfect` | — | Los parámetros, públicos | ✅ |
| `MazeGeneratorError` | `ValueError` | Excepción del paquete | ✅ |

**Contrato de la animación (decidido 2026-10-16):**
- El generador **no sabe nada de MLX**. Solo rellena `self.steps` durante
  `generate()` (se vacía al principio de cada `generate()`).
- Cada paso es un muro que se abre y **se queda abierto**: los intentos que el
  trenzado deshace (`_close_wall`) **no** se guardan.
- Vale igual para backtracker, Kruskal y trenzado.
- El display "reproduce" la lista: parte de la rejilla con todos los muros
  cerrados y abre unos cuantos pasos por fotograma con `mlx_loop_hook`.
- Se lanza con la **tecla `A`**.

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
    algorithm: str          ← PENDIENTE (paso 5 de joserome)

def parse_config(path: str) -> MazeConfig: ...
```

- **`parse_config(path)` es la ÚNICA función pública** que usa
  `a_maze_ing.py`.
- Recibe la **ruta**. Leer `sys.argv` va en `a_maze_ing.py`.
- Valida **solo el formato**: lectura, claves obligatorias / duplicadas /
  desconocidas / vacías, tipos y `OUTPUT_FILE` no vacío.
- **No valida valores** (tamaño, límites, entrada ≠ salida, 42, tamaño mínimo
  del Pac-Man): eso lo hace **solo** el generador.
- `exit_` en el parser, `exit` en el generador; se mapea en `a_maze_ing.py`.
- **`ALGORITHM`** (decidido 2026-10-16): opcional, por defecto
  `"backtracker"`; acepta `backtracker` o `kruskal` sin distinguir mayúsculas
  y lo devuelve en minúscula. Otro valor → `ConfigError`.

**`mazegen/solver.py`:** `shortest_path(grid, entry, exit) -> str`. BFS con
`deque`, devuelve letras (`"ESSEN"`), `ValueError` si no hay camino. No
importa nada de `app/`.

**`app/writer.py`:** `write_maze(path, grid, entry, exit, solution) -> None`.
Formato exacto del subject, hex en minúscula, `\n` en cada línea. Deja salir
el `OSError`.

**`app/display.py`:** clase `Display`.
- **Decidido 2026-10-16:** recibe el `MazeGenerator` **ya generado**; su
  `__init__` **no** llama a `generate()`.
- `run()` abre la ventana y bucle de eventos. Teclas: `R` regenera, `P`
  camino, `C` color de muros, `A` animación (pendiente), `ESC`/X salir.

### 2.3 `a_maze_ing.py` (juntos, S1)

`sys.argv` → `parse_config` → `MazeGenerator(..., exit=config.exit_,
algorithm=config.algorithm)` → `generate()` → `shortest_path` →
`write_maze` → `Display(generator).run()`.
- Captura `ConfigError`, `MazeGeneratorError` y `OSError` (incluido
  `OUTPUT_FILE` no escribible) y los muestra **sin traceback**.
- Si `pattern_cells` está vacío, avisa por consola (lo pide el subject).
- Si la semilla no venía en el config, la muestra.

---

## 3. Reparto ✅

| Línea | Responsable | Piezas |
|:--|:--|:--|
| **A — Motor** (`mazegen/` menos el solver) | **alvicent** | `directions`, `generator`, `pattern42`, backtracker, Pac-Man, Kruskal, pasos de animación, tests del motor |
| **B — Consumo** | **joserome** | `config_parser`, `configs/`, `solver`, `writer`, display MLX + interacción + animación en pantalla |
| Juntos | ambos | `a_maze_ing.py`, empaquetado, LICENSE, README, ensayo de defensa |

En la defensa **los dos** tienen que saber explicar todo.

---

## 4. Próximas sesiones — joserome (línea B)

### Paso 1 — Dejar `main` en verde 🔴 (rama `fix/display-lint`)

- `app/display.py:56` W293: línea en blanco con espacios.
- `app/display.py:118` E125: sangría de la firma de `_fill_rect`.
- mypy: `to_bytes(..., self.byte_order)` → anotar `byte_order` como
  `Literal["little", "big"]`.
- Docstring de la clase `Display`.

### Paso 2 — Instalar MLX como las demás librerías (rama `feat/mlx-install`)

- **Decidido 2026-10-16:** MLX se instala con Poetry, igual que el resto
  (`make install` → `poetry install`).
- ⚠️ **Trampa:** `mlx` en PyPI es **otra librería** (la de Apple para IA).
  Hay que apuntar al `.whl` de MiniLibX de la intra, como dependencia por
  **ruta** (`path = "..."`), guardando el `.whl` en el repo (p. ej. `vendor/`).
- Va en un **grupo de Poetry** (p. ej. `display`), **no** en
  `[project] dependencies`: `mazegen` tiene que poder reutilizarse sin MLX.
- `mypy --strict`: si sigue sin encontrar tipos de `mlx`, añadir en
  `pyproject.toml` un `[[tool.mypy.overrides]]` con `module = "mlx"` e
  `ignore_missing_imports = true` (sin comentarios `#` en el código).
- Documentarlo en el README.

### Paso 3 — `Display` recibe el laberinto ya generado

Quitar el `generator.generate()` del `__init__` (lo hace `a_maze_ing.py`).

### Paso 4 — Probar en un ordenador del campus

En cuanto exista `a_maze_ing.py`: ventana, teclas, tamaños grandes y
pequeños.

### Paso 5 — Clave `ALGORITHM` en el parser

Según el contrato (sección 2.2) + un config de error `algorithm_invalid.txt`.

### Paso 6 — Bonus: animación en pantalla (tecla `A`)

Cuando Ale tenga `steps` (A12): reproducirlos con `mlx_loop_hook`.

### Retoques menores

- [ ] `configs/entry_out_of_bounds.txt` rompe la **salida**: renombrar o
      romper la `ENTRY`.
- [ ] `configs/entry_in_42.txt` (estaba en la lista y no existe).
- [ ] `writer.py`: `format(n, "x")` en vez del `match` (opcional).
- [ ] `solver.py`: quitar el punto final del mensaje y los paréntesis de
      `(dx, dy)`.
- [ ] (Opcional) Tecla para cambiar el color del 42.

---

## 5. Próximas sesiones — Ale (línea A)

- [x] **A1–A6** motor perfecto (directions, validaciones, muros, 42,
      backtracker, semilla)
- [x] **A7** tests del motor perfecto
- [x] **A8** modo Pac-Man (trenzado sin zonas 3×3)
- [x] **A9** backtracker en su propio método `_backtracker(rng)`
- [x] Tests del Pac-Man (conectividad, bucles, callejones, 3×3, esquinas y
      centro, semilla) → 76 tests
- [x] Validado con `maze_analyzer.py` → bonus de 0 callejones ✅
- [ ] **A10** 🔴 **Garantizar ≥ 2 bucles en Pac-Man:** función nueva que,
      tras el trenzado, abra muros extra (con "probar y deshacer", sin zonas
      3×3) hasta que `pasos − (celdas − 1) ≥ 2`. Más:
      - error si `PERFECT=False` y el tamaño es menor que **3×3**;
      - tests con tamaños pequeños (3×3 a 6×6) y muchas semillas.
- [ ] **A11** Bonus: **Kruskal** + parámetro `algorithm` (por defecto
      `"backtracker"`; desconocido → `MazeGeneratorError`). Los tests que ya
      hay, con los dos algoritmos (`parametrize`).
- [ ] **A12** Bonus: `self.steps` para la animación (contrato en 2.1).
- [ ] README: algoritmo y por qué, modo Pac-Man, "Reusable code".

---

## 6. Decisiones técnicas

### B1. Representación de la rejilla ✅

- `list[list[int]]`, bits N = `1`, E = `2`, S = `4`, W = `8`
- Estado inicial: todos los muros cerrados (`ALL_WALLS` = `15`)
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

### B4. Algoritmos de generación ✅

- **Perfecto — backtracker (DFS) con pila explícita**, no recursión (límite
  de ~1000 llamadas de Python). Por qué: el más fácil de explicar, pasillos
  largos, sin límite de tamaño.
- **Pac-Man — trenzado (braiding):** se parte del perfecto con la misma
  semilla y el mismo `rng`; se recorren las celdas en orden aleatorio y cada
  callejón abre un muro (prioridad: vecinas que también son callejón).
  "Probar y deshacer": si al abrir se forma una zona 3×3 abierta, se vuelve a
  cerrar y se prueba otra opción.
  - Resultado: 0 callejones reales; solo quedan los 3 huecos del 42, que el
    analizador tolera como "enclosed".
  - Pendiente A10: garantizar ≥ 2 bucles en tamaños pequeños.
- **Bonus — Kruskal** (decidido 2026-10-16): cada celda empieza siendo su
  propia "isla"; se recorren los muros en orden aleatorio y se abre uno solo
  si une dos islas distintas (union-find). Pasillos cortos y muchos cruces:
  contrasta con el backtracker.
- **Zonas 3×3:** en modo perfecto no pueden existir (un 2×2 abierto ya sería
  un bucle); en Pac-Man las evita el trenzado. Comprobado por tests en los
  dos modos.

### B5. Visualización ✅ MiniLibX

- **Por qué:** nos gusta complicarnos 😄 — y además permite interacción con
  teclado y deja el 42, la entrada, la salida y el camino mucho más claros
  que el ASCII.
- **Interacciones:** `R` regenerar · `P` mostrar/ocultar camino · `C` rotar
  color de muros (5) · `A` animación (bonus, pendiente) · `ESC`/X salir.
- **Colores:** fondo negro, entrada verde, salida roja, camino amarillo, 42
  gris.
- **Tamaño:** celda de 1 a 40 px, la ventana ocupa como mucho el 80 % de la
  pantalla.
- **Instalación:** Poetry, desde el `.whl` de la intra (sección 4, paso 2).

### B6. Casos límite ✅

| Caso | Decisión |
|:--|:--|
| Tamaño mínimo, `PERFECT=True` | 2 celdas (entrada ≠ salida). Ya lo hace el generador |
| Tamaño mínimo, `PERFECT=False` | **3×3** → si no, `MazeGeneratorError` (A10) |
| Tamaño mínimo para el 42 | **9×7**. Si no cabe: se genera sin 42 y se avisa |
| WIDTH / HEIGHT ≤ 0 | **error** (generador) |
| ENTRY o EXIT dentro del 42 | **error** (generador) |
| ENTRY == EXIT | **error** (generador) |
| ENTRY / EXIT fuera de límites | **error** (generador) |
| Clave obligatoria ausente / duplicada / desconocida / vacía | **error** (parser) |
| Espacios alrededor del `=` | **se aceptan** |
| Valores de PERFECT | `true`/`yes`/`1` · `false`/`no`/`0`, sin distinguir mayúsculas; otro = error |
| `ALGORITHM` | `backtracker` (defecto) o `kruskal`, sin distinguir mayúsculas; otro = error |
| SEED ausente | aleatoria y se **muestra** |
| `OUTPUT_FILE` vacío | **error** (parser) |
| `OUTPUT_FILE` no escribible | **error claro, sin traceback** (`a_maze_ing.py` captura `OSError`) |
| Config inexistente / sin argumento | error claro, sin traceback |

**Claves extra:** `SEED` (entero, opcional) y `ALGORITHM` (opcional).

### B7. Estilo común ✅

- Shebang solo en `a_maze_ing.py`
- Docstring de módulo en todos; docstrings en inglés, **estilo Google**,
  también en clases
- Sin comentarios `#` en los `.py`
- Type hints en todas las firmas; Python 3.10+
- Constantes en MAYÚSCULAS con `Final`; auxiliares internas con `_`
- `...` para cuerpos de contrato; `pass` para bloques vacíos ejecutables
- `a_maze_ing.py` con la estructura fija y `=== End of Program ===`
- `mazegen/` y `app/`: sin `main`, sin `if __name__`, sin `print` al importar
- Un único salto de línea al final de cada archivo

### B8. Herramientas externas ✅

- **`maze_analyzer.py`** (del subject): **fuera del repo** (no es nuestro y
  rompería el lint). Cada uno lo guarda fuera y lo usa así:
  `python3 ~/maze_analyzer.py maze.txt --max-dead-ends 0`

---

## 7. Planificación

Plazo de entrega: **por decidir**.

Avance estimado (2026-10-16, por horas de trabajo, con los 3 bonus):

| | Hecho | Queda (aprox.) |
|:--|:--|:--|
| Línea A (Ale) | ~75 % | 12–15 h (A10, Kruskal, `steps`, README) |
| Línea B (joserome) | ~68 % | 9–14 h (lint, MLX en Poetry, prueba en campus, `ALGORITHM`, animación) |
| Juntos | ~25 % | 10–14 h (`a_maze_ing.py`, `.whl`, LICENSE, README, defensa) |
| **Total** | **~62 %** | **~30–40 h** |

| Fase | Real | Notas |
|:--|:--|:--|
| 0 — Acuerdos y entorno | 2026-10-09 | |
| 1 — Núcleo mínimo | 2026-10-13 | Generador, parser, solver, writer y tests |
| 2 — Modo Pac-Man | 2026-10-15 | Trenzado + tests + analizador ✅ (falta A10) |
| 3 — Display MLX | 2026-10-16 | Hecho, falta lint, instalación y prueba |
| 4 — Integración (`a_maze_ing.py`) | | **Siguiente** |
| 5 — Bonus (Kruskal, animación) | | 0 callejones ✅ |
| 6 — Empaquetado y entrega | | |

### Puntos de sincronización

- [x] **S0** — contrato y repo funcionando → nos separamos
- [ ] **S1** — `a_maze_ing.py`: config → laberinto → archivo → ventana,
      `maze_analyzer.py` OK, todos los `configs/` con error claro
- [ ] **S2** — Pac-Man con A10 + display probado en el campus
- [ ] **S3** — paquete `.whl`, LICENSE, README, `lint-strict`, ensayo de
      defensa

### Orden recomendado para la próxima sesión

1. joserome: paso 1 (lint en verde).
2. Juntos: `a_maze_ing.py` y probarlo en el campus con la ventana.
3. Ale: A10. joserome: pasos 2 y 3.

### Herramientas

- Git / GitHub (ramas y PRs), `<editor>`, Poetry, flake8, mypy, pytest,
  build, pdb, MiniLibX, `maze_analyzer.py`
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
| 2026-10-09 | Visualización con MiniLibX | ambos | Nos gusta complicarnos; interacción y claridad |
| 2026-10-09 | Claves duplicadas/desconocidas = error | ambos | Detectar errores de escritura del config |
| 2026-10-09 | SEED opcional; si falta, aleatoria y se muestra | ambos | Reproducibilidad |
| 2026-10-09 | ENTRY/EXIT dentro del 42 = error | ambos | Config inválido, mensaje claro |
| 2026-10-09 | Docstrings Google; licencia MIT | ambos | — |
| 2026-10-09 | Trabajo en GitHub, entrega en vogsphere | ambos | Ramas y PRs para revisarnos |
| 2026-10-09 | Reparto: Ale línea A, joserome línea B | ambos | — |
| 2026-10-09 | Atributos del generador públicos (sin getters) | Ale | Contrato simple |
| 2026-10-09 | `ALL_WALLS` calculado en `directions.py` con `\|` | Ale | Un solo sitio para "todos los muros" |
| 2026-10-09 | 42 = dígitos 3×5, mínimo de laberinto 9×7 | Ale | 1 celda de margen para no aislar celdas |
| 2026-10-09 | `MazeConfig.exit_` / `MazeGenerator(exit=...)` | ambos | Se mapea en `a_maze_ing.py` |
| 2026-10-09 | Nunca trabajar en `main` | ambos | Incidente del push rechazado (PR #3) |
| 2026-10-09 | El parser valida solo formato; los valores solo el generador | ambos (OK joserome 2026-10-16) | No repetir código; el generador valida por ser reutilizable |
| 2026-10-09 | PERFECT acepta true/false, yes/no y 1/0 (sin distinguir mayúsculas) | ambos | Más tolerante con el usuario |
| 2026-10-09 | `get_path()` fuera del parser; nueva `parse_config()` | ambos (OK joserome 2026-10-16) | Cumplir el contrato |
| 2026-10-09 | Nunca mergear con lint en rojo | ambos | PR #4 entró en rojo |
| 2026-10-12 | `pattern42`: constantes calculadas del dibujo | Ale | Cambiar el dibujo recalcula todo |
| 2026-10-12 | `pattern_cells` se calcula en el `__init__` | Ale | Hace falta para validar entrada/salida |
| 2026-10-13 | `_inside()` reutilizado por `_check_coord` y `_neighbours` | Ale | Los límites viven en un solo sitio |
| 2026-10-13 | `generate()` empieza en `entry` con `random.Random(self.seed)` propio | Ale | Reproducible sin tocar el `random` global |
| 2026-10-13 | Semilla aleatoria con `random.randrange(2**32)` | Ale | `seed` siempre es `int`; `seed=0` válido |
| 2026-10-13 | Solver BFS con `deque` y diccionario `previous` | joserome | Camino más corto garantizado |
| 2026-10-13 | `mazegen/__init__.py` exporta la API con `__all__` | Ale | `from mazegen import MazeGenerator`; flake8 y mypy strict |
| 2026-10-13 | Tests con pytest, independientes del código probado (BFS y recuentos propios) | Ale | Un test no se corrige a sí mismo |
| 2026-10-15 | Objetivo: obligatoria + los 3 bonus | ambos | Nota máxima |
| 2026-10-15 | Backtracker separado en `_backtracker(rng)` | Ale | Prepara el 2.º algoritmo |
| 2026-10-15 | Pac-Man por trenzado con "probar y deshacer" y el mismo `rng` | Ale | Reproducible; sin zonas 3×3 |
| 2026-10-15 | Centro = `((w − 1) // 2, (h − 1) // 2)` | Ale | Siempre es el hueco del 42; coincide con el analizador |
| 2026-10-15 | Los 3 huecos del 42 se quedan; no se rediseña el dibujo | ambos | El analizador los tolera como "enclosed" |
| 2026-10-15 | `maze_analyzer.py` fuera del repo | ambos | No es nuestro; rompería el lint |
| 2026-10-16 | Pac-Man debe garantizar ≥ 2 bucles (función nueva, A10) | ambos | Fallo en tamaños pequeños |
| 2026-10-16 | `PERFECT=False` exige mínimo 3×3 | ambos | Por debajo no caben 2 bucles |
| 2026-10-16 | 2.º algoritmo: Kruskal | ambos | Contraste con el backtracker; fácil de explicar |
| 2026-10-16 | Clave `ALGORITHM` opcional, defecto `backtracker`, sin distinguir mayúsculas | ambos | Bonus de varios algoritmos |
| 2026-10-16 | Animación: el generador guarda `steps`; el display los reproduce; tecla `A` | ambos | `mazegen` sigue sin depender de MLX |
| 2026-10-16 | Espacios alrededor del `=` se aceptan | ambos | Tolerante con el usuario |
| 2026-10-16 | `OUTPUT_FILE` no escribible → error claro desde `a_maze_ing.py` | ambos | Nunca traceback |
| 2026-10-16 | MLX se instala con Poetry desde el `.whl` de la intra, en un grupo aparte | ambos | `make install` instala todo; `mazegen` sin MLX |
| 2026-10-16 | `Display` recibe el laberinto ya generado | ambos | No generar dos veces |
| 2026-10-16 | Merges siempre con los dos delante, sin proteger `main` | ambos | Trabajamos juntos en persona |

---

## 9. Retrospectiva (rellenar al final)

- **Qué funcionó bien:**
- **Qué mejoraríamos:**