"""
Risk Heat Map Generator
Skapar visuell 5x5 risk-matris för NEAB Security Assessment
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RiskHeatMap:
    """Genererar professionell risk heat map"""

    # NEAB Färgschema (matchar PDF:en)
    COLORS = {
        'critical': '#ef4444',      # Röd (Mycket hög)
        'high': '#f59e0b',          # Orange (Hög)
        'medium': '#fbbf24',        # Gul (Medel)
        'low': '#10b981',           # Grön (Låg)
        'very_low': '#6ee7b7',      # Ljusgrön (Mycket låg)
        'grid': '#e5e7eb',          # Ljusgrå
        'text': '#1f2937',          # Mörkgrå
        'neab_blue': '#1e3a8a'      # NEAB blå
    }

    def __init__(self, figsize=(10, 8)):
        self.figsize = figsize
        self.risk_matrix = self._create_risk_matrix()

    def _create_risk_matrix(self):
        """
        Skapa 5x5 risk-matris enligt MSB:s metodik
        Riskvärde = Sannolikhet × Konsekvens

        Risknivåer:
        - 1-3: Låg (grön)
        - 4-6: Medel (gul)
        - 8-12: Hög (orange)
        - 15-25: Mycket hög (röd)
        """
        # Matris: rad = sannolikhet (1-5), kolumn = konsekvens (1-5)
        # Riskvärde = rad × kolumn
        matrix = np.zeros((5, 5), dtype=int)
        for i in range(5):
            for j in range(5):
                matrix[i, j] = (i + 1) * (j + 1)
        return matrix

    def _get_risk_color(self, risk_value):
        """Returnera färg baserat på riskvärde"""
        if risk_value >= 15:
            return self.COLORS['critical']
        elif risk_value >= 8:
            return self.COLORS['high']
        elif risk_value >= 4:
            return self.COLORS['medium']
        else:
            return self.COLORS['low']

    def _get_risk_level(self, risk_value):
        """Returnera risknivå som text"""
        if risk_value >= 15:
            return 'Mycket hög'
        elif risk_value >= 8:
            return 'Hög'
        elif risk_value >= 4:
            return 'Medel'
        else:
            return 'Låg'

    def generate_heatmap(self, risker, output_path):
        """
        Generera heat map med risker plottade

        Args:
            risker: Lista med risk-dictionaries från risk_workshop_modul
            output_path: Var bilden ska sparas
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Rita basfärger för varje cell
        for i in range(5):
            for j in range(5):
                risk_value = self.risk_matrix[i, j]
                color = self._get_risk_color(risk_value)

                # Rita rektangel
                rect = FancyBboxPatch(
                    (j, 4-i), 1, 1,
                    boxstyle="round,pad=0.02",
                    facecolor=color,
                    edgecolor=self.COLORS['grid'],
                    linewidth=2,
                    alpha=0.3
                )
                ax.add_patch(rect)

                # Lägg till riskvärde i cellen
                ax.text(j + 0.5, 4-i + 0.5, str(risk_value),
                       ha='center', va='center',
                       fontsize=14, fontweight='bold',
                       color=self.COLORS['text'], alpha=0.4)

        # Plotta risker som punkter
        risk_counts = {}  # Räkna risker per cell för att stapla dem
        skipped_risks = []  # För debugging
        plotted_risks = []  # För debugging

        logger.info(f"=== HEAT MAP DEBUG: Börjar plotta {len(risker)} risker ===")

        for i, risk in enumerate(risker):
            # Hämta sannolikhet och konsekvens
            sannolikhet = risk.get('Sannolikhet', risk.get('sannolikhet', 0))
            konsekvens = risk.get('Konsekvensnivå', risk.get('konsekvens', 0))
            riskniva = risk.get('Risknivå', '')
            risk_id = risk.get('Risk-ID', f'R{i}')

            if sannolikhet == 0 or konsekvens == 0:
                skipped_risks.append(f"{risk_id} ({riskniva}) - S:{sannolikhet}, K:{konsekvens}")
                continue

            # Konvertera till grid-koordinater (0-indexed)
            x = konsekvens - 1
            y = 5 - sannolikhet  # Inverterat eftersom y=0 är längst upp

            plotted_risks.append(f"{risk_id} ({riskniva}) - S:{sannolikhet}, K:{konsekvens} → Grid({x},{y})")

            # Räkna risker i denna cell
            cell_key = (x, y)
            risk_counts[cell_key] = risk_counts.get(cell_key, 0) + 1
            count = risk_counts[cell_key]

            # Offset för att stapla punkter
            offset_x = 0.2 * ((count - 1) % 3 - 1)  # -0.2, 0, 0.2
            offset_y = 0.15 * ((count - 1) // 3)

            # Rita punkt
            circle = plt.Circle(
                (x + 0.5 + offset_x, y + 0.5 - offset_y),
                0.12,
                color=self.COLORS['neab_blue'],
                alpha=0.8,
                zorder=10
            )
            ax.add_patch(circle)

        # Logga sammanfattning
        logger.info(f"=== HEAT MAP SAMMANFATTNING ===")
        logger.info(f"Plottade {len(plotted_risks)} risker:")
        for pr in plotted_risks[:10]:  # Visa första 10
            logger.info(f"  ✓ {pr}")
        if len(plotted_risks) > 10:
            logger.info(f"  ... och {len(plotted_risks) - 10} till")

        if skipped_risks:
            logger.warning(f"Skippade {len(skipped_risks)} risker (0-värden):")
            for sr in skipped_risks[:5]:
                logger.warning(f"  ✗ {sr}")

        # Konfigurera axlar
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')

        # X-axel (Konsekvens)
        ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5])
        ax.set_xticklabels(['1\nLiten', '2\nMindre', '3\nMåttlig', '4\nAllvarlig', '5\nKatastrofal'],
                          fontsize=10, fontweight='bold')
        ax.set_xlabel('Konsekvens', fontsize=12, fontweight='bold',
                     color=self.COLORS['neab_blue'], labelpad=10)

        # Y-axel (Sannolikhet)
        ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5])
        ax.set_yticklabels(['5\nStor', '4\nMedel', '3\nViss', '2\nLiten', '1\nMycket liten'],
                          fontsize=10, fontweight='bold')
        ax.set_ylabel('Sannolikhet', fontsize=12, fontweight='bold',
                     color=self.COLORS['neab_blue'], labelpad=10)

        # Ta bort ram
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Lägg till titel
        ax.set_title('Riskmatris - NEAB Security Assessment',
                    fontsize=14, fontweight='bold', pad=20,
                    color=self.COLORS['neab_blue'])

        # Lägg till legend
        legend_elements = [
            mpatches.Patch(facecolor=self.COLORS['critical'], alpha=0.6,
                          edgecolor=self.COLORS['grid'], linewidth=2,
                          label='Mycket hög (15-25)'),
            mpatches.Patch(facecolor=self.COLORS['high'], alpha=0.6,
                          edgecolor=self.COLORS['grid'], linewidth=2,
                          label='Hög (8-12)'),
            mpatches.Patch(facecolor=self.COLORS['medium'], alpha=0.6,
                          edgecolor=self.COLORS['grid'], linewidth=2,
                          label='Medel (4-6)'),
            mpatches.Patch(facecolor=self.COLORS['low'], alpha=0.6,
                          edgecolor=self.COLORS['grid'], linewidth=2,
                          label='Låg (1-3)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.COLORS['neab_blue'],
                      markersize=10, alpha=0.8, label='Identifierad risk')
        ]

        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1),
                 frameon=True, fancybox=True, shadow=True, fontsize=10)

        # Lägg till footer med statistik - räkna från faktiska Risknivå
        mycket_hog = sum(1 for r in risker if r.get('Risknivå', r.get('risknivå', '')) == 'Mycket hög')
        hog = sum(1 for r in risker if r.get('Risknivå', r.get('risknivå', '')) == 'Hög')
        medel = sum(1 for r in risker if r.get('Risknivå', r.get('risknivå', '')) == 'Medel')
        lag = sum(1 for r in risker if r.get('Risknivå', r.get('risknivå', '')) == 'Låg')

        footer_text = f"Totalt {len(risker)} risker identifierade | {mycket_hog} mycket höga | {hog} höga | {medel} medel | {lag} låga"
        fig.text(0.5, 0.02, footer_text, ha='center', fontsize=10,
                color=self.COLORS['text'], style='italic')

        # Justera layout
        plt.tight_layout(rect=[0, 0.03, 0.85, 1])

        # Spara
        output_path = Path(output_path)
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        return output_path


def generate_risk_heatmap(risker, output_path):
    """
    Convenience function för att generera heat map

    Args:
        risker: Lista med risk-dictionaries
        output_path: Sökväg där bilden ska sparas

    Returns:
        Path till den genererade bilden
    """
    heatmap = RiskHeatMap(figsize=(10, 8))
    return heatmap.generate_heatmap(risker, output_path)


if __name__ == "__main__":
    # Test med dummy-data
    test_risker = [
        {'Sannolikhet': 5, 'Konsekvensnivå': 5, 'Riskvärde': 25},  # Mycket hög
        {'Sannolikhet': 4, 'Konsekvensnivå': 4, 'Riskvärde': 16},  # Mycket hög
        {'Sannolikhet': 3, 'Konsekvensnivå': 5, 'Riskvärde': 15},  # Mycket hög
        {'Sannolikhet': 3, 'Konsekvensnivå': 4, 'Riskvärde': 12},  # Hög
        {'Sannolikhet': 2, 'Konsekvensnivå': 4, 'Riskvärde': 8},   # Hög
        {'Sannolikhet': 2, 'Konsekvensnivå': 3, 'Riskvärde': 6},   # Medel
        {'Sannolikhet': 2, 'Konsekvensnivå': 2, 'Riskvärde': 4},   # Medel
        {'Sannolikhet': 1, 'Konsekvensnivå': 2, 'Riskvärde': 2},   # Låg
    ]

    generate_risk_heatmap(test_risker, 'test_heatmap.png')
    print("Test heat map genererad: test_heatmap.png")