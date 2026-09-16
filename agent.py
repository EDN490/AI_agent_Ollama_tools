# Senest opdateret: 16. september 2026 kl. 08:20 zzz


"""
Lokal AI-agent med Ollama og Qwen 2.5 3B
========================================

Dette program viser grundprincipperne i en simpel AI-agent.

Agenten består af:

    - en LLM
    - conversation memory
    - tools
    - et agent-loop

LLM'en fungerer som agentens "hjerne".

Den kan blandt andet:

    - besvare almindelige spørgsmål
    - forstå instruktioner
    - forklare programmering og andre emner
    - generere programmer og kode
    - generere tekst og andet indhold
    - beslutte, hvornår et tool skal bruges

Python-programmet fungerer som forbindelsen mellem LLM'en
og den virkelige verden.

Agenten har følgende tools:

    read_file()
        Læser en tekstfil.

    write_file()
        Skriver tekst eller kode til en fil.

    list_directory()
        Viser filer og mapper i et directory.

    get_weather()
        Henter den aktuelle temperatur for en by
        via Open-Meteo.

Agenten kan IKKE køre kode.

Agenten arbejder kun i det directory, hvor agent.py ligger.

Installation
============

Windows
-------

Installer Python.

Installer Ollama.

Hent modellen:

    ollama run qwen2.5:3b

Installer Ollama Python-pakken:

    python -m pip install ollama


Linux
-----

Installer Ollama:

    curl -fsSL https://ollama.com/install.sh | sh

Hent modellen:

    ollama run qwen2.5:3b

Installer Python og pip hvis det er nødvendigt:

    sudo apt update
    sudo apt install python3 python3-pip

På nyere Linux-systemer kan pip være beskyttet af PEP 668.
I så fald bruger vi et Python virtual environment.

Installer venv:

    sudo apt update
    sudo apt install python3-venv

Opret et virtual environment:

    python3 -m venv ~/ollama-env

Aktiver det:

    source ~/ollama-env/bin/activate

Installer Ollama Python-pakken:

    pip install ollama

Hver gang agent.py skal afprøves i en ny terminal,
skal virtual environment aktiveres først:

    source ~/ollama-env/bin/activate

Derefter kan agenten startes:

    cd /sti/til/agent
    python agent.py


Installationen er afprøvet på:

    Windows 10 PC med 4 GB RAM
    Raspberry Pi 5 med 8 GB RAM


Model
=====

Vi bruger:

    qwen2.5:3b

"B" står for "billion" og bruges her efter den engelske
short-scale talbetydning.

3B betyder derfor 3 milliarder, altså:

    3.000.000.000 parametre


Conversation memory
==================

LLM'en har ikke selv en permanent hukommelse mellem
de enkelte kald.

I stedet gemmer Python-programmet samtalen i listen
"messages".

Hele samtalen sendes med til LLM'en ved hvert kald.

Memory findes derfor kun, mens programmet kører.

Hvis programmet afsluttes, forsvinder denne memory.

Listen indeholder beskeder med forskellige roller:
#
#     - system
#     - user
#     - assistant
#     - tool
#
# Rollen fortæller LLM'en, hvilken type besked der er tale om.
#
# system
#     Instruktioner til LLM'en.
#
# user
#     En besked fra brugeren.
#
# assistant
#     Et tidligere svar fra LLM'en.
#
# tool
#     Resultatet fra et tool, som Python har kørt.


Agent-loop
==========

Agenten arbejder i et loop.

1. Brugeren skriver en besked.

2. Beskeden sendes til LLM'en.

3. LLM'en vurderer, om den kan svare direkte,
   eller om den skal bruge et tool.

4. Hvis der skal bruges tools, sender LLM'en
   en eller flere tool calls til Python.

5. Python udfører alle de ønskede tools.

6. Resultaterne sendes tilbage til LLM'en.

7. LLM'en venter på tool-resultaterne og laver
   derefter det endelige svar.

8. Svaret vises til brugeren.


Tools
=====

LLM'en kan ikke selv læse filer, skrive filer
eller hente data fra internettet.

Den kan kun udføre handlinger, som programmet
giver den tools til.

Eksempler på tools kunne være:

    execute_program
    query_database
    call_api
    search_web
    send_email
    get_weather
    create_image

LLM'en behøver ikke kende den interne implementation
af et tool.

Den kan i stedet bede Python om at bruge et tool.

Python udfører handlingen og sender resultatet
tilbage til LLM'en.


Workspace
=========

Agenten må kun arbejde i det directory,
hvor agent.py ligger.

Det bestemmes med:

    WORKSPACE = Path(__file__).resolve().parent

safe_path() kontrollerer, at filer og mapper
ligger inden for dette workspace.


Eksempler
=========

Du kan eksempelvis spørge:

    Hvilke lande er nabolande til Danmark?

    Hvilke filer ligger i det aktuelle directory?

    Læs test.txt og fortæl mig hvad der står.

    Lav et python-program der beregner Fibonacci-tal
    og gem det som fibonacci.py

Vejret:

    Hvad er temperaturen i København?

    Hvad er temperaturen i London?


Begrænsning
===========

Agenten kan generere programmer og gemme dem i filer.

Agenten kan IKKE køre programmer.

Der findes derfor ikke noget execute_program-tool
i denne version.
"""


from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
import json


# Ollama er navnet på den lokale AI-platform, som vi bruger
# til at køre og kommunikere med vores LLM.
#
# Navnet er spansk-inspireret, og "ll" kan derfor udtales
# med en j-/y-lignende lyd.
#
# Ollama udtales derfor cirka:
#
#     "o-JA-ma"
#
# Udtalen kan variere, men dette er en spansk-inspireret
# måde at udtale navnet på.
from ollama import Client


# Den LLM-model som agenten bruger.
MODEL = "qwen2.5:3b"


# Workspace er det directory, hvor agent.py ligger.
#
# __file__
#     Er stien til denne Python-fil.
#
# resolve()
#     Gør stien absolut.
#
# parent
#     Finder directory'et som filen ligger i.
WORKSPACE = Path(__file__).resolve().parent


# Sikkerhedsbegrænsning:
#
# Agenten må højst udføre 5 tool calls for én
# brugerbesked.
MAX_TOOL_CALLS = 5


# Forbindelse til Ollama.
client = Client()


# Conversation memory.
#
# Hele samtalen gemmes i denne liste.
messages = [
    {
        "role": "system",
        "content": """
Du er en lokal AI-agent.

Du kan svare på almindelige spørgsmål og hjælpe
med programmering og andre opgaver.

Du har adgang til tools, som Python-programmet
kan udføre for dig.

Brug read_file til at læse filer.

Brug write_file til at skrive tekst eller kode
til filer.

Brug list_directory til at vise filer og mapper
i et directory.

Brug get_weather, når brugeren spørger om den aktuelle
temperatur eller vejret i en bestemt by.

Når du kalder get_weather, skal bynavnet altid angives
på engelsk.

Eksempel:

Brugeren:
    Hvad er temperaturen i København?

Tool call:
    get_weather(city="Copenhagen")

Hvis brugeren beder dig om at lave et program,
kan du generere koden og bruge write_file til
at gemme den i en fil.

Du må ikke forsøge at køre programmer.

Du må kun arbejde med filer inden for agentens
workspace.

Svar på dansk, medmindre brugeren skriver på et
andet sprog.
"""
    }
]


def safe_path(path: str) -> Path:
    """
    Kontrollerer at en fil eller mappe ligger
    inden for agentens workspace.
    """

    requested_path = Path(path)

    if requested_path.is_absolute():
        full_path = requested_path.resolve()
    else:
        full_path = (WORKSPACE / requested_path).resolve()

    try:
        full_path.relative_to(WORKSPACE)
    except ValueError:
        raise ValueError(
            "Adgang nægtet: Stien ligger uden for workspace."
        )

    return full_path


def read_file(path: str) -> str:
    """
    Læser indholdet af en tekstfil.
    """

    try:
        file_path = safe_path(path)

        if not file_path.is_file():
            return f"Filen findes ikke: {path}"

        return file_path.read_text(
            encoding="utf-8"
        )

    except Exception as e:
        return f"Fejl ved læsning af fil: {e}"


def write_file(path: str, content: str) -> str:
    """
    Skriver tekst til en fil.
    """

    try:
        file_path = safe_path(path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return f"Filen er gemt: {file_path.name}"

    except Exception as e:
        return f"Fejl ved skrivning af fil: {e}"


def list_directory(path: str = ".") -> str:
    """
    Viser filer og mapper i et directory.
    """

    try:
        directory = safe_path(path)

        if not directory.is_dir():
            return f"Directory findes ikke: {path}"

        entries = []

        for entry in sorted(directory.iterdir()):
            if entry.is_dir():
                entries.append(
                    f"[DIR]  {entry.name}"
                )
            else:
                entries.append(
                    f"[FILE] {entry.name}"
                )

        if not entries:
            return "Directory'et er tomt."

        return "\n".join(entries)

    except Exception as e:
        return f"Fejl ved visning af directory: {e}"


def get_weather(city: str) -> str:
    """
    Henter den aktuelle temperatur for en by.

    Først bruges Open-Meteos geocoding API til at finde
    byens latitude og longitude.

    Derefter bruges Open-Meteos weather API til at hente
    den aktuelle temperatur.
    """

    try:
        encoded_city = quote(city)

        geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={encoded_city}"
            "&count=1"
            "&language=da"
            "&format=json"
        )

        with urlopen(
            geocoding_url,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        print()
        print("=== Open-Meteo Geocoding JSON ===")

        print(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            )
        )

        print()

        results = data.get("results")

        if not results:
            return f"Kunne ikke finde byen: {city}"

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        found_name = location.get(
            "name",
            city
        )

        country = location.get(
            "country",
            ""
        )

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            "&current=temperature_2m"
        )

        with urlopen(
            weather_url,
            timeout=10
        ) as response:

            weather_data = json.loads(
                response.read().decode("utf-8")
            )

        print()
        print("=== Open-Meteo Weather JSON ===")

        print(
            json.dumps(
                weather_data,
                indent=4,
                ensure_ascii=False
            )
        )

        print()

        current = weather_data.get(
            "current",
            {}
        )

        temperature = current.get(
            "temperature_2m"
        )

        if temperature is None:
            return "Kunne ikke hente temperaturen."

        unit = weather_data.get(
            "current_units",
            {}
        ).get(
            "temperature_2m",
            "°C"
        )

        return (
            f"Temperaturen i {found_name}, {country} "
            f"er {temperature} {unit}."
        )

    except Exception as e:
        return f"Fejl ved hentning af vejrdata: {e}"


# Her laver vi en dictionary, hvor tool-navnet
# peger på den Python-funktion, der skal udføres.
available_tools = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "get_weather": get_weather,
}


# Ollama skal have en liste over de tools,
# som LLM'en må bruge.
#
# Vi kan derfor hente funktionerne direkte
# fra dictionary'en.
tools = list(available_tools.values())


def ask_agent(user_message: str) -> str:
    """
    Sender brugerens besked til LLM'en og håndterer
    eventuelle tool calls.
    """

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    tool_call_count = 0

    while True:

        response = client.chat(
            model=MODEL,
            messages=messages,
            tools=tools,
        )

        assistant_message = response.message        

        messages.append(
            assistant_message
        )

        tool_calls = assistant_message.tool_calls
        x = assistant_message.
        
        if not tool_calls:
            return assistant_message.content

        for tool_call in tool_calls:

            if tool_call_count >= MAX_TOOL_CALLS:
                return (
                    "Agenten stoppede, fordi den nåede "
                    "grænsen for antal tool calls."
                )

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print()
            print(
                f"[Agenten bruger tool: {tool_name}]"
            )

            tool = available_tools.get(tool_name)

            if tool is None:

                result = (
                    f"Ukendt tool: {tool_name}"
                )

            else:

                try:
                    result = tool(
                        **arguments
                    )

                except Exception as e:
                    result = (
                        f"Fejl ved tool '{tool_name}': {e}"
                    )

            tool_call_count += 1

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": str(result),
                }
            )


def main():
    """
    Starter agentens brugerinterface.
    """

    print()
    print("======================================")
    print(" Lokal AI-agent")
    print("======================================")
    print()
    print("Agenten kan generere tekst og kode.")
    print("Agenten kan læse filer.")
    print("Agenten kan skrive tekst og kode til filer.")
    print(
        "Agenten kan hente temperaturen i byer "
        "fra Open-Meteo."
    )
    print("Agenten kan IKKE køre kode.")
    print()
    print("Skriv 'exit' for at afslutte.")
    print("Skriv 'clear' for at nulstille memory.")
    print()

    while True:

        try:
            user_message = input("Du: ").strip()

        except (KeyboardInterrupt, EOFError):
            print()
            print("Programmet afsluttes.")
            break

        if not user_message:
            continue

        if user_message.lower() == "exit":
            print("Programmet afsluttes.")
            break

        if user_message.lower() == "clear":

            messages[:] = [
                messages[0]
            ]

            print("Memory er nulstillet.")
            continue

        answer = ask_agent(
            user_message
        )

        print()
        print("Agent:")
        print(answer)
        print()


if __name__ == "__main__":
    main()
