# A-Maze-ing — Notas y decisiones del equipo

> Documento interno. Aquí apuntamos cada decisión técnica y de organización
> **antes** de programar sobre ella. Si algo del contrato cambia, se habla
> entre los dos y se actualiza aquí primero.
>
> Al final del proyecto, parte de este contenido pasa al README
> (algoritmo y por qué, formato del config, gestión del equipo, planificación).

**Equipo:** alvicent (Ale) · `<login2>`
**Inicio:** 2026-10-07

---

## 0. Estado de la Fase 0

- [x] Repo creado, los dos con acceso
- [x] `.gitignore` (sin ignorar el `.whl` de la raíz)
- [x] Poetry + dependencias de desarrollo (flake8, mypy, build, pytest) y `poetry.lock`
- [x] flake8 y mypy configurados para excluir el venv / build / dist
- [x] Makefile con install, run, debug, clean, lint, lint-strict (flags exactos)
- [x] Esqueleto de carpetas, `make lint` limpio
- [ ] Docstrings de módulo rellenos
- [ ] `config.txt` por defecto + carpeta `configs/` con casos rotos
- [x] Decisiones B1, B2, B4, B5, B7
- [ ] B6 completa (quedan casos por decidir)
- [ ] **Contrato de `MazeGenerator` (B3) escrito y aceptado por los dos** ← bloquea
- [ ] Reparto de líneas de trabajo
- [ ] Fechas previstas por fase
- [ ] Prueba en limpio del compañero (`git clone` → `make install` → `make lint` → `make run`)

---

## 1. Decisiones técnicas

### B1. Representación de la rejilla ✅

- **Estructura:** lista de listas de `int` (`list[list[int]]`)
- **Bits de muro:** N = `1`, E = `2`, S = `4`, W = `8`
- **Estado inicial de cada celda:** todos los muros cerrados (`15`, `0xF`)
- **Dónde viven las constantes** (bits, desplazamientos, opuestos): dentro de
  `mazegen/` (las usan generador y solver)
- **Motivo:** coincide bit a bit con el formato hex de salida; abrir o cerrar
  un muro es una operación de bits, rápida y fácil de explicar en la defensa.

### B2. Sistema de coordenadas ✅

- **Formato externo (config / salida):** `(x, y)` → x = columna, y = fila
- **Acceso interno:** `grid[y][x]`
- **Origen:** arriba-izquierda · **Norte es:** `y - 1`
- **Dibujo de referencia:**

```
      x=0   x=1   x=2
y=0  (0,0) (1,0) (2,0)
y=1  (0,1) (1,1) (2,1)
```

### B3. Contrato de `MazeGenerator` ⏳ (pendiente — BLOQUEA)

**Ubicación:** `mazegen/generator.py`, exportado en `mazegen/__init__.py`

**Entrada (constructor):**

| Parámetro | Tipo | Obligatorio | Por defecto | Notas |
|:--|:--|:--|:--|:--|
| | | | | |

**Acción:**
- ¿Genera al crearse o con un método aparte? →
- ¿Se puede regenerar (nueva semilla)? ¿Cómo? →

**Salida (lo que expone):**

| Nombre | Tipo | Qué contiene |
|:--|:--|:--|
| rejilla | `list[list[int]]` | Bits NESW por celda (B1) |
| solución | | ¿letras `NESW` o lista de celdas? |
| celdas del 42 | | |
| semilla usada | `int` | Para mostrarla si no venía en el config |

**Errores:**
- ¿Qué valida el generador por sí mismo? →
- ¿Qué excepción lanza? (¿propia?) →
- ¿Cómo indica que el 42 no cabe, sin hacer `print` desde la librería? →

### B4. Algoritmo de generación ✅

- **Modo perfecto:** backtracker recursivo (DFS), implementado **con pila
  explícita**, no con recursión (límite de ~1000 llamadas de Python)
- **Por qué:** es el más fácil de explicar y razonar en la defensa; genera
  pasillos largos; con una pila es iterativo y no tiene problemas de tamaño.
- **Modo Pac-Man (idea inicial):** partir del laberinto perfecto y tumbar
  muros para crear bucles y eliminar callejones, sin crear zonas 3x3 abiertas
- **¿Algoritmos extra para el bonus?:** pendiente (candidato: Kruskal)

### B5. Visualización ✅

- **Elección:** MiniLibX (MLX)
- **Por qué:** `<completar>`
- **Interacciones:** regenerar · mostrar/ocultar camino · rotar colores de
  muros · `<otras>`
- **Pendientes por MLX:**
  - [ ] Conseguir el paquete Python de MLX (adjuntos del proyecto en la intra)
        y comprobar que funciona en las máquinas del campus
  - [ ] Decidir cómo se instala con `make install` sin meterlo en las
        dependencias de `mazegen` (el paquete reutilizable no lo necesita)
  - [ ] Comprobar `make lint-strict`: con `--strict` no se ignoran los imports
        sin tipos, así que el import de MLX puede dar error
  - [ ] Cambiar el docstring de `app/display.py` ("terminal" → "window")
  - [ ] Tamaño de celda en píxeles y tamaño máximo de ventana

### B6. Casos límite (política)

| Caso | Decisión |
|:--|:--|
| Tamaño mínimo del laberinto | ⏳ |
| Tamaño mínimo para dibujar el 42 | ⏳ (si no cabe: se omite y se avisa, lo dice el subject) |
| ENTRY o EXIT dentro del 42 | **error** |
| ENTRY == EXIT | **error** |
| ENTRY / EXIT fuera de límites | **error** |
| Clave obligatoria ausente | **error** |
| Clave duplicada | **error** |
| Clave desconocida | **error** |
| Espacios alrededor del `=` | ⏳ |
| Valores aceptados para PERFECT | `True` / `False` **sin distinguir mayúsculas**; cualquier otro, error |
| SEED ausente | semilla **al azar**, y se **muestra** para poder reproducirla |
| Fichero de salida no escribible | ⏳ (error claro, sin traceback) |
| Config inexistente / sin argumento | error claro, sin traceback |

**Claves extra del config:**

| Clave | Valores | Por defecto |
|:--|:--|:--|
| SEED | entero | aleatoria (y se muestra) |

### B7. Estilo común ✅

- Shebang `#!/usr/bin/env python3` **solo en `a_maze_ing.py`** (el único que
  se ejecuta); los módulos importados no lo llevan
- Docstring de módulo en todos los archivos: `"""archivo.py: ..."""`
  (en los `__init__.py`, el nombre del paquete)
- Docstrings en inglés, PEP 257, **estilo Google** (`Args:`, `Returns:`,
  `Raises:`), también en clases
- Sin comentarios `#` en los `.py`
- Type hints en todas las firmas; Python 3.10+
- `...` para cuerpos de contrato; `pass` para bloques vacíos ejecutables
- Script (`a_maze_ing.py`): estructura fija con `=== End of Program ===`
- Módulos de librería (`mazegen/`, `app/`): sin `main`, sin
  `if __name__ == "__main__"`, sin `print` al importarse
- Todos los archivos acaban en un único salto de línea

---

## 2. Organización

### Reparto ⏳

| Línea | Responsable | Piezas |
|:--|:--|:--|
| A — Motor | | constantes, generador perfecto, patrón 42, modo Pac-Man |
| B — Consumo | | parser, solver BFS, writer, display MLX + interacción, validadores/tests |
| Juntos | ambos | empaquetado, LICENSE, README, ensayo de defensa |

### Git

- **Remotos:** GitHub `https://github.com/Alexxvr8/A-Maze_ing` (trabajo) ·
  vogsphere `<url>` (entrega final) · dueño GitHub: alvicent
- **Ramas:** `feat/...`, `fix/...`, `docs/...`
- **Commits:** `<área>: <qué>` — p. ej. `parser: validate ENTRY bounds`
- **Regla:** nada entra en `main` sin revisión del otro y `make lint` limpio
- **Entorno:** `make install` (Poetry, venv en `.venv/` gracias a
  `poetry.toml`); repetir solo si cambia `poetry.lock`

### Planificación

Plazo de entrega: **por decidir**.

| Fase | Prevista | Real | Notas |
|:--|:--|:--|:--|
| 0 — Acuerdos y entorno | | | Entorno listo el 2026-10-09 |
| 1 — Núcleo mínimo | | | |
| 2 — 42 + solver + display | | | |
| 3 — Modo Pac-Man | | | |
| 4 — Interacción | | | |
| 5 — Empaquetado y entrega | | | |
| 6 — Bonus | | | |

### Puntos de sincronización

- [ ] **S0** — contrato firmado y repo funcionando → nos separamos
- [ ] **S1** — generador perfecto + solver/writer/display integrados, `maze_analyzer.py` OK
- [ ] **S2** — 42 + Pac-Man + interacción integrados, pruebas con muchas semillas
- [ ] **S3** — paquete, LICENSE, README, `lint-strict`, ensayo de defensa

### Herramientas usadas

- Git / GitHub, `<editor>`, Poetry, flake8, mypy, pytest, build, pdb, MiniLibX
- IA: `<para qué tareas y qué partes>`

---

## 3. Registro de decisiones

| Fecha | Decisión | Quién | Motivo |
|:--|:--|:--|:--|
| 2026-10-07 | Empezamos el proyecto, equipo de 2 | ambos | — |
| 2026-10-08 | Gestor: Poetry; sin `requirements.txt` | ambos | Una sola fuente de dependencias + lockfile |
| 2026-10-08 | Paquete `mazegen` sin dependencias; herramientas en grupo `dev` | ambos | Quien reutilice el paquete no se lleva nuestro lint |
| 2026-10-08 | Config de flake8 en `.flake8`, de mypy en `pyproject.toml` | ambos | flake8 no lee `pyproject.toml` |
| 2026-10-09 | Venv dentro del repo con `poetry.toml` (`in-project = true`) | ambos | Mismo entorno para los dos sin pasos manuales |
| 2026-10-09 | Shebang solo en el punto de entrada | ambos | Los módulos importados nunca se ejecutan directamente |
| 2026-10-09 | Rejilla `list[list[int]]`, bits N1 E2 S4 W8, `grid[y][x]` | ambos | Coincide con el formato de salida |
| 2026-10-09 | Algoritmo perfecto: backtracker DFS con pila | ambos | Fácil de explicar, sin límite de recursión |
| 2026-10-09 | Visualización con MiniLibX | ambos | `<motivo>` |
| 2026-10-09 | Config: claves duplicadas/desconocidas = error; PERFECT sin mayúsculas | ambos | Detectar errores de escritura del config |
| 2026-10-09 | SEED opcional; si falta, aleatoria y se muestra | ambos | Reproducibilidad sin obligar a escribirla |
| 2026-10-09 | ENTRY/EXIT dentro del 42 = error | ambos | Config inválido, mensaje claro |
| 2026-10-09 | Docstrings estilo Google; licencia MIT | ambos | — |
| 2026-10-09 | Trabajo en GitHub, entrega en vogsphere | ambos | Ramas y PRs para revisarnos |

---

## 4. Retrospectiva (rellenar al final)

- **Qué funcionó bien:**
- **Qué mejoraríamos:**