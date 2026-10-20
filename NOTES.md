# A-Maze-ing — Notas y decisiones del equipo

> Documento interno. Aquí apuntamos cada decisión técnica y de organización
> **antes** de programar sobre ella. Si algo del contrato (sección 2) cambia,
> se habla entre los dos y se actualiza aquí primero.
>
> El README recoge la versión pública (algoritmos y por qué, formato del
> config, gestión del equipo, planificación). Este archivo es el detalle.

**Equipo:** alvicent (Ale, GitHub `Alexxvr8`) · joserome (GitHub `Joositoo`)
**Inicio:** 2026-10-07
**Objetivo:** proyecto **perfecto** → obligatoria completa + **los 3 bonus**

---

## 0. Estado del repo (última revisión: 2026-10-20) ✅ TERMINADO

**Avance: 100 %.** Parte obligatoria y los 3 bonus hechos, probado en el
campus y `.whl` final generado. Solo queda entregar en vogsphere y preparar
la defensa (sección 4).

| Archivo | Estado | De quién |
|:--|:--|:--|
| `mazegen/directions.py` | ✅ | Ale |
| `mazegen/pattern42.py` | ✅ | Ale |
| `mazegen/generator.py` | ✅ Backtracker + Kruskal + Pac-Man (trenzado, ≥ 2 bucles, 0 callejones, mínimo 3×3) + `steps` | Ale |
| `mazegen/solver.py` | ✅ `shortest_path()` con BFS | joserome |
| `mazegen/__init__.py` | ✅ API pública con `__all__` | Ale |
| `mazegen/README.md` + `py.typed` | ✅ Documentación del paquete | Ale |
| `app/config_parser.py` | ✅ Con `ALGORITHM` | joserome (ajustado por Ale) |
| `app/writer.py` | ✅ | joserome |
| `app/display.py` | ✅ R/P/C/A/ESC, animación de generación y de camino | joserome (franja de ayuda: Ale) |
| `a_maze_ing.py` | ✅ Captura todos los errores, avisa sin 42, muestra la semilla | joserome |
| `configs/` | ✅ 15 configs, uno por cada error | joserome |
| `tests/test_generator.py` | ✅ 221 tests | Ale |
| `vendor/mlx-2.2-py3-none-any.whl` | ✅ MiniLibX de Ubuntu | Ale |
| `pyproject.toml`, `poetry.lock` | ✅ Grupo `display` con MLX, override de mypy, metadatos | Ale |
| `LICENSE.md` | ✅ MIT | Ale |
| `README.md` | ✅ Completo | Ale (MLX y controles: joserome) |
| `mazegen-0.1.0-py3-none-any.whl` | ✅ Generado desde `main` con el código final | Ale |

**Calidad en `main`:**
- pytest: ✅ 221 passed
- `make lint`: ✅
- `make lint-strict`: ✅

### Comprobado el 2026-10-20

- **Prueba en un ordenador del campus** (joserome): clon limpio →
  `make install` → `make run`, todas las teclas, tamaños grandes y pequeños
  y los `configs/` de error. ✅
- **`a_maze_ing.py` de punta a punta:** todos los configs de error dan
  mensaje claro y código 1, sin traceback. Sin MLX instalada:
  `No module named 'mlx'`, sin traceback.
- **`maze_analyzer.py`** sobre la salida de `a_maze_ing.py`, 2 modos × 2
  algoritmos × 4 tamaños (20×15, 3×3, 9×7, 50×40):
  - `PERFECT=True` → 8/8 *"PERFECT maze"*.
  - `PERFECT=False` con `--max-dead-ends 0` → 8/8 *"Pac-Man-USABLE"*.
- **El `.whl` se instala** en un venv limpio y funciona con el ejemplo del
  README.

### Historial de incidentes

- **2026-10-09:** joserome trabajó en su `main` local mientras Ale
  mergeaba → `main` divergió y el push falló. Resuelto con rama + PR #3.
- **2026-10-09:** PR #4 entró con lint en rojo (`pattern42` a medias).
  Resuelto en PR #6.
- **2026-10-09 y 12:** dos commits de Ale directos a `main` sin PR.
- **2026-10-16:** PR #15 (MLX) entró con `make lint` en rojo. Arreglado en
  el PR #21.
- **2026-10-16:** el modo Pac-Man dejaba 1 solo bucle en tamaños pequeños.
  Resuelto con A10 (PR #17).
- **2026-10-19 y 20:** dos commits de joserome directos a `main` sin PR
  (`variable fixed` y `Fixed errors`).
- **2026-10-20:** el arreglo de la franja de ayuda del display se coló en
  el commit de MLX (PR #23). Funciona, pero el commit mezcla dos cosas.
- **2026-10-20:** el primer `.whl` se generó en una rama sacada antes de
  mergear A13, así que no llevaba el arreglo. Regenerado desde `main`.

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
   (arreglo), `docs/` (documentación), `test/` (tests), `build/`
   (dependencias y empaquetado).
4. **Antes de cada push y de cada merge:** `make lint` y los tests en verde.
   **Sin excepciones.**
5. **Mensajes de commit:** `<tipo>(<área>): <qué>` y que describan **ese**
   commit. Ej.: `feat(mazegen): braided Pac-Man mode for PERFECT=False`.
6. **Un commit, una cosa.** `git status` antes de `git add`, y añadir los
   archivos por nombre.
7. **PR → merge con los dos delante.** Trabajamos juntos en persona, así que el
   merge lo hace uno con el otro al lado revisándolo (no hace falta proteger
   `main` en GitHub).
8. **Después del merge:** borrar la rama (botón "Delete branch" en GitHub, y
   `git branch -d <rama>` en local).
9. **Si `git push` falla con `rejected`:** NO usar `--force`. Avisar al otro.
10. **Si cambia `poetry.lock`** (alguien añadió una dependencia): `make install`.
11. **Si cambia algo de `mazegen/`:** regenerar el `.whl` de la raíz
    (sección 6, B9). Siempre desde `main` actualizado.

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
              algorithm: str = "backtracker")
```

| Miembro | Tipo | Qué es |
|:--|:--|:--|
| `__init__` | — | Valida y guarda. **No genera.** Lanza `MazeGeneratorError` si algo es inválido |
| `generate()` | `-> None` | Construye con `self.seed`: perfecto con el algoritmo elegido y, si `perfect` es `False`, trenzado (0 callejones fuera del 42, ≥ 2 bucles, sin zonas 3×3) |
| `regenerate()` | `-> None` | Semilla nueva + `generate()` |
| `algorithm` | `str` | `"backtracker"` o `"kruskal"` (constante `ALGORITHMS`). Otro valor → `MazeGeneratorError` |
| `grid` | `list[list[int]]` | `grid[y][x]` con bits N1 E2 S4 W8. Vacía hasta `generate()` |
| `seed` | `int` | Semilla usada. Nunca `None` |
| `pattern_cells` | `set[tuple[int, int]]` | Celdas del 42. **Vacío si no cabe** |
| `steps` | `list[tuple[tuple[int, int], int]]` | Muros que acaban abiertos, en el orden en que se abrieron: `(celda, dirección)` |
| `width`, `height`, `entry`, `exit`, `perfect` | — | Los parámetros, públicos |
| `MazeGeneratorError` | `ValueError` | Excepción del paquete |

**Contrato de la animación ✅:**
- El generador **no sabe nada de MLX**. Solo rellena `self.steps` durante
  `generate()` (se vacía al principio de cada `generate()`).
- Cada paso es un muro que se abre y **se queda abierto**: los intentos que
  se deshacen no se guardan, y si un muro se cierra para compensar (A13)
  se borra de la lista con `_forget_step`.
- Reproducir `steps` sobre una rejilla cerrada da exactamente `grid`
  (comprobado por tests, también en tamaños pequeños).
- El display los reproduce con `mlx_loop_hook`, unos cuantos por fotograma
  (unos 4 s en total). Tecla **`A`**.

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
    algorithm: str

def parse_config(path: str) -> MazeConfig: ...
```

- **`parse_config(path)` es la ÚNICA función pública** que usa
  `a_maze_ing.py`.
- Recibe la **ruta**. Leer `sys.argv` va en `a_maze_ing.py`.
- Valida **solo el formato**: lectura, claves obligatorias / duplicadas /
  desconocidas / vacías, tipos y `OUTPUT_FILE` no vacío.
- **No valida valores** (tamaño, límites, entrada ≠ salida, 42, tamaño mínimo
  del Pac-Man, algoritmo): eso lo hace **solo** el generador.
- `exit_` en el parser, `exit` en el generador; se mapea en `a_maze_ing.py`.
- **`ALGORITHM`**: opcional. El parser la lee, la pasa a minúscula y, si
  falta, pone `"backtracker"` (`DEFAULT_ALGORITHM`).

**`mazegen/solver.py`:** `shortest_path(grid, entry, exit) -> str`. BFS con
`deque`, devuelve letras (`"ESSEN"`), `ValueError` si no hay camino. No
importa nada de `app/`.

**`app/writer.py`:** `write_maze(path, grid, entry, exit, solution) -> None`.
Formato exacto del subject, hex en minúscula, `\n` en cada línea. Deja salir
el `OSError`.

**`app/display.py`:** clase `Display`.
- Recibe el `MazeGenerator` **ya generado**; su `__init__` no genera.
- `run()` abre la ventana y el bucle de eventos. Teclas: `R` regenera
  (animado), `P` camino (animado), `C` color de muros, `A` repite la
  animación, `ESC`/X salir.
- La imagen ocupa toda la ventana, incluida la franja de ayuda, para que el
  texto se borre en cada fotograma.

### 2.3 `a_maze_ing.py` ✅

`sys.argv` → `parse_config` → `MazeGenerator(..., algorithm=...)` →
`generate()` → aviso si no hay 42 → semilla si no venía en el config →
`shortest_path` → `write_maze` → `Display(generator).run()`.
- Con un número de argumentos distinto de 1: `Usage` y código 1.
- Captura `ConfigError`, `MazeGeneratorError`, `ValueError`, `OSError`,
  `RuntimeError` e `ImportError`, y aparte `KeyboardInterrupt`. Mensaje por
  `stderr`, código 1, nunca traceback.
- `from app.display import Display` va **dentro** del `try`: así, si MLX no
  está instalada, el error se captura como los demás.
- Escribe el archivo **antes** de abrir la ventana.

---

## 3. Reparto ✅

| Línea | Responsable | Piezas |
|:--|:--|:--|
| **A — Motor** (`mazegen/` menos el solver) | **alvicent** | `directions`, `generator`, `pattern42`, backtracker, Pac-Man, Kruskal, pasos de animación, tests del motor |
| **B — Consumo** | **joserome** | `config_parser`, `configs/`, `solver`, `writer`, display MLX + interacción + animación en pantalla |
| Compartido → **alvicent** | | Instalación de MLX, LICENSE, metadatos y `.whl` del paquete, README del paquete y README principal, NOTES |
| Compartido → **joserome** | | `a_maze_ing.py`, revisar la parte de MLX y controles del README |
| Juntos | ambos | Prueba final en el campus y ensayo de la defensa |

El reparto de lo compartido se decidió el 2026-10-18 según lo que le quedaba
a cada uno: la línea A estaba casi terminada.

En la defensa **los dos** tienen que saber explicar todo.

---

## 4. Entrega y defensa

### Hecho ✅

- [x] `.whl` final regenerado desde `main` (Ale)
- [x] Prueba completa en un ordenador del campus (joserome)
- [x] `configs/entry_in_42.txt` (joserome)
- [x] Sección de MLX y controles del README revisada (joserome)
- [x] Retoques del README y salto de línea final en todos los archivos (Ale)

### Opcional (no hace falta para entregar)

- [ ] `writer.py`: `format(n, "x")` en vez del `match`.
- [ ] `solver.py`: quitar el punto final del mensaje y los paréntesis de
      `(dx, dy)`.
- [ ] Display: que `P` durante la animación de generación quede apuntada
      (`path_after = True`) en vez de ignorarse.
- [ ] `a_maze_ing.py`: prefijo `Error: ` en los mensajes.
- [ ] Tecla para cambiar el color del 42.

Si se hace alguno después de entregar en vogsphere, hay que volver a subirlo
(y si toca `mazegen/`, regenerar el `.whl`).

### Entrega

- [ ] Subir a vogsphere desde `main` (solo cuenta lo que hay en el repo de
      la intra). Comprobar antes los nombres: `a_maze_ing.py`,
      `config.txt`, `Makefile`, `README.md`, `LICENSE.md`,
      `mazegen-0.1.0-py3-none-any.whl`, `.gitignore`.

### Preparación de la defensa (los dos)

- [ ] Construir el paquete en un venv nuevo: `python3 -m venv venv`,
      `pip install build`, `python -m build`.
- [ ] Instalar el `.whl` en otro venv y usarlo con el ejemplo del README.
- [ ] Pasar `maze_analyzer.py` delante del evaluador: `PERFECT=True` y
      `PERFECT=False --max-dead-ends 0`.
- [ ] Que cada uno explique la parte del otro.
- [ ] Practicar una modificación pequeña en vivo: cambiar un color, añadir
      una tecla, cambiar el tamaño mínimo del 42, añadir una clave al config.

---

## 5. Línea A (Ale) ✅

- [x] **A1–A6** motor perfecto (directions, validaciones, muros, 42,
      backtracker, semilla)
- [x] **A7** tests del motor perfecto
- [x] **A8** modo Pac-Man (trenzado sin zonas 3×3)
- [x] **A9** backtracker en su propio método `_backtracker(rng)`
- [x] Tests del Pac-Man (conectividad, bucles, callejones, 3×3, esquinas y
      centro, semilla)
- [x] **A10** Pac-Man con ≥ 2 bucles (`_ensure_loops`) y mínimo 3×3 (PR #17)
- [x] Refactor: métodos agrupados en bloques con separadores y
      `_closed_inner_walls()` compartida
- [x] **A11** Bonus: **Kruskal** con union-find + parámetro `algorithm`
      (PR #18)
- [x] **A12** Bonus: `self.steps` para la animación (PR #20)
- [x] Instalación de MLX con Poetry (PR #23)
- [x] LICENSE, metadatos, `py.typed` y README del paquete (PR #24)
- [x] README principal (PR #26)
- [x] **A13** Bonus completo: 0 callejones también en tamaños pequeños con
      Kruskal (`_compensate` + `_forget_step`, PR #27)
- [x] `.whl` final (PR del 2026-10-20)

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
- **Bonus — Kruskal:** cada celda fuera del 42 empieza siendo su propia
  "isla"; se recorren los muros interiores en orden aleatorio y se abre uno
  solo si une dos islas distintas (union-find con un diccionario `parent`;
  se unen los **jefes**, no las celdas). No usa `entry`: la conectividad la
  garantiza que al final todo es una sola isla.
  - `_find` con `while` (no recursión) y **acortando el camino**
    (`parent[cell] = parent[parent[cell]]`): 200×200 pasó de 11 s a 0,3 s.
  - Contraste: con la semilla 42 en 20×15, el backtracker deja 32
    callejones y Kruskal 87.
- **Pac-Man — trenzado (braiding):** se parte del perfecto con la misma
  semilla y el mismo `rng`; se recorren las celdas en orden aleatorio y cada
  callejón abre un muro (prioridad: vecinas que también son callejón).
  "Probar y deshacer": si al abrir se forma una zona 3×3 abierta, se vuelve a
  cerrar y se prueba otra opción.
- **Pac-Man — "abrir y compensar" (A13):** si todas las opciones de un
  callejón crean un 3×3 abierto (pasaba con Kruskal en tamaños con un lado
  de 3 a 7), se abre igualmente y `_compensate` cierra **otro** muro de ese
  bloque cuyas dos celdas sigan con ≥ 2 salidas. Se mantiene la
  conectividad (un 3×3 abierto menos un muro sigue conectado), no aparecen
  callejones nuevos y el número de bucles no baja. El muro cerrado se borra
  de `steps` con `_forget_step` (puede estar apuntado desde cualquiera de
  sus dos lados).
- **Pac-Man — ≥ 2 bucles (A10):** `_ensure_loops` abre muros extra hasta
  tener 2. Bucles = pasajes − (celdas alcanzables − 1).
- **Resultado:** 0 callejones fuera del 42; solo quedan los 3 huecos del
  dibujo, que el analizador tolera como "enclosed".
- **Zonas 3×3:** en modo perfecto no pueden existir (un 2×2 abierto ya sería
  un bucle); en Pac-Man las evitan el trenzado y la compensación.

### B5. Visualización ✅ MiniLibX

- **Por qué:** nos gusta complicarnos 😄 — y además permite interacción con
  teclado y deja el 42, la entrada, la salida y el camino mucho más claros
  que el ASCII.
- **Interacciones:** `R` regenerar · `P` mostrar/ocultar camino · `C` rotar
  color de muros (5) · `A` animación · `ESC`/X salir. `R` y `P` también se
  animan.
- **Colores:** fondo negro, entrada verde, salida roja, camino amarillo, 42
  gris.
- **Tamaño:** celda de 1 a 40 px, la ventana ocupa como mucho el 80 % de la
  pantalla y mide al menos 440 px de ancho (para el texto de ayuda).
- **Instalación:** ver B10.

### B6. Casos límite ✅

| Caso | Decisión |
|:--|:--|
| Tamaño mínimo, `PERFECT=True` | 2 celdas (entrada ≠ salida) |
| Tamaño mínimo, `PERFECT=False` | **3×3** → si no, `MazeGeneratorError` |
| Tamaño mínimo para el 42 | **9×7**. Si no cabe: se genera sin 42 y se avisa |
| WIDTH / HEIGHT ≤ 0 | **error** (generador) |
| ENTRY o EXIT dentro del 42 | **error** (generador) |
| ENTRY == EXIT | **error** (generador) |
| ENTRY / EXIT fuera de límites | **error** (generador) |
| Clave obligatoria ausente / duplicada / desconocida / vacía | **error** (parser) |
| Espacios alrededor del `=` | **se aceptan** |
| Valores de PERFECT | `true`/`yes`/`1` · `false`/`no`/`0`, sin distinguir mayúsculas; otro = error |
| `ALGORITHM` | `backtracker` (defecto) o `kruskal`, sin distinguir mayúsculas; otro = `MazeGeneratorError` |
| SEED ausente | aleatoria y se **muestra** |
| `OUTPUT_FILE` vacío | **error** (parser) |
| `OUTPUT_FILE` no escribible (p. ej. una carpeta) | error claro, sin traceback |
| Config inexistente, carpeta o sin argumento | error claro, sin traceback |
| MLX no instalada o falta una librería del sistema | error claro, sin traceback (`ImportError` / `OSError`) |
| Ctrl+C | `Interrupted`, sin traceback |

**Claves extra:** `SEED` (entero, opcional) y `ALGORITHM` (opcional).

### B7. Estilo común ✅

- Shebang solo en `a_maze_ing.py`
- Docstring de módulo en todos; docstrings en inglés, **estilo Google**,
  también en clases
- Sin comentarios `#` en los `.py`, **salvo** separadores de bloque
  `# --- Nombre ---` hasta la columna 79: dentro de las clases y, en los
  tests, entre grupos de tests. Ningún otro comentario.
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

### B9. Paquete `mazegen` ✅

- Se construye con `python -m build` (backend `poetry-core`). Solo entra
  `mazegen/`: ni `app/`, ni tests, ni `vendor/`.
- Metadatos en `[project]`: `readme = "mazegen/README.md"`,
  `license = "MIT"`, `license-files = ["LICENSE.md"]`, autores.
  `[project].dependencies` vacío.
- `mazegen/py.typed` para que mypy use nuestros tipos en otros proyectos.
- El `.whl` va en la **raíz** (lo pide el subject) y tiene que
  corresponder al código final. Para regenerarlo:
  ```
  git switch main && git pull
  poetry run python -m build
  cp dist/mazegen-0.1.0-py3-none-any.whl .
  ```
- Licencia **MIT**: permisiva, corta, permite reutilizar y distribuir el
  generador con la única condición de mantener el aviso de copyright.

### B10. Instalación de MiniLibX ✅

- El `mlx-2.2.tgz` de la intra trae `src/` (C), `fedora/` y `ubuntu/`. Usamos
  **`ubuntu/mlx-2.2-py3-none-any.whl`** (los ordenadores del campus son
  Ubuntu), guardado en `vendor/` **sin cambiarle el nombre**.
- Grupo de Poetry **`display`**, no `[project].dependencies`: `mazegen`
  tiene que poder reutilizarse sin MLX.
- Marcador `sys_platform == 'linux'`: el `.whl` dice `none-any`, pero solo
  funciona en Linux con X11.
- `[[tool.mypy.overrides]]` con `ignore_missing_imports` para `mlx`, que no
  trae tipos → `make lint-strict` en verde.
- Requisito del sistema en Ubuntu: `sudo apt install libxcb-keysyms1`.
- ⚠️ `mlx` en PyPI es **otra librería** (la de Apple para IA).
- ⚠️ Para probar desde un clon limpio, **desactivar** antes el venv
  (`deactivate`): si no, Poetry reutiliza el entorno activado.

---

## 7. Planificación

Plazo de entrega: **sin fecha fija**.

| Fase | Hecho | Notas |
|:--|:--|:--|
| 0 — Acuerdos y entorno | 2026-10-09 | Contrato, reglas de Git, estilo, Poetry |
| 1 — Núcleo mínimo | 2026-10-13 | Generador, parser, solver, writer y tests |
| 2 — Modo Pac-Man | 2026-10-16 | Trenzado + ≥ 2 bucles + tests + analizador |
| 3 — Display MLX | 2026-10-16 | Teclas R/P/C/ESC |
| 4 — Bonus | 2026-10-16 a 2026-10-20 | Kruskal (10-16) · animación (10-18) · 0 callejones completo (10-20) |
| 5 — Integración (`a_maze_ing.py`) | 2026-10-20 | Más tarde de lo previsto |
| 6 — Empaquetado y entrega | 2026-10-20 | MLX, LICENSE, `.whl`, README y prueba en el campus |

**Cómo evolucionó:** las primeras fases fueron según lo previsto y acabamos
haciendo los 3 bonus. El cambio principal fue la integración: estaba
prevista justo después del núcleo (S1), pero fuimos mejorando cada línea por
separado y la dejamos para el final. Hasta entonces, las pruebas del programa
completo se hicieron con pequeños comandos de terminal.

### Puntos de sincronización

- [x] **S0** — contrato y repo funcionando → nos separamos
- [x] **S1** — `a_maze_ing.py`: config → laberinto → archivo → ventana,
      `maze_analyzer.py` OK, todos los `configs/` con error claro
- [x] **S2** — display probado en el campus
- [x] **S3** — `.whl` final, `lint-strict`, LICENSE y README
- [ ] **S4** — entrega en vogsphere y defensa

### Herramientas

- Git / GitHub (ramas y PRs), VS Code, Poetry, flake8, mypy, pytest, build,
  pdb, MiniLibX, `maze_analyzer.py`
- IA (Claude): ver la sección *Use of AI* del README

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
| 2026-10-16 | `_ensure_loops` tras el trenzado; comprueba antes de abrir | Ale | Los laberintos grandes no cambian con la misma semilla |
| 2026-10-16 | `ALGORITHM` lo valida solo el generador; el parser solo lee y pasa a minúscula | ambos | Una sola lista de algoritmos; misma regla formato/valores |
| 2026-10-16 | Kruskal con union-find, `_find` iterativo y acortando caminos | Ale | Sin límite de recursión; 200×200 en 0,3 s |
| 2026-10-16 | `_closed_inner_walls()` compartida por Kruskal y `_ensure_loops` | Ale | La lista de muros vive en un solo sitio |
| 2026-10-16 | Excepción a B7: separadores `# --- Bloque ---` dentro de las clases | ambos | Legibilidad de `generator.py` |
| 2026-10-16 | Todos los tests de propiedades con los dos algoritmos (`parametrize`) | Ale | Kruskal cumple las mismas reglas |
| 2026-10-16 | Separadores `# --- Bloque ---` también en los tests | Ale | Mismo criterio de legibilidad |
| 2026-10-18 | Animación de generación y de camino, unos 4 s fijos | joserome | Igual de rápida en cualquier tamaño |
| 2026-10-18 | Reparto de lo compartido según lo que queda a cada uno | ambos | La línea A estaba casi terminada |
| 2026-10-20 | `a_maze_ing.py` lo hace joserome; MLX lo instala Ale | ambos | Intercambio para avanzar en paralelo |
| 2026-10-20 | MLX: `.whl` de Ubuntu en `vendor/`, grupo `display`, marcador Linux, override de mypy | Ale | El campus es Ubuntu; `mazegen` sin MLX; `lint-strict` en verde |
| 2026-10-20 | La imagen del display ocupa toda la ventana | Ale | El texto de ayuda se borra en cada fotograma |
| 2026-10-20 | Licencia MIT; metadatos y README dentro del `.whl`; `py.typed` | Ale | El subject pide código y documentación en un solo archivo |
| 2026-10-20 | Import del display dentro del `try`; `ImportError` y `KeyboardInterrupt` capturados | joserome | Nunca traceback, ni sin MLX ni con Ctrl+C |
| 2026-10-20 | A13: "abrir y compensar" + `_forget_step` | Ale | Bonus de 0 callejones también en tamaños pequeños con Kruskal |
| 2026-10-20 | El `.whl` se regenera siempre lo último, desde `main` | ambos | Incidente del `.whl` sin A13 |

---

## 9. Retrospectiva

- **Qué funcionó bien:** casi todo. Acordar el contrato entre las dos líneas
  en este NOTES antes de programar permitió que cada uno avanzara sin
  bloquear al otro. Solo nos pisamos una vez (quién valida los valores, el
  parser o el generador), y lo resolvimos dejando la regla por escrito.
  Trabajar en persona y revisar juntos cada PR también ayudó mucho.
- **Qué mejoraríamos:** hacer `a_maze_ing.py` mucho antes. Hasta entonces,
  cada prueba del programa completo tuvo que hacerse con pequeños comandos
  de terminal en vez de ejecutar el programa. También: generar el `.whl`
  solo al final y desde `main`, y no mezclar dos cambios en un commit.