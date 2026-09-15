# NEAB Security Assessment Suite v2.0

Professionellt verktyg för säkerhetsanalys av kritisk infrastruktur enligt NIS2, GDPR, DORA och CER.

## 🎯 Funktioner

- **Regulatorisk kartläggning**: Automatisk mappning av NIS2, GDPR, DORA och CER-krav
- **Riskanalys**: MSB-metodstöd + STRIDE hotmodellering
- **Mitigeringsstrategier**: Åtgärdsrekommendationer enligt CIS Controls v8
- **API-säkerhetsanalys**: Jämförelse av B2B vs B2C-scenarios
- **Professionella rapporter**: PDF för ledningen + Excel-arbetsfiler
- **Webformulär**: Stegvist guidat interface för datainmatning
- **CLI-support**: Kommandoradsversion för automation

## 📋 Krav

- **Python**: 3.11 eller 3.12 rekommenderas (3.13 fungerar med vissa anpassningar)
- **OS**: Windows, macOS eller Linux
- **Minne**: 2 GB RAM
- **Disk**: 500 MB ledigt utrymme

## 🚀 Installation

### Steg 1: Klona/ladda ner projektet

```bash
cd ~/Documents/Chas
git clone <repository-url> neab_security_assessment
cd neab_security_assessment
```

### Steg 2: Skapa virtuell miljö (rekommenderat)

**Windows (Git Bash/MINGW64):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Steg 3: Installera beroenden

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Om du får NumPy-fel på Windows med Python 3.13:**
```bash
pip install --upgrade pip setuptools wheel
pip install --user "numpy>=2.2.0"
pip install -r requirements.txt
```

### Steg 4: Testa installationen

```bash
python huvudskript.py --show-input
```

Om du ser input-sammanfattningen är allt korrekt installerat! ✓

## 📖 Användning

### Alternativ 1: Webformulär (rekommenderat för första gången)

1. Starta webbservern:
```bash
python app.py
```

2. Öppna webbläsaren:
```
http://127.0.0.1:5000
```

3. Fyll i formuläret steg för steg

4. Granska och kör analys

5. Ladda ner genererade rapporter

### Alternativ 2: Kommandorad (CLI)

**Med default template:**
```bash
python huvudskript.py
```

**Med egen input-fil:**
```bash
python huvudskript.py -i min_input.yaml
```

**Visa endast input-sammanfattning:**
```bash
python huvudskript.py -i config/neab_input.yaml --show-input
```

### Alternativ 3: Python API

```python
from huvudskript import NEABSecurityAssessment

# Skapa assessment med egen input
assessment = NEABSecurityAssessment('min_input.yaml')

# Visa sammanfattning
assessment.visa_input_sammanfattning()

# Kör analys
resultat = assessment.kor_komplett_analys()

# Output finns i data/output/<timestamp>/
```

## 📁 Projektstruktur

```
neab_security_assessment/
├── app.py                    # Flask web-app
├── huvudskript.py            # CLI-version
├── requirements.txt          # Python-beroenden
├── config/
│   ├── input_loader.py      # YAML/JSON loader
│   ├── neab_input.yaml      # Input-template
│   └── settings.py          # App-inställningar
├── modules/
│   ├── regulatorisk_modul.py
│   ├── risk_workshop_modul.py
│   ├── api_sakerhet_modul.py
│   └── rapport_generator.py
├── templates/               # HTML-templates för webb
│   ├── base.html
│   ├── index.html
│   ├── form_step1.html
│   ├── form_step2.html
│   ├── form_step3.html
│   └── results.html
├── utils/
│   ├── console_formatter.py # Snygg konsolutskrift
│   └── pdf_template.py      # PDF-generering
└── data/
    ├── input/               # Sparade inputs
    └── output/              # Genererade rapporter
```

## 🔧 Konfiguration

### Anpassa input-template

Redigera `config/neab_input.yaml` för att:
- Ändra organisationsdata
- Lägga till/ta bort kritiska system
- Definiera hotbild
- Konfigurera API-scenarios
- Sätta regulatoriska krav

### Exempel på egen input-fil

```yaml
# min_organisation.yaml
organisation:
  namn: "Mitt Energibolag AB"
  kunder:
    elnat: 50000
    fjarrvärme: 8000
  personal:
    totalt: 200

regulatoriska_krav:
  nis2:
    tillamplig: true
    klassificering: "Väsentlig enhet"
  gdpr:
    tillamplig: true

# ... fortsättning
```

Kör sedan:
```bash
python huvudskript.py -i min_organisation.yaml
```

## 📊 Output-filer

Varje analys genererar:

1. **`NEAB_Ledningsrapport_<timestamp>.pdf`**
   - Sammanfattning för ledningen
   - Riskbedömning
   - Rekommenderade åtgärder

2. **`NEAB_Sakerhetsanalys_<timestamp>.xlsx`**
   - Flik: Regulatorisk kartläggning
   - Flik: Riskmatris
   - Flik: Riskbehandlingsplan
   - Flik: API-risker

3. **`NEAB_Resultat_<timestamp>.json`**
   - Maskinläsbar data
   - För vidare bearbetning

4. **`Workshop_Protokoll_<timestamp>.txt`**
   - Dokumentation av riskworkshop
   - Deltagare, metod, resultat

## 🎨 Funktioner v2.0

### Nya i denna version:

✨ **Förbättrad konsolutskrift**
- Färgkodad output (Windows-kompatibel)
- Progressbars och status-indikatorer
- Professionell banner och sammanfattningar

✨ **Förbättrad PDF-rapport**
- Modern design med färgschema
- Tydlig struktur för ledningen
- Professionella tabeller och diagram

✨ **Input från fil**
- YAML/JSON-support
- Validering av input
- Template för snabbstart

✨ **Webformulär**
- Stegvist guidat interface
- Realtidsvalidering
- Spara och återuppta

✨ **Modulär arkitektur**
- Tydlig separation av concerns
- Återanvändbar kod
- Lätt att utöka

## 🐛 Felsökning

### Problem: "UnicodeEncodeError" i konsolen

**Lösning:** Koden hanterar detta automatiskt i v2.0, men om problemet kvarstår:

```bash
# Windows
set PYTHONIOENCODING=utf-8
python huvudskript.py

# PowerShell
$env:PYTHONIOENCODING="utf-8"
python huvudskript.py
```

### Problem: NumPy kompileras från källkod (Windows + Python 3.13)

**Lösning:**
```bash
pip install --user "numpy>=2.2.0" --only-binary :all:
pip install -r requirements.txt
```

Eller använd Python 3.11/3.12 istället.

### Problem: "Module not found"

**Lösning:**
```bash
# Kontrollera att du är i rätt mapp
cd ~/Documents/Chas/neab_security_assessment

# Kontrollera att venv är aktiverad
which python  # Ska peka på venv/Scripts/python

# Reinstallera beroenden
pip install -r requirements.txt
```

### Problem: Flask-appen startar inte

**Lösning:**
```bash
# Kontrollera att port 5000 är ledig
netstat -an | grep 5000

# Eller använd annan port
python app.py --port 8080
```

## 📝 Exempel på användningsfall

### Use Case 1: Årlig riskanalys för styrelsen

```bash
# Kör med default NEAB-template
python huvudskript.py

# Resultat: Komplett rapportpaket i data/output/<timestamp>/
# Skicka PDF:en till styrelsen
# Använd Excel-filen för uppföljning
```

### Use Case 2: Snabbanalys av ny hotbild

```python
from huvudskript import NEABSecurityAssessment

# Ladda befintlig konfiguration
assessment = NEABSecurityAssessment('config/neab_input.yaml')

# Kör bara riskanalys-delen
risk_data = assessment.risk_workshop.genomfor_workshop({
    'hotbild': ['Nytt hot: Supply chain attack via SCADA-leverantör'],
    'kronjuveler': assessment.input_loader.get_crown_jewels()
})

print(risk_data)
```

### Use Case 3: Integration i CI/CD

```bash
# Automatisk säkerhetsanalys vid större ändringar
python huvudskript.py -i production_config.yaml

# Kontrollera exit code
if [ $? -eq 0 ]; then
    echo "Analys OK"
    # Skicka rapport via mail
else
    echo "Analys misslyckades"
    exit 1
fi
```

## 🤝 Bidrag och utveckling

För att utveckla och utöka verktyget:

1. Skapa feature branch
2. Lägg till nya moduler i `modules/`
3. Uppdatera `requirements.txt` om nya beroenden
4. Testa med `pytest` (om aktiverat)
5. Skapa pull request

## 📄 Licens

Detta verktyg är utvecklat för utbildningssyfte inom ramen för Chas Academy.

## 👤 Författare

- **Stoffe** - Cybersecurity student, Chas Academy
- **Version**: 2.0
- **Datum**: 2024-12-02

## 🆘 Support

För frågor eller problem:
1. Kontrollera detta README först
2. Se felsökningssektionen
3. Kontrollera loggfilen `neab_assessment.log`
4. Kontakta kursansvarig

## 📚 Referenser

- [NIS2-direktivet](https://eur-lex.europa.eu/eli/dir/2022/2555)
- [MSB Metodstöd](https://www.msb.se/metodstod)
- [CIS Controls v8](https://www.cisecurity.org/controls/v8)
- [STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)

---

**Version**: 2.0  
**Senast uppdaterad**: 2024-12-02  
**Python**: 3.11+ (3.13 med anpassningar)  
**Status**: ✅ Production ready för skoluppgift