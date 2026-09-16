# AI_agent_Ollama_tools
1. Vi bygger en lille lokal **AI-agent i Python** med Ollama og modellen `Qwen 2.5 3B`.
2. **LLM'en fungerer som agentens "hjerne"** og kan forstå spørgsmål, instruktioner og tekst.
3. Agenten har en **conversation memory**, som gemmes i Python-programmet.
4. Vi har givet agenten **tools**, så den kan udføre konkrete handlinger.
5. Den kan **læse filer, skrive tekst og kode til filer samt vise indholdet af directories**.
6. Agenten kan også **hente temperaturen i byer** gennem Open-Meteos API.
7. **Python fungerer som forbindelsen** mellem LLM'en, filsystemet og eksterne tjenester.
8. Agenten arbejder kun inden for det **directory, hvor `agent.py` ligger**.
9. Den kan **generere programmer og gemme dem**, men har endnu ikke mulighed for at køre kode.
10. Formålet er at lære, **hvordan en AI-agent fungerer**, gennem en enkel og overskuelig implementation.
