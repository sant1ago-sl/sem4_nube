# Consulta Miembro de Mesa - ONPE 🗳️

Aplicación web para consultar si un ciudadano es miembro de mesa para las elecciones, usando el portal oficial de ONPE mediante scraping con Selenium.

## Características

- Consulta si eres **miembro de mesa** (titular o suplente)
- Detecta el rol: TITULAR, PRIMER SUPLENTE, SEGUNDO SUPLENTE, TERCER SUPLENTE, CUARTO SUPLENTE, QUINTO SUPLENTE
- Muestra ubicación: Región, Provincia, Distrito
- Interfaz web intuitiva
- Exporta resultados a CSV

---

## Instalación Paso a Paso

### 1. Instalar Python

Descarga e instala Python 3.11 o superior desde: https://python.org/downloads

**Importante:** Durante la instalación, marca la opción **"Add Python to PATH"**

### 2. Instalar Chrome

Descarga e instala Google Chrome desde: https://google.com/chrome

### 3. Clonar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd caso2
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

### 6. Abrir en el navegador

Ve a: **http://localhost:5000**

---

## Estructura del proyecto

```
caso2/
├── app.py                  # Aplicación Flask principal
├── requirements.txt        # Dependencias de Python
├── Dockerfile              # Imagen base
├── Dockerfile.optimizado   # Imagen Alpine
├── Dockerfile.multistage  # Multi-stage
├── .dockerignore
└── README.md             # Este archivo
```

---

## Construcción con Docker (Opcional)

### Dockerfile base
```bash
docker build -t onpe-app .
docker run -d -p 5000:5000 --name onpe onpe-app
```

### Dockerfile optimizado
```bash
docker build -f Dockerfile.optimizado -t onpe-app:opt .
docker run -d -p 5000:5000 --name onpe onpe-app:opt
```

---

## Cómo usar la aplicación

1. Abre **http://localhost:5000**
2. Ingresa el número de DNI (8 dígitos)
3. Haz clic en **Consultar**
4. Verás el resultado con:
   - Si es miembro de mesa (Sí/No)
   - El rol (TITULAR, SUPLENTE, etc.)
   - Nombres completos
   - Ubicación (Región/Provincia/Distrito)
5. Puedes exportar los resultados a CSV

---

## Solución de problemas

### Error: "selenium not found"
```bash
pip install selenium webdriver-manager
```

### Error: "Chrome not found"
确保 tienes Chrome instalado. También puedes instalar webdriver:
```bash
pip install webdriver-manager
```

### Error: "Port 5000 in use"
Cambia el puerto en app.py o usa:
```bash
python app.py  # Ya usa el puerto 5000 por defecto
```

---

## Fuente oficial

[https://consultaelectoral.onpe.gob.pe/inicio](https://consultaelectoral.onpe.gob.pe/inicio)