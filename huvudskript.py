#!/usr/bin/env python3
"""
NEAB Security Assessment Suite v2.0
Huvudskript för CLI-körning
"""
import sys
import io
from pathlib import Path
from datetime import datetime
import logging

# Fix för Windows konsol encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Lägg till projektets root till Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.input_loader import NEABInputLoader, InputValidator
from modules.regulatorisk_modul import RegulatoriskAnalys
from modules.risk_workshop_modul import RiskWorkshop
from modules.api_sakerhet_modul import APISakerhetAnalys
from modules.rapport_generator import RapportGenerator
from utils.console_formatter import ConsoleFormatter, ProgressBar
from utils.pdf_template import create_neab_report

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neab_assessment.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NEABSecurityAssessment:
    """Huvudklass för NEAB Security Assessment"""

    def __init__(self, input_file=None):
        """
        Args:
            input_file: Sökväg till input YAML/JSON. Om None används default template.
        """
        # Skapa output-mapp med timestamp
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = project_root / 'data' / 'output' / self.timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Ladda input
        try:
            self.input_loader = NEABInputLoader(input_file)
            ConsoleFormatter.success(f"Input laddad från: {self.input_loader.input_file}")
        except Exception as e:
            ConsoleFormatter.error(f"Kunde inte ladda input: {e}")
            sys.exit(1)

        # Validera input
        valid, errors = InputValidator.validate_all(self.input_loader.get_all_data())
        if not valid:
            ConsoleFormatter.error("Input-validering misslyckades:")
            for error in errors:
                ConsoleFormatter.bullet(error)
            sys.exit(1)

        # Initiera moduler
        input_data = self.input_loader.get_all_data()
        self.regulatorisk_modul = RegulatoriskAnalys(input_data)
        self.risk_workshop = RiskWorkshop(input_data)
        self.api_sakerhet = APISakerhetAnalys(input_data)
        self.rapport_generator = RapportGenerator(self.output_dir)

        ConsoleFormatter.info(f"Output-mapp: {self.output_dir}")

    def visa_input_sammanfattning(self):
        """Visa sammanfattning av inläst input"""
        ConsoleFormatter.section("INPUT SAMMANFATTNING")
        print(self.input_loader.get_summary())

    def kor_komplett_analys(self):
        """Genomför komplett säkerhetsanalys"""

        # Visa banner
        ConsoleFormatter.banner()

        # Visa input-sammanfattning
        self.visa_input_sammanfattning()

        # Huvudanalys
        ConsoleFormatter.header("STARTAR KOMPLETT SÄKERHETSANALYS")

        resultat = {}

        # Steg 1: Regulatorisk kartläggning
        ConsoleFormatter.step(1, 4, "Genomför regulatorisk kartläggning...")
        regulatorisk_data = self.regulatorisk_modul.genomfor_kartlaggning(
            self.input_loader.get_regulatory_requirements()
        )
        resultat['regulatorisk'] = regulatorisk_data

        ConsoleFormatter.success(
            f"Identifierade {len(regulatorisk_data.get('krav', []))} regulatoriska krav"
        )
        ConsoleFormatter.bullet(
            f"Efterlevnad: {regulatorisk_data.get('efterlevnad_procent', 0):.1f}%",
            indent=4
        )

        # Steg 2: Riskanalys
        ConsoleFormatter.step(2, 4, "Genomför riskanalys (MSB-metod + STRIDE)...")

        risk_input = {
            'kronjuveler': self.input_loader.get_crown_jewels(),
            'hotbild': self.input_loader.get_threat_landscape(),
            'sårbarheter': self.input_loader.get_known_vulnerabilities()
        }

        risk_data = self.risk_workshop.genomfor_workshop(risk_input)
        resultat['risk'] = risk_data

        ConsoleFormatter.success(
            f"Identifierade {len(risk_data.get('risker', []))} risker"
        )

        # Visa riskfördelning
        risk_distribution = risk_data.get('riskfordelning', {})
        for level, count in risk_distribution.items():
            if count > 0:
                ConsoleFormatter.bullet(
                    f"{level}: {count} st",
                    indent=4
                )

        # Steg 3: Mitigeringsstrategier
        ConsoleFormatter.step(3, 4, "Utvecklar mitigeringsstrategier...")
        mitigering_data = self.risk_workshop.generera_atgardsplan(risk_data)
        resultat['mitigering'] = mitigering_data

        ConsoleFormatter.success(
            f"Genererade {len(mitigering_data.get('åtgärder', []))} åtgärder"
        )

        # Steg 4: API-säkerhet
        ConsoleFormatter.step(4, 4, "Analyserar API-säkerhet (B2B/B2C)...")
        api_data = self.api_sakerhet.analysera_scenarios(
            self.input_loader.get_api_scenarios()
        )
        resultat['api'] = api_data

        ConsoleFormatter.success(
            f"Analyserade {len(api_data.get('scenarios', []))} API-scenarios"
        )

        # Generera rapporter
        ConsoleFormatter.section("GENERERAR RAPPORTER")

        progress = ProgressBar(4, "Skapar filer")

        # Excel
        excel_path = self.rapport_generator.generera_excel(resultat)
        progress.update()
        ConsoleFormatter.progress_complete("Excel-fil skapad", excel_path)

        # PDF (förbättrad)
        pdf_data = self._prepare_pdf_data(resultat)
        pdf_path = self.output_dir / f"NEAB_Ledningsrapport_{self.timestamp}.pdf"
        create_neab_report(pdf_path, pdf_data)
        progress.update()
        ConsoleFormatter.progress_complete("PDF-rapport skapad", pdf_path)

        # JSON
        json_path = self.rapport_generator.generera_json(resultat)
        progress.update()
        ConsoleFormatter.progress_complete("JSON-data skapad", json_path)

        # Protokoll
        protokoll_path = self.rapport_generator.generera_protokoll(resultat)
        progress.update()
        ConsoleFormatter.progress_complete("Workshop-protokoll skapat", protokoll_path)

        progress.complete()

        # Slutsammanfattning
        self._visa_slutsammanfattning(resultat)

        return resultat

    def _prepare_pdf_data(self, resultat):
        """Förbered data för PDF-generering"""
        org_data = self.input_loader.get_organisation_data()
        reg_data = resultat.get('regulatorisk', {})
        risk_data = resultat.get('risk', {})

        # Samla top risker
        top_risks = []
        for risk in risk_data.get('risker', [])[:5]:
            risk_str = f"{risk.get('hot', 'N/A')} ({risk.get('tillgang', 'N/A')})"
            top_risks.append(risk_str)

        # Samla regulatoriska brister
        regulatory_gaps = []
        for krav in reg_data.get('krav', []):
            if krav.get('status') in ['Delvis uppfyllt', 'Ej uppfyllt']:
                gap_str = f"{krav.get('krav_beskrivning', 'N/A')} ({krav.get('regelverk', 'N/A')})"
                regulatory_gaps.append(gap_str)

        # Samla prioriterade åtgärder
        priority_actions = []
        for action in resultat.get('mitigering', {}).get('åtgärder', [])[:5]:
            action_str = action.get('föreslagen_åtgärd', 'N/A')
            priority_actions.append(action_str)

        # Riskfördelning
        risk_distribution = risk_data.get('riskfordelning', {})

        return {
            'organisation': org_data.get('namn', 'Nordlunda Energi AB'),
            'compliance_rate': reg_data.get('efterlevnad_procent', 0),
            'very_high_risks': risk_distribution.get('Mycket hög', 0),
            'high_risks': risk_distribution.get('Hög', 0),
            'critical_actions': len(priority_actions),
            'top_risks': top_risks,
            'regulatory_gaps': regulatory_gaps,
            'priority_actions': priority_actions,
            'total_requirements': len(reg_data.get('krav', [])),
            'fulfilled': sum(1 for k in reg_data.get('krav', []) if k.get('status') == 'Uppfyllt'),
            'partial': sum(1 for k in reg_data.get('krav', []) if k.get('status') == 'Delvis uppfyllt'),
            'not_fulfilled': sum(1 for k in reg_data.get('krav', []) if k.get('status') == 'Ej uppfyllt'),
            'risk_distribution': risk_distribution,
            'priority_areas': [
                'Styrelseutbildning (NIS2)',
                'DPIA för mätdata (GDPR)',
                'Formalisering av riskhanteringsprocesser'
            ],
            'core_business': (
                f"{org_data.get('namn', 'NEAB')} är ett {org_data.get('typ', 'energibolag')} "
                f"som betjänar ca {org_data.get('kunder', {}).get('elnat', 0):,} elnätskunder "
                f"och {org_data.get('kunder', {}).get('fjarrvärme', 0):,} fjärrvärmekunder."
            ),
            'critical_systems': (
                "SCADA/DCS för styrning, AMI för mätdata, OMS för avbrottshantering, "
                "samt kund- och faktureringssystem."
            ),
            'security_governance': (
                "CISO med stab, OT-säkerhetsansvarig, samt SOC via MSSP med 24/7-övervakning."
            ),
            'follow_up_plan': (
                "Säkerhetsarbetet följs upp kvartalsvis med rapportering till styrelsen. "
                "Riskanalys uppdateras årligen eller vid väsentliga förändringar. "
                "Åtgärder spåras i riskregister med ansvariga och deadlines."
            )
        }

    def _visa_slutsammanfattning(self, resultat):
        """Visa slutsammanfattning i konsolen"""
        ConsoleFormatter.header("ANALYS SLUTFÖRD")

        reg_data = resultat.get('regulatorisk', {})
        risk_data = resultat.get('risk', {})

        summary_data = {
            'Regelefterlevnad': f"{reg_data.get('efterlevnad_procent', 0):.1f}%",
            'Totalt risker': str(len(risk_data.get('risker', []))),
            'Mycket höga risker': str(risk_data.get('riskfordelning', {}).get('Mycket hög', 0)),
            'Åtgärder identifierade': str(len(resultat.get('mitigering', {}).get('åtgärder', []))),
            'Output-mapp': str(self.output_dir)
        }

        ConsoleFormatter.summary_box("RESULTAT", summary_data)

        # Lista genererade filer
        ConsoleFormatter.info("Genererade filer:")
        for file in sorted(self.output_dir.glob('*')):
            ConsoleFormatter.bullet(file.name, indent=2)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='NEAB Security Assessment Suite v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exempel:
  # Använd default template
  python huvudskript.py

  # Använd egen input-fil
  python huvudskript.py -i min_input.yaml

  # Visa endast input-sammanfattning
  python huvudskript.py -i min_input.yaml --show-input
        """
    )

    parser.add_argument(
        '-i', '--input',
        help='Sökväg till input YAML/JSON fil',
        default=None
    )

    parser.add_argument(
        '--show-input',
        action='store_true',
        help='Visa endast input-sammanfattning och avsluta'
    )

    args = parser.parse_args()

    try:
        # Skapa assessment
        assessment = NEABSecurityAssessment(args.input)

        if args.show_input:
            # Visa bara input och avsluta
            assessment.visa_input_sammanfattning()
            return

        # Kör full analys
        resultat = assessment.kor_komplett_analys()

        ConsoleFormatter.success("Alla operationer slutförda!")

    except KeyboardInterrupt:
        ConsoleFormatter.warning("\nAvbruten av användare")
        sys.exit(130)
    except Exception as e:
        ConsoleFormatter.error(f"Fel uppstod: {e}")
        logger.exception("Oväntad exception")
        sys.exit(1)


if __name__ == "__main__":
    main()