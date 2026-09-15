"""
Input Loader - Läser konfiguration från YAML eller JSON
Hanterar både manuellt skapade filer och webb-genererade inputs
"""
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class NEABInputLoader:
    """
    Läser och validerar input-konfiguration för NEAB Security Assessment
    """

    def __init__(self, input_file: Optional[str] = None):
        """
        Args:
            input_file: Sökväg till input-fil (YAML eller JSON)
                       Om None, använd default template
        """
        if input_file:
            self.input_file = Path(input_file)
        else:
            # Default till template
            self.input_file = Path(__file__).parent / 'neab_input.yaml'

        self.data = self._load()
        self._validate()

    def _load(self) -> Dict[str, Any]:
        """Läs in från fil"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input-fil saknas: {self.input_file}")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            if self.input_file.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif self.input_file.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Okänt filformat: {self.input_file.suffix}")

    def _validate(self):
        """Validera att nödvändiga fält finns"""
        required_sections = ['organisation', 'kritiska_anlaggningar', 'regulatoriska_krav']

        for section in required_sections:
            if section not in self.data:
                raise ValueError(f"Saknad sektion i input: {section}")

    def get_organisation_data(self) -> Dict[str, Any]:
        """Hämta organisationsdata"""
        return self.data.get('organisation', {})

    def get_critical_assets(self) -> list:
        """Hämta kritiska anläggningar"""
        return self.data.get('kritiska_anlaggningar', [])

    def get_services(self) -> list:
        """Hämta tjänster"""
        return self.data.get('tjanster', [])

    def get_regulatory_requirements(self) -> Dict[str, Any]:
        """Hämta regulatoriska krav"""
        return self.data.get('regulatoriska_krav', {})

    def get_crown_jewels(self) -> list:
        """Hämta kronjuveler (kritiska system)"""
        return self.data.get('kronjuveler', [])

    def get_threat_landscape(self) -> list:
        """Hämta hotbild"""
        return self.data.get('hotbild', [])

    def get_known_vulnerabilities(self) -> list:
        """Hämta kända sårbarheter"""
        return self.data.get('kanda_brister', [])

    def get_api_scenarios(self) -> Dict[str, Any]:
        """Hämta API-scenarios"""
        return self.data.get('api_scenarios', {})

    def get_all_data(self) -> Dict[str, Any]:
        """Hämta all data"""
        return self.data

    def save_to_file(self, output_file: str, format: str = 'yaml'):
        """
        Spara konfiguration till fil

        Args:
            output_file: Sökväg till output
            format: 'yaml' eller 'json'
        """
        output_path = Path(output_file)

        with open(output_path, 'w', encoding='utf-8') as f:
            if format == 'yaml':
                yaml.dump(self.data, f, allow_unicode=True, sort_keys=False)
            elif format == 'json':
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"Okänt format: {format}")

    @staticmethod
    def create_from_dict(data: Dict[str, Any], output_file: str) -> 'NEABInputLoader':
        """
        Skapa input-fil från dictionary (används från webformulär)

        Args:
            data: Input-data som dictionary
            output_file: Var filen ska sparas

        Returns:
            NEABInputLoader med inläst data
        """
        output_path = Path(output_file)

        # Lägg till metadata
        data['metadata'] = {
            'created': datetime.now().isoformat(),
            'version': '2.0',
            'source': 'web_form'
        }

        # Spara till fil
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        # Returnera loader med den nya filen
        return NEABInputLoader(str(output_path))

    def get_summary(self) -> str:
        """Returnera läsbar sammanfattning av input"""
        org = self.get_organisation_data()

        summary = f"""
═══════════════════════════════════════════════════════
INPUT SAMMANFATTNING
═══════════════════════════════════════════════════════

Organisation: {org.get('namn', 'N/A')}
Typ: {org.get('typ', 'N/A')}

Kunder:
  - Elnät: {org.get('kunder', {}).get('elnat', 0):,}
  - Fjärrvärme: {org.get('kunder', {}).get('fjarrvärme', 0):,}

Personal: {org.get('personal', {}).get('totalt', 0)}

Kritiska anläggningar: {len(self.get_critical_assets())}
Kronjuveler: {len(self.get_crown_jewels())}
Tjänster: {len(self.get_services())}

Regulatoriska krav:
  - NIS2: {'Ja' if self.get_regulatory_requirements().get('nis2', {}).get('tillamplig') else 'Nej'}
  - GDPR: {'Ja' if self.get_regulatory_requirements().get('gdpr', {}).get('tillamplig') else 'Nej'}
  - DORA: {'Ja' if self.get_regulatory_requirements().get('dora', {}).get('tillamplig') else 'Nej'}
  - CER: {'Ja' if self.get_regulatory_requirements().get('cer', {}).get('tillamplig') else 'Nej'}

═══════════════════════════════════════════════════════
"""
        return summary


class InputValidator:
    """Validerar input-data"""

    @staticmethod
    def validate_organisation(data: Dict[str, Any]) -> tuple[bool, list]:
        """Validera organisationsdata"""
        errors = []

        if 'namn' not in data:
            errors.append("Organisations namn saknas")

        if 'kunder' in data:
            if 'elnat' not in data['kunder'] or not isinstance(data['kunder']['elnat'], int):
                errors.append("Antal elnätkunder måste vara ett heltal")

        return len(errors) == 0, errors

    @staticmethod
    def validate_regulatory(data: Dict[str, Any]) -> tuple[bool, list]:
        """Validera regulatoriska krav"""
        errors = []

        required_frameworks = ['nis2', 'gdpr', 'dora', 'cer']
        for framework in required_frameworks:
            if framework not in data:
                errors.append(f"Regelverk {framework.upper()} saknas")
            elif 'tillamplig' not in data[framework]:
                errors.append(f"Tillämplighet för {framework.upper()} saknas")

        return len(errors) == 0, errors

    @staticmethod
    def validate_all(input_data: Dict[str, Any]) -> tuple[bool, list]:
        """Validera all input"""
        all_errors = []

        # Validera organisation
        if 'organisation' in input_data:
            valid, errors = InputValidator.validate_organisation(input_data['organisation'])
            if not valid:
                all_errors.extend(errors)
        else:
            all_errors.append("Organisationsdata saknas")

        # Validera regulatoriska krav
        if 'regulatoriska_krav' in input_data:
            valid, errors = InputValidator.validate_regulatory(input_data['regulatoriska_krav'])
            if not valid:
                all_errors.extend(errors)
        else:
            all_errors.append("Regulatoriska krav saknas")

        return len(all_errors) == 0, all_errors