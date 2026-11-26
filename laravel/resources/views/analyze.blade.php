<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Internal Assistant — Analyze</title>
    <style>
        :root {
            --bg: #0f1419;
            --panel: #1a222c;
            --ink: #e7ecf1;
            --muted: #9aa7b5;
            --accent: #2dd4bf;
            --border: #2a3542;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
            background: var(--bg);
            color: var(--ink);
            min-height: 100vh;
        }
        main {
            max-width: 720px;
            margin: 0 auto;
            padding: 3rem 1.25rem 4rem;
        }
        .brand {
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 0.75rem;
        }
        h1 {
            font-size: clamp(1.6rem, 3vw, 2rem);
            font-weight: 600;
            letter-spacing: -0.02em;
            margin: 0 0 0.5rem;
        }
        p.lead {
            color: var(--muted);
            margin: 0 0 2rem;
            line-height: 1.5;
            max-width: 36rem;
        }
        form {
            background: var(--panel);
            border: 1px solid var(--border);
            padding: 1.25rem;
            display: grid;
            gap: 1rem;
        }
        label { font-weight: 600; font-size: 0.9rem; }
        input[type=file] { width: 100%; color: var(--muted); }
        button {
            background: var(--accent);
            color: #042f2e;
            border: 0;
            padding: 0.75rem 1rem;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover { filter: brightness(1.06); }
        pre {
            background: #0a0e12;
            border: 1px solid var(--border);
            color: #a7f3d0;
            padding: 1rem;
            overflow: auto;
            min-height: 8rem;
            margin-top: 1.5rem;
            font-size: 0.85rem;
        }
        .meta { color: var(--muted); font-size: 0.85rem; margin-top: 1rem; }
        a { color: var(--accent); }
    </style>
</head>
<body>
<main>
    <div class="brand">Internal Assistant</div>
    <p class="meta" style="margin-top:0;margin-bottom:1.25rem">
        <a href="{{ route('predict.form') }}">Predict</a>
        ·
        <a href="{{ route('ml.health') }}" target="_blank" rel="noreferrer">Health</a>
    </p>
    <h1>Dataset analyze</h1>
    <p class="lead">
        Upload a CSV. The gateway calls the ML service and caches identical payloads in Redis.
    </p>

    <form id="analyze-form">
        <label for="file">CSV file</label>
        <input id="file" name="file" type="file" accept=".csv,text/csv" required>
        <button type="submit">Run analyze</button>
    </form>

    <p class="meta">
        Service health:
        <a href="/ml-health" target="_blank" rel="noreferrer">/ml-health</a>
    </p>

    <pre id="out">{}</pre>
</main>
<script>
const form = document.getElementById('analyze-form');
const out = document.getElementById('out');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('file');
    if (!fileInput.files.length) return;

    const body = new FormData();
    body.append('file', fileInput.files[0]);

    const csrf = document.querySelector('meta[name="csrf-token"]')?.content;

    out.textContent = 'Running…';
    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'X-CSRF-TOKEN': csrf,
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body,
            credentials: 'same-origin',
        });

        const text = await res.text();
        let payload;
        try {
            payload = JSON.parse(text);
        } catch {
            out.textContent = `HTTP ${res.status}: expected JSON, got HTML/text:\n${text.slice(0, 500)}`;
            return;
        }

        if (!res.ok) {
            out.textContent = JSON.stringify({ status: res.status, ...payload }, null, 2);
            return;
        }

        out.textContent = JSON.stringify(payload, null, 2);
    } catch (err) {
        out.textContent = String(err);
    }
});
</script>
</body>
</html>
