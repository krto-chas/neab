# NEAB Security Assessment Suite - Flask Web Interface

## 📁 Filstruktur

```
neab_security_assessment/
├── app.py                      # Flask-applikation
├── huvudskript_v2.py          # Backend analysmotor
├── config/                     # Genererade YAML-filer
├── data/
│   └── output/                # Analysresultat
├── modules/                    # Analysmoduler
├── utils/                      # Hjälpfunktioner
├── static/
│   ├── css/
│   │   └── styles.css         # Komplett styling
│   └── js/
│       └── main.js            # Frontend JavaScript
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Startsida
    ├── form_step1.html        # Steg 1: Organisation
    ├── form_step2.html        # Steg 2: Tillgångar
    ├── form_step3.html        # Steg 3: Regelverk
    ├── form_step4.html        # Steg 4: Granska
    ├── run_analysis.html      # Kör analys
    └── results.html           # Visa resultat
```

## 🚀 Installation

### 1. Kopiera filer

```bash
# Kopiera Flask-appen
cp app_complete.py app.py

# Kopiera templates
cp templates/*.html templates/

# Kopiera static-filer
cp -r static/* static/
```

### 2. Installera beroenden

```bash
pip install flask pyyaml
```

### 3. Kör applikationen

```bash
python app.py
```

Öppna webbläsaren: http://localhost:5000

## 📝 Användning

### Steg-för-steg guide:

1. **Startsida** - Välj "Starta ny analys"
2. **Steg 1: Organisation** - Fyll i organisationsinformation
3. **Steg 2: Tillgångar** - Lägg till kritiska system och kronjuveler
4. **Steg 3: Regelverk** - Välj tillämpliga regelverk (NIS2, GDPR, DORA, CER)
5. **Steg 4: Granska** - Kontrollera indata och generera analys
6. **Kör analys** - Vänta medan systemet analyserar (1-2 min)
7. **Resultat** - Ladda ner PDF och Excel

## 🎨 Features

✅ **Modern UI** - Responsiv design med NEAB-färgschema
✅ **Session-hantering** - Data sparas mellan steg
✅ **Progress bar** - Visuell indikator för framsteg
✅ **Form validation** - Client-side validering
✅ **Auto-hide alerts** - Meddelanden försvinner automatiskt
✅ **File download** - Direkt nedladdning av rapporter
✅ **Results history** - Visa de 10 senaste analyserna

## 🔧 Konfiguration

### Secret Key (VIKTIGT för production!)

I `app.py`, ändra:
```python
app.secret_key = 'din-hemliga-nyckel-här'
```

Generera en säker nyckel:
```python
import secrets
print(secrets.token_hex(32))
```

### Portkonfiguration

Standard: `http://localhost:5000`

Ändra i `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 📊 Output

När analysen är klar genereras:
- ✅ PDF-rapport (4 sidor)
- ✅ Excel-analys (5 flikar)
- ✅ Heat map PNG
- ✅ JSON-data
- ✅ Workshop-protokoll

Alla filer sparas i: `data/output/YYYYMMDD_HHMMSS/`

## 🐛 Felsökning

### Port redan i bruk
```bash
# Hitta process
lsof -i :5000

# Döda process
kill -9 <PID>
```

### Template inte hittad
Kontrollera att alla HTML-filer finns i `templates/`

### CSS inte laddas
Kontrollera att `static/css/styles.css` finns

## 🎓 För gruppexaminationen

Använd webgränssnittet för att:
1. Demonstrera verktyget live
2. Generera olika scenarion
3. Visa hur data matas in
4. Presentera resultat direkt

## 📞 Support

Vid problem, kontrollera:
- Flask är installerat: `pip show flask`
- Alla filer är på plats
- Console-loggen för felmeddelanden