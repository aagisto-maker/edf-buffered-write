# Procedimiento para crear el repositorio público y obtener el DOI

Este documento describe, paso a paso, qué hacer y en qué orden para tener el
repositorio listo antes de subir el manuscrito al sistema editorial de
la revista de destino.

Todos los pasos requieren cuentas gratuitas: GitHub y Zenodo (este último se
accede con ORCID, que también es gratuito). Si no tienes ORCID aún, créalo
primero en https://orcid.org — tarda 2 minutos y es necesario para Zenodo y
también lo va a pedir el sistema editorial de Elsevier al enviar.

---

## Fase 0 — Preparativos (15 minutos)

### 0.1. Cuentas necesarias

- [ ] **ORCID** registrado en https://orcid.org/register
- [ ] **GitHub** registrado en https://github.com/signup (preferiblemente con
      el correo institucional UCM)
- [ ] **Zenodo** registrado en https://zenodo.org/signup, **iniciando sesión
      con ORCID** (importante: que la cuenta de Zenodo quede vinculada a
      ORCID desde el principio)

### 0.2. Cliente Git en local

Si no tienes Git instalado en tu equipo:

- Windows: descarga Git for Windows en https://git-scm.com/download/win
- macOS: ejecuta en Terminal `xcode-select --install`
- Linux: `sudo apt install git`

Comprueba que funciona:

```bash
git --version
```

### 0.3. Configurar identidad de Git

Solo la primera vez en tu equipo:

```bash
git config --global user.name "Ángel Agis-Torres"
git config --global user.email "tu-correo-ucm@ucm.es"
```

---

## Fase 1 — Crear el repositorio en GitHub (10 minutos)

### 1.1. Desde la web

1. Ve a https://github.com/new
2. Configura:
   - **Repository name**: `edf-buffered-write` (o el nombre que prefieras)
   - **Description**: "Reproducibility package for the journal on EDF buffered writing"
   - **Public** ✓ (es imprescindible que sea público para que Zenodo lo
     archive y para que los revisores accedan)
   - **Add a README file** ✓
   - **Add .gitignore**: elige plantilla "Python"
   - **Choose a license**: **GNU General Public License v3.0**
3. Botón "Create repository"

### 1.2. Clonar a tu equipo

En la página del repo recién creado, copia la URL HTTPS (botón verde "Code").
Luego en tu terminal:

```bash
cd ~/Documentos     # o donde tengas tus proyectos
git clone https://github.com/TU_USUARIO/edf-buffered-write.git
cd edf-buffered-write
```

### 1.3. Volcar el contenido del paquete

Coloca todos los archivos que ya tienes (los scripts del paquete, las figuras
generadas, el `metrics.json`, etc.) siguiendo la estructura propuesta:

```
edf-buffered-write/
├── README.md           ← reemplazar por la versión completa proporcionada
├── LICENSE             ← ya creada por GitHub
├── CITATION.cff        ← añadir
├── .zenodo.json        ← añadir
├── requirements.txt    ← añadir
├── src/                ← scripts del paquete
├── tests/              ← tests de integridad
├── data/
│   └── real/
│       └── README.md   ← descripción de la señal real (Fase 4)
├── results/
│   ├── figures/        ← Figuras 2, 3 y 4 en PDF y PNG
│   └── metrics.json    ← cifras numéricas reportadas en el paper
└── docs/
    └── reproduce.md    ← protocolo de reproducción
```

Reemplaza el `README.md` de plantilla por la versión completa que se te ha
proporcionado por separado.

### 1.4. Primer commit y push

```bash
git add .
git commit -m "Initial release of reproducibility package for journal submission"
git push origin main
```

Comprueba en la web de GitHub que todos los archivos están presentes y que el
README se renderiza correctamente.

---

## Fase 2 — Conectar GitHub con Zenodo (5 minutos)

Esto es la magia que hace que cada vez que publiques una "release" en GitHub,
Zenodo la archive automáticamente y le asigne un DOI.

### 2.1. Activar la integración

1. Ve a https://zenodo.org/account/settings/github/
2. Si es la primera vez, te pedirá autorizar a Zenodo a leer tu lista de
   repositorios → "Authorize"
3. Verás la lista de tus repositorios públicos. Localiza
   `edf-buffered-write` y **activa el interruptor** (ON)

A partir de ahora, cualquier release que publiques en GitHub se archivará en
Zenodo automáticamente.

---

## Fase 3 — Crear la primera "release" y obtener el DOI (5 minutos)

### 3.1. Asegúrate de que el repo está completo

Antes de hacer la release, ejecuta una vez los scripts en local para verificar
que `metrics.json` se genera correctamente y coincide con las cifras del
paper, y que las figuras se reproducen.

### 3.2. Tag y release en GitHub

En tu terminal:

```bash
git tag -a v1.0.0 -m "Version 1.0.0 — submission to journal"
git push origin v1.0.0
```

Luego en la web de GitHub:

1. Ve a tu repo → pestaña "Releases" (a la derecha) → "Draft a new release"
2. **Choose a tag**: `v1.0.0` (el que acabas de crear)
3. **Release title**: `v1.0.0 — BSPC submission`
4. **Description**: una frase breve, p. ej.:
   "First public release of the reproducibility package. Corresponds to the
   manuscript submitted to journal."
5. **Publish release**

### 3.3. Recoger el DOI en Zenodo

Espera 1–2 minutos. Luego:

1. Ve a https://zenodo.org/account/settings/github/
2. Haz clic en tu repo → verás la nueva release archivada
3. Copia el **DOI** que aparece (formato: `10.5281/zenodo.XXXXXXXX`)
4. Verifica también el badge: `https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXXX.svg`

**Importante sobre versionado en Zenodo:** Zenodo asigna dos DOIs:
- Un DOI **específico de versión** (apunta a v1.0.0 exacta)
- Un DOI **conceptual** (apunta siempre a la última versión)

Para el paper se recomienda citar el **DOI conceptual** — así, si el revisor
te pide cambios y publicas una v1.0.1, el DOI del paper sigue siendo válido
y apunta automáticamente a la versión revisada.

---

## Fase 4 — Actualizar el manuscrito (5 minutos)

Sustituye en el manuscrito los marcadores que dejaste pendientes:

- En *Data and code availability* y en el *Abstract*:
  - `https://github.com/[to be added]` → `https://github.com/TU_USUARIO/edf-buffered-write`
  - `(DOI to be assigned upon acceptance)` → `(DOI: 10.5281/zenodo.XXXXXXXX)`

Y actualiza también el `README.md` y el `CITATION.cff` del repositorio con el
DOI real (sustituye los `XXXXXXXX`). Haz commit y push de esos cambios:

```bash
git add README.md CITATION.cff
git commit -m "Add Zenodo DOI to README and citation file"
git push origin main
```

(Estos cambios menores no requieren una nueva release: el DOI ya está
asignado a v1.0.0 y el archivo en Zenodo es inmutable.)

---

## Fase 5 — Comprobaciones finales antes de enviar a la revista de destino

- [ ] El repo es **público** (no privado)
- [ ] El badge del DOI de Zenodo aparece y enlaza correctamente
- [ ] Los scripts reproducen `metrics.json` con las cifras del paper
- [ ] Las Figuras 2, 3 y 4 del paper coinciden visualmente con las
      regeneradas por `make_figures.py`
- [ ] `pytest tests/` pasa sin errores en una instalación limpia
- [ ] El `LICENSE` está presente y es GPL-3.0
- [ ] El `CITATION.cff` está presente y es válido (puedes verificarlo en
      https://citation-file-format.github.io/)
- [ ] El manuscrito tiene el DOI real, no `XXXXXXXX`

---

## Errores comunes que un revisor te señalaría

1. **Repo privado.** El revisor abre el enlace y se topa con un 404. Rechazo
   automático en algunas revistas. Verifica el modo público desde una ventana
   de incógnito sin sesión iniciada en GitHub.

2. **DOI "to be assigned upon acceptance".** Hay revistas que lo aceptan,
   pero la revista de destino y la tendencia actual es exigir el DOI desde la submission.
   Habiendo hecho la Fase 3, ya no es un problema.

3. **`requirements.txt` con versiones flotantes** (`numpy>=1.20`). Un revisor
   meticuloso puede no poder reproducir tus números si pip instala una
   versión más reciente con cambios de comportamiento. Usa `==` con la versión
   exacta que utilizaste.

4. **Datos reales no incluidos ni descargables.** Si usas señales EMG reales
   en `test_roundtrip_real_emg.py`, el `data/real/README.md` debe explicar
   exactamente cómo obtenerlas: URL de PhysioNet con DOI, o consentimiento
   informado y depósito separado si son datos propios. No basta con "datos
   propios disponibles a petición razonada".

5. **Falta de tests reproducibles.** El revisor que abra el repo espera poder
   ejecutar `pytest` y ver pasar todo en menos de un minuto. Es la forma más
   rápida de convencerle de que tu solución funciona.
