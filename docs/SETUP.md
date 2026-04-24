# Setup & Installation

This project supports two installation modes:

- **Mode A: Windows + WSL (Ubuntu)**
- **Mode B: Native Ubuntu/Linux**

Use path placeholders below so the commands stay valid regardless of where you keep your repos.

| Placeholder    | Meaning                                               |
| -------------- | ----------------------------------------------------- |
| `<IMPL_DIR>`   | Absolute path to this repo (`d4j_odc_implementation`) |
| `<D4J_HOME>`   | Absolute path to your Defects4J clone                 |
| `<LINUX_USER>` | Your Linux username                                   |

Example: `<IMPL_DIR>` might be `C:\dev\thesis\d4j_odc_implementation` on Windows, or `/home/alex/dev/d4j_odc_implementation` on Ubuntu.

`<D4J_HOME>` is defined by where you clone Defects4J. If you use the default clone command below, it will usually be the absolute path of a `defects4j` directory.

---

## Mode A - Windows + WSL (Ubuntu)

### 1) Prerequisites

- Windows: Python 3.11+
- WSL: Ubuntu installed and working
- Recommended layout: keep `<IMPL_DIR>` on Windows, keep `<D4J_HOME>` inside WSL Linux filesystem

### 2) Install Defects4J dependencies in WSL

```bash
sudo apt update
sudo apt install -y openjdk-11-jdk git subversion perl cpanminus curl unzip
git config --global core.autocrlf input
```

### 3) Clone and initialize Defects4J in WSL

```bash
cd /home/<LINUX_USER>
git clone https://github.com/rjust/defects4j.git
cd defects4j
export D4J_HOME="$(pwd)"
sudo cpanm --installdeps .
./init.sh
perl framework/bin/defects4j info -p Lang
```

If `info -p Lang` fails with missing Perl modules (for example `String::Interpolate`):

```bash
sudo cpanm String::Interpolate
sudo cpanm --installdeps <D4J_HOME>
```

### 4) Create Python environment in Windows repo

```powershell
cd <IMPL_DIR>

python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
# or: .venv\Scripts\activate.bat    # CMD

pip install -r requirements.txt
pip install -e .
```

### 5) Configure `.env` (WSL mode)

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key_here
DEFECTS4J_CMD=wsl perl <D4J_HOME>/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=wsl
```

---

## Mode B - Native Ubuntu/Linux

### 1) Prerequisites

```bash
sudo apt update
sudo apt install -y openjdk-11-jdk git subversion perl cpanminus curl unzip
```

### 2) Clone and initialize Defects4J

```bash
git clone https://github.com/rjust/defects4j.git
cd defects4j
export D4J_HOME="$(pwd)"
sudo cpanm --installdeps .
./init.sh
perl framework/bin/defects4j info -p Lang
```

If `info -p Lang` fails with missing Perl modules:

```bash
sudo cpanm String::Interpolate
sudo cpanm --installdeps <D4J_HOME>
```

### 3) Create Python environment in implementation repo

```bash
cd <IMPL_DIR>
python3 -m venv .venv

# If venv creation fails with "ensurepip is not available":
# sudo apt install -y python3-venv
# (or version-specific package, e.g. python3.12-venv)

source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 4) Configure `.env` (native Linux mode)

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key_here
DEFECTS4J_CMD=perl <D4J_HOME>/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=native
```

---

## Quick Validation (both modes)

```bash
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
```

If validation fails with `Can't open perl script .../framework/bin/defects4j`, verify that `<D4J_HOME>` in `DEFECTS4J_CMD` matches your actual clone location exactly.

---

## Provider Options

| Provider            | Default key env var  | Default base URL                                   |
| ------------------- | -------------------- | -------------------------------------------------- |
| `gemini`            | `GEMINI_API_KEY`     | `https://generativelanguage.googleapis.com/v1beta` |
| `openrouter`        | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1`                     |
| `openai-compatible` | `OPENAI_API_KEY`     | `https://api.openai.com/v1`                        |

OpenRouter example:

```dotenv
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=openai/gpt-5.2
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://your-site.example
OPENROUTER_APP_TITLE=Defects4J ODC Pipeline
```
