# 🚀 NEAB Security Assessment - Snabbstart

## Installation (5 minuter)

### 1. Förberedelser
```bash
cd ~/Documents/Chas/neab_security_assessment
```

### 2. Uppdatera requirements.txt
Ersätt din befintliga `requirements.txt` med den nya från `/mnt/user-data/outputs/requirements.txt`

### 3. Installera beroenden

**Om du har Python 3.13 (som du har):**
```bash
pip install --upgrade pip
pip install colorama PyYAML Flask Werkzeug openpyxl reportlab matplotlib python-dateutil
pip install "numpy>=2.2.0"
pip install "pandas>=2.2.0"
```

**Om det fortfarande krånglar:**
```bash
# Använd Anaconda istället (om du har det)
conda install numpy pandas flask openpyxl reportlab matplotlib pyyaml colorama -c conda-forge
```

### 4. Kopiera nya filer

Kopiera följande filer från `/mnt/user-data/outputs/` till ditt projekt:

**Kärnfiler:**
- `hauptskript.py` → `~/Documents/Chas/neab_security_assessment/huvudskript.py` (ersätt befintlig)
- `app.py` → `~/Documents/Chas/neab_security_assessment/app.py` (ny fil)
- `requirements.txt` → uppdatera din befintliga

**Utils (nya):**
- `utils/console_formatter.py`
- `utils/pdf_template.py`

**Config:**
- `config/input_loader.py`
- `config/neab_input.yaml`

**Templates (för webb):**
- `templates/base.html`
- `templates/index.html`

Du behöver också skapa resterande form-templates (step1, step2, step3, review, results, error).

### 5. Testa installationen

```bash
python huvudskript.py --show-input
```

Om du ser detta ✅:
```
═══════════════════════════════════════════════════════
INPUT SAMMANFATTNING
═══════════════════════════════════════════════════════

Organisation: Nordlunda Energi AB
...
```

Då fungerar allt!

## 🎯 Första körningen

### Alternativ A: Kommandorad (snabbast)

```bash
python huvudskript.py
```

Du får:
- ✅ Snygg färglagd output i konsolen
- ✅ Förbättrad PDF-rapport
- ✅ Excel med alla flikar
- ✅ JSON-data
- ✅ Workshop-protokoll

Alla filer hamnar i:
```
data/output/<timestamp>/
```

### Alternativ B: Webformulär (mer användarvänligt)

```bash
python app.py
```

Öppna sedan:
```
http://127.0.0.1:5000
```

Fyll i formuläret steg för steg → Granska → Kör analys → Ladda ner rapporter!

## 📊 Vad har förbättrats?

### ✨ Version 2.0 Nytt:

1. **Konsolutskrift**
   - Färgkodad (grön för success, röd för fel)
   - Progressbars
   - Tydliga sektioner
   - Windows-kompatibelt (inga krascher på svenska tecken)

2. **PDF-rapport**
   - Professionell design med färgschema
   - Tydlig struktur för ledningen
   - Header/footer på varje sida
   - Sammanfattningsbox på framsidan

3. **Input från fil**
   - YAML-template med all NEAB-data
   - Validering av input
   - Lätt att anpassa för andra organisationer

4. **Webformulär**
   - Stegvis inmatning
   - Realtidsvalidering
   - Spara och återuppta
   - Direkt nedladdning av rapporter

5. **Modulär kod**
   - Lättare att underhålla
   - Återanvändbar för framtida projekt
   - Tydlig separation av concerns

## 🔍 Vad produceras?

### 1. PDF-rapport (för ledningen)
```
NEAB_Ledningsrapport_20241202_152852.pdf
```
- Sammanfattning för ledningsnivå
- Organisationsbeskrivning
- Regulatorisk kartläggning
- Risksammanfattning
- Rekommenderade åtgärder
- Uppföljningsplan

### 2. Excel-arbetsfil
```
NEAB_Sakerhetsanalys_20241202_152852.xlsx
```
Flikar:
- Regulatorisk kartläggning (9 krav)
- Riskmatris (32 risker)
- Riskbehandlingsplan (15 åtgärder)
- API-risker (B2B/B2C-scenarios)

### 3. JSON-data
```
NEAB_Resultat_20241202_152852.json
```
Strukturerad data för vidare bearbetning

### 4. Workshop-protokoll
```
Workshop_Protokoll_20241202_152852.txt
```
Dokumentation av genomförd riskworkshop

## 📝 Anpassa för din uppgift

### För gruppexamination behöver ni:

1. **Fyll i gruppmedlemmar** i slutrapporten
2. **Lägg till era reflektioner** (varje person)
3. **Dokumentera workshopen** (vem gjorde vad)
4. **Justera NEAB-data** om ni vill ändra scenariot

### Redigera input:

```bash
# Öppna config/neab_input.yaml
# Ändra:
organisation:
  namn: "Er organisation"
  kunder:
    elnat: 100000  # etc
```

Kör sedan:
```bash
python huvudskript.py -i config/neab_input.yaml
```

## ⚡ Tips & Tricks

### Snabbtesta med olika scenarios

```bash
# Scenario 1: Default NEAB
python huvudskript.py

# Scenario 2: Högrisk (lägg till fler hot i YAML)
python huvudskript.py -i high_risk_scenario.yaml

# Scenario 3: Minimal (färre system)
python huvudskript.py -i minimal_scenario.yaml
```

### Automatisera för flera organisationer

```bash
for org in org1 org2 org3; do
    python huvudskript.py -i configs/${org}_input.yaml
done
```

### Integrera i din workflow

```python
# my_script.py
from huvudskript import NEABSecurityAssessment

assessment = NEABSecurityAssessment('my_input.yaml')
resultat = assessment.kor_komplett_analys()

# Gör något med resultat...
if resultat['risk']['riskfordelning']['Mycket hög'] > 5:
    send_alert_to_ciso()
```

## 🐛 Vanliga problem

### "ModuleNotFoundError: No module named 'colorama'"
**Fix:**
```bash
pip install colorama
```

### "UnicodeEncodeError" i konsolen
**Fix:** Redan fixat i v2.0! Om det ändå händer:
```bash
$env:PYTHONIOENCODING="utf-8"  # PowerShell
set PYTHONIOENCODING=utf-8     # CMD
export PYTHONIOENCODING=utf-8  # Bash
```

### NumPy-kompileringsfel (Python 3.13)
**Fix:**
```bash
pip install "numpy>=2.2.0" --only-binary :all:
```

### Port 5000 upptagen (Flask)
**Fix:**
```bash
python app.py  # Ändra i app.py: app.run(port=8080)
```

## 📞 Support

1. Kolla README.md
2. Kolla loggfilen: `neab_assessment.log`
3. Kolla felsökningssektionen i README
4. Fråga din grupp
5. Kontakta kursansvarig

## ✅ Checklista inför redovisning

- [ ] Alla dependencies installerade
- [ ] Testkörning lyckad
- [ ] PDF-rapport genererad och granskas
- [ ] Excel-fil öppnas korrekt
- [ ] Gruppmedlemmar ifyllda
- [ ] Reflektioner skrivna
- [ ] Workshop-protokoll komplett
- [ ] Presentation förberedd
- [ ] Källkod backup (GitHub)

## 🎓 För skoluppgiften

Denna version ger er:

✅ **Regulatorisk kartläggning** (Moment 1)
✅ **Riskworkshop med STRIDE** (Moment 2)
✅ **Mitigeringsstrategier med CIS Controls** (Moment 3)
✅ **API-säkerhetsanalys B2B/B2C** (Moment 4)
✅ **Ledningsrapport** enligt krav (Moment 5)
✅ **Excel-bilagor** med alla flikar
✅ **Workshop-protokoll**

Alltså: **ALLT ni behöver för uppgiften!**

---

**Happy hacking! 🚀**

Vid frågor, kolla README.md eller loggfilen först.

Version: 2.0 | Uppdaterad: 2024-12-02