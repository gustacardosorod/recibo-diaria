# Gerador de Recibo de Diária — Viação Águia Branca

Aplicação Flask para geração de recibos de diária de motoristas com download em PDF.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py
# Acesse: http://localhost:5000
```

## Hospedagem gratuita — Render.com (recomendado)

1. Crie uma conta em https://render.com (gratuito)
2. Crie um novo repositório no GitHub e envie todos estes arquivos
3. No Render: **New → Web Service → conecte o repositório**
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Clique em **Deploy** — em ~2 minutos você terá um link público!

## Alternativa — Railway.app

1. Acesse https://railway.app
2. **New Project → Deploy from GitHub repo**
3. Selecione o repositório — o Railway detecta automaticamente o Procfile
4. Variável de ambiente: nenhuma necessária
5. Domínio gerado automaticamente

## Configurando os CNPJs

Abra `app.py` e edite a lista `CNPJS` no início do arquivo:

```python
CNPJS = [
    {"label": "Viação Águia Branca S/A – Matriz",    "value": "12.345.678/0001-90"},
    {"label": "Viação Águia Branca S/A – Filial ES", "value": "12.345.678/0002-71"},
    # Adicione quantos precisar...
]
```

## Estrutura do projeto

```
aguia-branca/
├── app.py              ← Servidor Flask + geração de PDF
├── templates/
│   └── index.html      ← Interface web
├── requirements.txt    ← Dependências Python
├── Procfile            ← Comando de start (Render/Railway)
├── runtime.txt         ← Versão do Python
└── README.md
```
