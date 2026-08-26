# Mai-inspired municipal citizen-service chatbot stub (demo target)
# Intentionally incomplete governance artefacts for Aegis to find.

## Purpose
Public-service chatbot for a Dutch municipality answering questions about
social benefits, appointments, and waste collection. Citizens interact via
a web widget on the municipal portal.

## System characteristics
- Conversational agent / municipal chatbot for essential public services
- LLM assistant with retrieval over municipal policy PDFs
- No human oversight escalation documented yet
- Training data scraped from public forums (historical)
- Zip code scoring used in a side experiment for "service urgency"
- No rate limit on the public widget
- System prompt stored in repo; untrusted tool output concatenated into context

## Known gaps
- Missing model card
- Missing data sheet / bias audit
- No instructions for use for deployers
- No risk register
