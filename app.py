from flask import Flask, render_template_string, request, jsonify, Response
import requests
import json
import csv
import io
import re
import sys
import os

SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    pass

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consulta Miembro de Mesa - ONPE</title>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --blue: #2563eb;
            --blue-dark: #1d4ed8;
            --blue-light: #dbeafe;
            --green: #1e8449;
            --green-light: #eafaf1;
            --gray: #6c757d;
            --gray-light: #f4f5f7;
            --border: #dde1e7;
            --text: #1a1a2e;
            --text-muted: #6b7280;
            --white: #ffffff;
            --red: #2563eb;
            --red-dark: #1d4ed8;
            --red-light: #dbeafe;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'IBM Plex Sans', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 30px 20px;
        }

        .wrapper {
            max-width: 1100px;
            margin: 0 auto;
        }

        /* HEADER */
        .header {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 22px 30px;
            border-radius: 10px 10px 0 0;
            display: flex;
            align-items: center;
            gap: 14px;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
        }
        .header-icon { font-size: 32px; }
        .header h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }
        .header p { font-size: 13px; opacity: 0.85; margin-top: 2px; }

        /* CARD */
        .card {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: none;
            padding: 28px 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .card:last-child { border-radius: 0 0 10px 10px; }

        /* TEXTAREA SECTION */
        .input-label {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 10px;
            line-height: 1.5;
        }
        .input-label strong { color: var(--text); }

        textarea {
            width: 100%;
            height: 160px;
            padding: 14px;
            border: 1.5px solid var(--border);
            border-radius: 7px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.2s;
            color: var(--text);
            background: #fafafa;
        }
        textarea:focus { outline: none; border-color: var(--red); background: white; }

        .input-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
            font-size: 12px;
            color: var(--text-muted);
        }
        .dni-count strong { color: var(--red); }

        /* BUTTONS */
        .btn-row { display: flex; gap: 10px; margin-top: 16px; }

        .btn {
            padding: 11px 24px;
            border: none;
            border-radius: 6px;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 7px;
        }
        .btn-primary { background: var(--red); color: white; }
        .btn-primary:hover { background: var(--red-dark); }
        .btn-primary:disabled { background: #ccc; cursor: not-allowed; }
        .btn-secondary { background: #5a6473; color: white; }
        .btn-secondary:hover { background: #3d4451; }

        /* DIVIDER */
        .divider { height: 1px; background: var(--border); margin: 0; }

        /* RESULTS HEADER */
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            flex-wrap: wrap;
            gap: 12px;
        }
        .results-title { font-size: 20px; font-weight: 700; }

        .badges { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .badge {
            padding: 5px 13px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-green { background: var(--green); color: white; }
        .badge-gray { background: #e2e8f0; color: #374151; border: 1px solid #cbd5e0; }

        .btn-excel {
            background: #1e6b35;
            color: white;
            padding: 9px 18px;
            border: none;
            border-radius: 6px;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: background 0.15s;
        }
        .btn-excel:hover { background: #155228; }

        /* TABLE */
        .table-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }

        thead tr { background: var(--red); color: white; }
        thead th {
            padding: 12px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }

        tbody tr { border-bottom: 1px solid var(--border); transition: background 0.1s; }
        tbody tr:last-child { border-bottom: none; }
        tbody tr:hover { background: #fafafa; }
        tbody td { padding: 11px 14px; vertical-align: middle; }

        .td-num { color: var(--text-muted); font-size: 12px; }
        .td-dni { font-family: 'IBM Plex Mono', monospace; font-weight: 500; }
        .td-nombres { font-weight: 500; }

        .pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
        }
        .pill-si { background: var(--green-light); color: var(--green); }
        .pill-no { background: #fef2f2; color: var(--red); }

        .rol-text { font-size: 12px; color: var(--text-muted); }

        /* LOADING */
        .loading-row td {
            text-align: center;
            padding: 30px;
            color: var(--text-muted);
            font-size: 14px;
        }
        .spinner {
            display: inline-block;
            width: 18px; height: 18px;
            border: 2px solid #ddd;
            border-top-color: var(--red);
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }
        .empty-state .icon { font-size: 36px; margin-bottom: 10px; }
        .empty-state p { font-size: 14px; }

        /* PROGRESS */
        .progress-bar-wrap {
            display: none;
            margin-top: 14px;
        }
        .progress-bar-wrap.visible { display: block; }
        .progress-label { font-size: 12px; color: var(--text-muted); margin-bottom: 5px; }
        .progress-bar-bg { background: #e5e7eb; border-radius: 4px; height: 6px; }
        .progress-bar-fill {
            height: 6px;
            background: var(--red);
            border-radius: 4px;
            transition: width 0.3s;
            width: 0%;
        }
    </style>
</head>
<body>
<div class="wrapper">

    <!-- HEADER -->
    <div class="header">
        <div class="header-icon">🗳️</div>
        <div>
            <h1>Consulta Miembro de Mesa - ONPE</h1>
        </div>
    </div>

    <!-- INPUT CARD -->
    <div class="card">
        <textarea id="dniInput" placeholder="75414326&#10;76578509&#10;..."></textarea>
        <div class="input-footer">
            <span class="dni-count">DNIs ingresados: <strong id="dniCounter">0</strong></span>
        </div>
        <div class="progress-bar-wrap" id="progressWrap">
            <div class="progress-label" id="progressLabel">Consultando...</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" id="progressFill"></div></div>
        </div>
        <div class="btn-row">
            <button class="btn btn-primary" id="btnConsultar" onclick="consultar()">🔍 Consultar</button>
            <button class="btn btn-secondary" onclick="limpiar()">✖ Limpiar</button>
        </div>
    </div>

    <div class="divider"></div>

    <!-- RESULTS CARD -->
    <div class="card">
        <div class="results-header">
            <span class="results-title">Resultados</span>
            <div class="badges">
                <span class="badge badge-green" id="badgeMiembros">Miembros: 0</span>
                <span class="badge badge-gray" id="badgeTotal">Total consultados: 0</span>
                <button class="btn-excel" onclick="descargarExcel()" id="btnExcel" style="display:none">
                    📥 Descargar Excel
                </button>
            </div>
        </div>

        <div class="table-wrap">
            <table id="tablaResultados">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>DNI</th>
                        <th>Miembro?</th>
                        <th>Rol</th>
                        <th>Nombres</th>
                        <th>Region</th>
                        <th>Provincia</th>
                        <th>Distrito</th>
                    </tr>
                </thead>
                <tbody id="tablaBody">
                    <tr>
                        <td colspan="8">
                            <div class="empty-state">
                                <div class="icon">📋</div>
                                <p>Ingresa uno o más DNIs y haz clic en <strong>Consultar</strong></p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

</div>

<script>
    let resultados = [];

    const dniInput = document.getElementById('dniInput');
    const dniCounter = document.getElementById('dniCounter');
    const tablaBody = document.getElementById('tablaBody');
    const badgeMiembros = document.getElementById('badgeMiembros');
    const badgeTotal = document.getElementById('badgeTotal');
    const btnConsultar = document.getElementById('btnConsultar');
    const btnExcel = document.getElementById('btnExcel');
    const progressWrap = document.getElementById('progressWrap');
    const progressFill = document.getElementById('progressFill');
    const progressLabel = document.getElementById('progressLabel');

    dniInput.addEventListener('input', () => {
        const dnis = parseDNIs(dniInput.value);
        dniCounter.textContent = dnis.length;
    });

    function parseDNIs(text) {
        return text.split(/[\\n,;\\s]+/)
            .map(d => d.trim())
            .filter(d => /^\\d{8}$/.test(d));
    }

    async function consultar() {
        const dnis = parseDNIs(dniInput.value);
        if (dnis.length === 0) {
            alert('Por favor ingresa al menos un DNI válido de 8 dígitos.');
            return;
        }

        resultados = [];
        btnConsultar.disabled = true;
        btnExcel.style.display = 'none';
        progressWrap.classList.add('visible');

        tablaBody.innerHTML = `<tr class="loading-row"><td colspan="8"><span class="spinner"></span> Consultando ${dnis.length} DNI(s)...</td></tr>`;

        for (let i = 0; i < dnis.length; i++) {
            const dni = dnis[i];
            const pct = Math.round(((i) / dnis.length) * 100);
            progressFill.style.width = pct + '%';
            progressLabel.textContent = `Consultando ${i + 1} de ${dnis.length}: ${dni}`;

            try {
                const res = await fetch('/consultar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dni })
                });
                const data = await res.json();
                resultados.push({ dni, ...data });
            } catch (e) {
                resultados.push({ dni, error: true, nombres: 'Error de conexión' });
            }
        }

        progressFill.style.width = '100%';
        progressLabel.textContent = '¡Consulta completada!';
        setTimeout(() => progressWrap.classList.remove('visible'), 1200);

        renderTabla();
        btnConsultar.disabled = false;
        if (resultados.length > 0) btnExcel.style.display = 'flex';
    }

    function renderTabla() {
        if (resultados.length === 0) {
            tablaBody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="icon">📋</div><p>Sin resultados</p></div></td></tr>';
            return;
        }

        const miembros = resultados.filter(r => r.es_miembro).length;
        badgeMiembros.textContent = `Miembros: ${miembros}`;
        badgeTotal.textContent = `Total consultados: ${resultados.length}`;

        tablaBody.innerHTML = resultados.map((r, i) => `
            <tr>
                <td class="td-num">${i + 1}</td>
                <td class="td-dni">${r.dni}</td>
                <td><span class="pill ${r.es_miembro ? 'pill-si' : 'pill-no'}">${r.es_miembro ? 'SÍ' : 'NO'}</span></td>
                <td class="rol-text">${r.rol || (r.es_miembro ? 'MIEMBRO DE MESA' : 'NO ERES MIEMBRO DE MESA')}</td>
                <td class="td-nombres">${r.nombres || '-'}</td>
                <td>${r.region || '-'}</td>
                <td>${r.provincia || '-'}</td>
                <td>${r.distrito || '-'}</td>
            </tr>
        `).join('');
    }

    function limpiar() {
        dniInput.value = '';
        dniCounter.textContent = '0';
        resultados = [];
        btnExcel.style.display = 'none';
        badgeMiembros.textContent = 'Miembros: 0';
        badgeTotal.textContent = 'Total consultados: 0';
        tablaBody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><div class="icon">📋</div><p>Ingresa uno o más DNIs y haz clic en <strong>Consultar</strong></p></div></td></tr>`;
    }

    function descargarExcel() {
        fetch('/exportar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resultados })
        }).then(res => res.blob()).then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'consulta_miembro_mesa.csv';
            a.click();
            URL.revokeObjectURL(url);
        });
    }
</script>
</body>
</html>
"""

def consultar_onpe_selenium(dni):
    if not SELENIUM_AVAILABLE:
        return None

    driver = None
    try:
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--disable-software-rasterizer')
        opts.add_argument('--disable-extensions')
        opts.add_argument('--remote-debugging-port=9222')
        opts.add_argument('--window-size=1920,1080')
        opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        opts.add_experimental_option('useAutomationExtension', False)
        
        # Para Docker Alpine
        if os.path.exists('/usr/bin/chromium'):
            opts.binary_location = '/usr/bin/chromium'

        driver = webdriver.Chrome(options=opts)
        driver.get('https://consultaelectoral.onpe.gob.pe/inicio')

        import time
        time.sleep(20)

        dni_input = driver.find_element(By.ID, 'mat-input-0')
        dni_input.clear()
        dni_input.send_keys(dni)

        time.sleep(2)

        buscar_btn = driver.find_element(By.CSS_SELECTOR, 'button.button_consulta')
        buscar_btn.click()

        time.sleep(8)

        page = driver.page_source

        page_lower = page.lower()
        
        es_miembro = False
        rol = "NO ES MIEMBRO"
        
        if 'no eres miembro' in page_lower or 'no es miembro' in page_lower:
            es_miembro = False
            rol = "NO ES MIEMBRO"
        elif 'miembro de mesa' in page_lower and 'card card-1' in page:
            es_miembro = True
            if 'titular' in page_lower:
                rol = "TITULAR"
            elif 'primer suplente' in page_lower:
                rol = "PRIMER SUPLENTE"
            elif 'segundo suplente' in page_lower:
                rol = "SEGUNDO SUPLENTE"
            elif 'tercer suplente' in page_lower:
                rol = "TERCER SUPLENTE"
            elif 'cuarto suplente' in page_lower:
                rol = "CUARTO SUPLENTE"
            elif 'quinto suplente' in page_lower:
                rol = "QUINTO SUPLENTE"
            else:
                rol = "MIEMBRO DE MESA"

        nombres_match = re.search(r'class="apellido">([^<]+)<', page)
        nombres = nombres_match.group(1).strip() if nombres_match else '-'

        nombre2_match = re.search(r'class="nombre">\s*(\w+ \w+)\s*<', page)
        if not nombres_match and nombre2_match:
            nombres = nombre2_match.group(1).strip()

        ubicacion_match = re.search(r'class="local">([^<]+)<', page)
        if ubicacion_match:
            ubicacion = ubicacion_match.group(1).strip()
            parts = ubicacion.split(' / ')
            region = parts[0] if len(parts) > 0 else '-'
            provincia = parts[1] if len(parts) > 1 else '-'
            distrito = parts[2] if len(parts) > 2 else '-'
        else:
            region = provincia = distrito = '-'

        local = region if region != '-' else '-'
        direccion = '-'

        return {
            "es_miembro": es_miembro,
            "nombres": nombres,
            "rol": rol,
            "region": region,
            "provincia": provincia,
            "distrito": distrito,
            "local": local,
            "direccion": direccion
        }

    except Exception as e:
        print(f"Selenium error: {e}", file=sys.stderr)
        return None
    finally:
        if driver:
            driver.quit()


def consultar_onpe(dni):
    result = consultar_onpe_selenium(dni)
    if result:
        return result

    return {"es_miembro": False, "nombres": "Error al consultar ONPE", "rol": "", "region": "", "provincia": "", "distrito": "", "local": "", "direccion": "", "error": True}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/consultar", methods=["POST"])
def consultar():
    data = request.get_json()
    dni = data.get("dni", "").strip()
    if not re.match(r'^\d{8}$', dni):
        return jsonify({"es_miembro": False, "nombres": "DNI inválido", "error": True})
    resultado = consultar_onpe(dni)
    return jsonify(resultado)

@app.route("/exportar", methods=["POST"])
def exportar():
    data = request.get_json()
    resultados = data.get("resultados", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["#", "DNI", "Miembro?", "Rol", "Nombres", "Region", "Provincia", "Distrito"])

    for i, r in enumerate(resultados, 1):
        writer.writerow([
            i,
            r.get("dni", ""),
            "SÍ" if r.get("es_miembro") else "NO",
            r.get("rol", ""),
            r.get("nombres", ""),
            r.get("region", ""),
            r.get("provincia", ""),
            r.get("distrito", "")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=consulta_miembro_mesa.csv"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
