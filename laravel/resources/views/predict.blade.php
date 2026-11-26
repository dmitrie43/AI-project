<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Internal Assistant — Predict</title>
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
        main { max-width: 720px; margin: 0 auto; padding: 3rem 1.25rem 4rem; }
        .brand {
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 0.75rem;
        }
        nav { margin-bottom: 1.5rem; font-size: 0.9rem; }
        nav a { color: var(--accent); margin-right: 1rem; }
        h1 {
            font-size: clamp(1.6rem, 3vw, 2rem);
            font-weight: 600;
            margin: 0 0 0.5rem;
        }
        p.lead { color: var(--muted); margin: 0 0 2rem; line-height: 1.5; max-width: 36rem; }
        form {
            background: var(--panel);
            border: 1px solid var(--border);
            padding: 1.25rem;
            display: grid;
            gap: 1rem;
        }
        label { font-weight: 600; font-size: 0.9rem; display: grid; gap: 0.35rem; }
        input, select {
            background: #0a0e12;
            border: 1px solid var(--border);
            color: var(--ink);
            padding: 0.55rem 0.65rem;
            width: 100%;
        }
        button {
            background: var(--accent);
            color: #042f2e;
            border: 0;
            padding: 0.75rem 1rem;
            font-weight: 600;
            cursor: pointer;
        }
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
    </style>
</head>
<body>
<main>
    <div class="brand">Internal Assistant</div>
    <nav>
        <a href="{{ route('analyze.form') }}">Analyze CSV</a>
        <a href="{{ route('predict.form') }}">Predict</a>
        <a href="{{ route('ml.health') }}" target="_blank" rel="noreferrer">Health</a>
    </nav>
    <h1>Ticket predict</h1>
    <p class="lead">
        Send live features to ml-api <code>/predict</code>.
        Returns <code>is_open</code> class and probabilities from the trained model.
    </p>

    <form id="predict-form">
        <label>
            Category
            <select name="category" required>
                <option value="vpn">vpn</option>
                <option value="access">access</option>
                <option value="hardware">hardware</option>
                <option value="billing">billing</option>
                <option value="onboarding">onboarding</option>
            </select>
        </label>
        <label>
            Priority (1–5, optional)
            <input name="priority" type="number" min="1" max="5" step="1" value="4">
        </label>
        <label>
            Satisfaction (1–5, optional)
            <input name="satisfaction" type="number" min="1" max="5" step="1" placeholder="empty ok">
        </label>
        <label>
            Tag count
            <input name="tag_count" type="number" min="0" max="50" step="1" value="2">
        </label>
        <button type="submit">Run predict</button>
    </form>

    <pre id="out">{}</pre>
</main>
<script>
const form = document.getElementById('predict-form');
const out = document.getElementById('out');
const csrf = document.querySelector('meta[name="csrf-token"]')?.content;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = {
        category: fd.get('category'),
        priority: fd.get('priority') === '' ? null : Number(fd.get('priority')),
        satisfaction: fd.get('satisfaction') === '' ? null : Number(fd.get('satisfaction')),
        tag_count: fd.get('tag_count') === '' ? 0 : Number(fd.get('tag_count')),
    };

    out.textContent = 'Running…';
    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRF-TOKEN': csrf,
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
            body: JSON.stringify(payload),
        });
        const text = await res.text();
        let json;
        try { json = JSON.parse(text); }
        catch { out.textContent = `HTTP ${res.status}:\n${text.slice(0, 500)}`; return; }
        out.textContent = JSON.stringify(json, null, 2);
    } catch (err) {
        out.textContent = String(err);
    }
});
</script>
</body>
</html>
