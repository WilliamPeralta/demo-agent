# LangGraph Markdown Editor Agent

Un agente LangGraph che permette di editare un documento markdown tramite chat. Include una UI con pannello artifact laterale.

## Struttura

```
lang-agent/
├── src/agent/graph.py    # Agente LangGraph con tools per editare markdown
├── chat-ui/              # Frontend React (agent-chat-ui)
├── langgraph.json        # Configurazione LangGraph
└── .env                  # Variabili d'ambiente
```

## Setup

### 1. Configura le variabili d'ambiente

Modifica `.env` e aggiungi la tua API key OpenAI:

```bash
LANGSMITH_PROJECT=new-agent
LANGSMITH_API_KEY=lsv2_...
OPENAI_API_KEY=sk-...   # <-- Aggiungi la tua key qui
```

### 2. Installa le dipendenze Python

```bash
pip install -e . "langgraph-cli[inmem]"
```

### 3. Avvia il LangGraph Server

```bash
langgraph dev
```

Il server sara' disponibile su `http://localhost:2024`

### 4. Avvia la Chat UI (in un altro terminale)

```bash
cd chat-ui
pnpm install
pnpm dev
```

La UI sara' disponibile su `http://localhost:3000`

## Utilizzo

1. Apri `http://localhost:3000` nel browser
2. Inizia a chattare con l'agente
3. L'artifact markdown apparira' nel pannello laterale a destra
4. Puoi chiedere all'agente di:
   - Mostrare il documento attuale
   - Aggiungere nuove sezioni
   - Modificare parti specifiche del testo
   - Riscrivere completamente il documento

### Esempi di comandi

- "Mostrami il documento"
- "Aggiungi una sezione 'Conclusioni' alla fine"
- "Cambia il titolo in 'Il Mio Documento'"
- "Aggiungi una lista della spesa con 5 elementi"
- "Riscrivi il documento come una guida su Python"

## Architettura

L'agente ha accesso a 3 tools:

1. **update_document**: Sostituisce l'intero documento
2. **append_to_document**: Aggiunge contenuto alla fine
3. **replace_text**: Sostituisce parti specifiche del testo

Lo state del grafo include:
- `messages`: Lista dei messaggi della conversazione
- `artifact`: Il contenuto markdown del documento

## LangGraph Studio

Puoi anche usare LangGraph Studio per debuggare l'agente. Quando avvii `langgraph dev`, vedrai un link per aprire Studio nel browser.

## Sviluppo

Per modificare l'agente, edita `src/agent/graph.py`.

Per modificare la UI, edita i file in `chat-ui/src/`.
