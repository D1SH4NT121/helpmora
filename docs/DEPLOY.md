# Deploying HELPmora

HELPmora can be run locally or deployed to cloud platforms (such as Render, Hugging Face Spaces, or any Docker container host) with **zero mandatory API keys**.

---

## Local Deployment (Windows / Linux / macOS)

### Prerequisites
- Python 3.12+ (installed in virtual environment `.venv312`)
- Jaclang (`pip install jaclang jac-scale`)

### One-Click Startup (Windows)
```powershell
# PowerShell
.\run.ps1

# Or Command Prompt
run.bat
```
The server will start listening at: `http://localhost:8000/`.

---

## Docker Deployment

Build and run the container locally or on any cloud server:

```bash
# Build the Docker container image
docker build -t helpmora .

# Run container on port 8000 (or 7860)
docker run -p 8000:8000 helpmora
```

The container starts `cmguard` reverse gateway and the Jac application automatically.

---

## Deploying to Render (Free Tier)

Render provides free Docker web services directly from your GitHub repository:

1. **Push your code to GitHub:**
   Ensure your repository is synced with `https://github.com/D1SH4NT121/helpmora`.
2. **Create a Blueprint in Render:**
   - Log in to [Render](https://render.com).
   - Click **New +** -> **Blueprint**.
   - Connect your `D1SH4NT121/helpmora` repository.
   - Render reads [`render.yaml`](../render.yaml) and automatically configures the web service.
3. **Optional Environment Variables:**
   - `HELPMORA_JWT_SECRET`: Random 32+ character secret string.
   - (Optional) `OPENAI_API_KEY` or `GEMINI_API_KEY`: If you wish to enable cloud LLM rephrasing (purely optional; local heuristics run out-of-the-box).
4. **Deploy:** Click **Create Service**. Your app will be live at `https://<your-service>.onrender.com`.

---

## Verifying Deployment Health

Once booted, verify:
1. `GET /` returns HTTP 200 with the landing page.
2. Clicking **Enter the Navigator** opens `#chat`.
3. Graph seed loader confirms 40 seeded Indian welfare programs across housing, food, healthcare, and legal domains.
