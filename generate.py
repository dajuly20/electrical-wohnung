#!/usr/bin/env python3
"""
Elektrischer Schaltplan Generator
Generiert Dokumentation aus wiring.yaml
"""

import yaml
import csv
import os
from datetime import datetime
from pathlib import Path

class ElectricalDocGenerator:
    def __init__(self, data_file='data/wiring.yaml'):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        self.output_dir = Path('output')
        self.docs_dir = Path('docs')
        self.output_dir.mkdir(exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)
        
    def generate_all(self):
        """Generiere alle Outputs"""
        print("🔧 Generiere Dokumentation...")
        self.generate_markdown_table()
        self.generate_mermaid_diagram()
        self.generate_csv()
        self.generate_svg_schematic()
        self.generate_load_balance()
        self.generate_homeassistant_config()
        self.generate_maintenance_checklist()
        print("✅ Fertig! Alle Dateien in output/ und docs/")
        
    def generate_markdown_table(self):
        """Generiere Markdown-Tabelle"""
        output = f"# Elektrische Installation - Wohnung Julian\n\n"
        output += f"**Dokumentiert am:** {self.data['installation']['date_documented']}  \n"
        output += f"**Standort:** {self.data['installation']['location']}\n\n"
        
        output += "## Hauptkomponenten\n\n"
        output += f"- **Hauptsicherung:** {self.data['main_components']['main_breaker']['type']} "
        output += f"{self.data['main_components']['main_breaker']['rating']}\n"
        output += f"- **FI-Schutzschalter:** {self.data['main_components']['rcd']['rating']}\n"
        output += f"- **Energiemonitor:** {self.data['main_components']['energy_monitor']['model']}\n\n"
        
        output += "## Phasenverteilung\n\n"
        output += "| Phase | Farbe | Aktuelle Last | Sicherungen | Räume/Verbraucher |\n"
        output += "|-------|-------|---------------|-------------|-------------------|\n"
        
        for phase_name, phase_data in self.data['phase_distribution'].items():
            color = phase_data['color']
            load = phase_data['current_load_w']
            loads_str = "<br>".join([f"- {l.get('room', l.get('device', 'N/A'))}" 
                                     for l in phase_data['loads']]) if phase_data['loads'] else "—"
            breakers = ", ".join(set([l.get('breaker', '') for l in phase_data['loads'] 
                                      if l.get('breaker')])) or "TBD"
            output += f"| {phase_name} | {color} | {load}W | {breakers} | {loads_str} |\n"
        
        output += "\n## Sicherungen\n\n"
        output += "| Sicherung | Typ | Phase | Farbe | Räume |\n"
        output += "|-----------|-----|-------|-------|-------|\n"
        
        for breaker_name, breaker_data in sorted(self.data['breakers'].items()):
            phase = breaker_data.get('phase', 'TBD')
            color = breaker_data.get('color', '—')
            rooms = ", ".join(breaker_data.get('rooms', [])) or "TBD"
            output += f"| {breaker_name} | {breaker_data['type']} | {phase} | {color} | {rooms} |\n"
        
        output += "\n## Notizen\n\n"
        for note in self.data.get('notes', []):
            output += f"- {note}\n"
        
        output_file = self.docs_dir / 'installation.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"  ✓ Markdown: {output_file}")
        
    def generate_mermaid_diagram(self):
        """Generiere Mermaid-Diagramm"""
        output = "```mermaid\ngraph TB\n"
        output += "    Zaehler[Stromzähler<br/>3-Phasen]\n"
        output += "    Haupt[Hauptsicherung<br/>Diazed 63A]\n"
        output += "    FI[FI-Schutzschalter<br/>30mA]\n"
        output += "    Shelly[Shelly Pro3EM<br/>Energiemonitor]\n\n"
        
        output += "    Zaehler --> Haupt\n"
        output += "    Haupt --> FI\n"
        output += "    FI --> Shelly\n\n"
        
        # Phasen
        for phase_name, phase_data in self.data['phase_distribution'].items():
            color = phase_data['color']
            load = phase_data['current_load_w']
            output += f"    Shelly -->|{phase_name} {color}| {phase_name}[{phase_name}<br/>{color}<br/>{load}W]\n"
        
        output += "\n"
        
        # Sicherungen
        for breaker_name, breaker_data in sorted(self.data['breakers'].items()):
            phase = breaker_data.get('phase', 'TBD')
            if phase != 'TBD':
                rooms = breaker_data.get('rooms', [])
                rooms_str = "<br/>".join(rooms) if rooms else "TBD"
                output += f"    {phase} --> {breaker_name}[{breaker_name}<br/>{breaker_data['type']}<br/>{rooms_str}]\n"
        
        output += "```\n"
        
        output_file = self.docs_dir / 'schematic.mmd'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"  ✓ Mermaid: {output_file}")
        
    def generate_csv(self):
        """Generiere CSV-Export"""
        # Phase distribution CSV
        phase_file = self.output_dir / 'phase_distribution.csv'
        with open(phase_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Phase', 'Farbe', 'Aktuelle Last (W)', 'Verbraucher'])
            for phase_name, phase_data in self.data['phase_distribution'].items():
                loads = "; ".join([l.get('room', l.get('device', 'N/A')) 
                                   for l in phase_data['loads']])
                writer.writerow([
                    phase_name,
                    phase_data['color'],
                    phase_data['current_load_w'],
                    loads or 'TBD'
                ])
        
        # Breakers CSV
        breaker_file = self.output_dir / 'breakers.csv'
        with open(breaker_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Sicherung', 'Typ', 'Phase', 'Farbe', 'Räume'])
            for breaker_name, breaker_data in sorted(self.data['breakers'].items()):
                writer.writerow([
                    breaker_name,
                    breaker_data['type'],
                    breaker_data.get('phase', 'TBD'),
                    breaker_data.get('color', ''),
                    '; '.join(breaker_data.get('rooms', []))
                ])
        
        print(f"  ✓ CSV: {phase_file}, {breaker_file}")
        
    def generate_svg_schematic(self):
        """Generiere SVG-Stromlaufplan"""
        width, height = 1200, 800
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <style>
      .title {{ font: bold 20px sans-serif; }}
      .label {{ font: 14px sans-serif; }}
      .small {{ font: 12px sans-serif; }}
      .wire {{ stroke: #333; stroke-width: 2; fill: none; }}
      .wire-l1 {{ stroke: #000; stroke-width: 3; }}
      .wire-l2 {{ stroke: #8B4513; stroke-width: 3; }}
      .wire-l3 {{ stroke: #0066CC; stroke-width: 3; }}
      .component {{ fill: #f0f0f0; stroke: #333; stroke-width: 2; }}
      .breaker {{ fill: #fff; stroke: #333; stroke-width: 1.5; }}
    </style>
  </defs>
  
  <text x="600" y="30" class="title" text-anchor="middle">Elektrische Installation - Wohnung Julian</text>
  <text x="600" y="50" class="small" text-anchor="middle">{self.data['installation']['date_documented']}</text>
  
  <!-- Zähler -->
  <rect x="50" y="80" width="100" height="80" class="component"/>
  <text x="100" y="110" class="label" text-anchor="middle">Stromzähler</text>
  <text x="100" y="130" class="small" text-anchor="middle">3-Phasen</text>
  
  <!-- Hauptsicherung -->
  <rect x="200" y="80" width="100" height="80" class="component"/>
  <text x="250" y="110" class="label" text-anchor="middle">Haupt-Sicherung</text>
  <text x="250" y="130" class="small" text-anchor="middle">Diazed 63A</text>
  
  <!-- FI -->
  <rect x="350" y="80" width="100" height="80" class="component"/>
  <text x="400" y="110" class="label" text-anchor="middle">FI-Schalter</text>
  <text x="400" y="130" class="small" text-anchor="middle">30mA</text>
  
  <!-- Shelly -->
  <rect x="500" y="80" width="120" height="80" class="component"/>
  <text x="560" y="110" class="label" text-anchor="middle">Shelly Pro3EM</text>
  <text x="560" y="130" class="small" text-anchor="middle">Energiemonitor</text>
  
  <!-- Verbindungen -->
  <line x1="150" y1="120" x2="200" y2="120" class="wire"/>
  <line x1="300" y1="120" x2="350" y2="120" class="wire"/>
  <line x1="450" y1="120" x2="500" y2="120" class="wire"/>
  
  <!-- Phasen-Verteilung -->
'''
        
        y_phase = 200
        phase_colors = {'L1': 'wire-l1', 'L2': 'wire-l2', 'L3': 'wire-l3'}
        phase_y = {'L1': y_phase, 'L2': y_phase + 80, 'L3': y_phase + 160}
        
        for phase_name, phase_data in self.data['phase_distribution'].items():
            y = phase_y[phase_name]
            color_class = phase_colors[phase_name]
            
            # Phase aus Shelly
            svg += f'  <line x1="620" y1="120" x2="700" y2="{y}" class="{color_class}"/>\n'
            svg += f'  <circle cx="700" cy="{y}" r="5" fill="{phase_data["color"]}"/>\n'
            svg += f'  <text x="720" y="{y+5}" class="label">{phase_name} ({phase_data["color"]}) - {phase_data["current_load_w"]}W</text>\n'
            
            # Sicherungen auf dieser Phase
            x_breaker = 850
            for breaker_name, breaker_data in sorted(self.data['breakers'].items()):
                if breaker_data.get('phase') == phase_name:
                    rooms = ", ".join(breaker_data.get('rooms', ['TBD']))[:30]
                    svg += f'  <rect x="{x_breaker}" y="{y-20}" width="80" height="40" class="breaker"/>\n'
                    svg += f'  <text x="{x_breaker+40}" y="{y}" class="small" text-anchor="middle">{breaker_name}</text>\n'
                    svg += f'  <text x="{x_breaker+40}" y="{y+15}" class="small" text-anchor="middle" font-size="10">{rooms}</text>\n'
                    svg += f'  <line x1="700" y1="{y}" x2="{x_breaker}" y2="{y}" class="{color_class}"/>\n'
                    x_breaker += 120
        
        svg += '</svg>'
        
        output_file = self.output_dir / 'schematic.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"  ✓ SVG: {output_file}")
        
    def generate_load_balance(self):
        """Generiere Lastbalancierungs-Analyse"""
        output = "# Lastbalancierungs-Analyse\n\n"
        output += f"**Stand:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        total_load = sum(p['current_load_w'] for p in self.data['phase_distribution'].values())
        max_load_per_phase = 16 * 230  # 16A * 230V = 3680W
        
        output += "## Aktuelle Lastverteilung\n\n"
        output += "| Phase | Last (W) | Last (A) | Auslastung | Status |\n"
        output += "|-------|----------|----------|------------|--------|\n"
        
        for phase_name, phase_data in self.data['phase_distribution'].items():
            load_w = phase_data['current_load_w']
            load_a = load_w / 230
            utilization = (load_w / max_load_per_phase) * 100
            status = "✅ OK" if utilization < 50 else "⚠️ Hoch" if utilization < 80 else "❌ Kritisch"
            output += f"| {phase_name} | {load_w}W | {load_a:.2f}A | {utilization:.1f}% | {status} |\n"
        
        output += f"\n**Gesamt:** {total_load}W ({total_load/230:.2f}A)\n"
        output += f"**Maximale Kapazität pro Phase:** {max_load_per_phase}W (16A @ 230V)\n\n"
        
        # Balance-Check
        loads = [p['current_load_w'] for p in self.data['phase_distribution'].values()]
        max_diff = max(loads) - min(loads)
        avg_load = sum(loads) / len(loads)
        imbalance_pct = (max_diff / avg_load * 100) if avg_load > 0 else 0
        
        output += "## Balance-Bewertung\n\n"
        output += f"- **Durchschnittslast:** {avg_load:.0f}W\n"
        output += f"- **Maximale Differenz:** {max_diff}W\n"
        output += f"- **Ungleichgewicht:** {imbalance_pct:.1f}%\n\n"
        
        if imbalance_pct > 50:
            output += "⚠️ **Empfehlung:** Lastverteilung optimieren! Verbraucher umverteilen.\n\n"
        else:
            output += "✅ **Status:** Balance akzeptabel.\n\n"
        
        output += "## Empfehlungen\n\n"
        if max_diff > 1000:
            max_phase = max(self.data['phase_distribution'].items(), 
                           key=lambda x: x[1]['current_load_w'])
            min_phase = min(self.data['phase_distribution'].items(), 
                           key=lambda x: x[1]['current_load_w'])
            output += f"- Verbraucher von **{max_phase[0]}** ({max_phase[1]['current_load_w']}W) "
            output += f"auf **{min_phase[0]}** ({min_phase[1]['current_load_w']}W) verschieben\n"
        else:
            output += "- Aktuelle Verteilung ist ausgewogen\n"
        
        output_file = self.docs_dir / 'load_balance.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"  ✓ Lastbalance: {output_file}")
        
    def generate_homeassistant_config(self):
        """Generiere Home Assistant YAML-Config"""
        output = "# Home Assistant - Shelly Pro3EM Integration\n"
        output += "# Kopiere in configuration.yaml oder packages/electrical.yaml\n\n"
        
        output += "sensor:\n"
        
        # Phase sensors
        for phase_name, phase_data in self.data['phase_distribution'].items():
            phase_num = phase_name[-1]  # L1 -> 1
            output += f"  - platform: mqtt\n"
            output += f"    name: \"Energie {phase_name}\"\n"
            output += f"    state_topic: \"shellypro3em-{self.data['main_components']['energy_monitor']['device_id']}/status/em:0\"\n"
            output += f"    value_template: \"{{{{ value_json.a_act_power }}}}\"\n"
            output += f"    unit_of_measurement: \"W\"\n"
            output += f"    device_class: power\n\n"
        
        output += "  # Gesamtverbrauch\n"
        output += "  - platform: template\n"
        output += "    sensors:\n"
        output += "      total_power:\n"
        output += "        friendly_name: \"Gesamtverbrauch\"\n"
        output += "        unit_of_measurement: \"W\"\n"
        output += "        value_template: >\n"
        output += "          {{ states('sensor.energie_l1')|float +\n"
        output += "             states('sensor.energie_l2')|float +\n"
        output += "             states('sensor.energie_l3')|float }}\n\n"
        
        output += "      # Kosten (Beispiel: 0.30 EUR/kWh)\n"
        output += "      power_cost_hourly:\n"
        output += "        friendly_name: \"Stromkosten pro Stunde\"\n"
        output += "        unit_of_measurement: \"EUR/h\"\n"
        output += "        value_template: >\n"
        output += "          {{ (states('sensor.total_power')|float / 1000 * 0.30)|round(2) }}\n\n"
        
        # Automations
        output += "automation:\n"
        output += "  - alias: \"Warnung bei hoher Last\"\n"
        output += "    trigger:\n"
        output += "      - platform: numeric_state\n"
        output += "        entity_id: sensor.total_power\n"
        output += "        above: 3000\n"
        output += "    action:\n"
        output += "      - service: notify.notify\n"
        output += "        data:\n"
        output += "          message: \"Hoher Stromverbrauch: {{ states('sensor.total_power') }}W\"\n"
        
        output_file = self.output_dir / 'homeassistant.yaml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"  ✓ Home Assistant: {output_file}")
        
    def generate_maintenance_checklist(self):
        """Generiere Wartungs-Checkliste"""
        output = "# Wartungs- und Notfall-Checkliste\n\n"
        output += f"**Installation:** {self.data['installation']['location']}  \n"
        output += f"**Dokumentiert:** {self.data['installation']['date_documented']}\n\n"
        
        output += "## Regelmäßige Wartung\n\n"
        output += "### Monatlich\n"
        output += "- [ ] FI-Schutzschalter testen (Prüftaste)\n"
        output += "- [ ] Shelly Pro3EM auf Fehlermeldungen prüfen\n"
        output += "- [ ] Lastbalance checken\n\n"
        
        output += "### Halbjährlich\n"
        output += "- [ ] Alle Sicherungen auf festen Sitz prüfen\n"
        output += "- [ ] Verteiler-Klemmen nachziehen\n"
        output += "- [ ] Shelly Firmware-Update prüfen\n\n"
        
        output += "## Notfall-Abschaltung\n\n"
        output += "### Bei Problemen in Räumen/Bereichen:\n\n"
        
        for breaker_name, breaker_data in sorted(self.data['breakers'].items()):
            rooms = ", ".join(breaker_data.get('rooms', ['TBD']))
            phase = breaker_data.get('phase', 'TBD')
            output += f"**{breaker_name}** ({breaker_data['type']}) - Phase {phase}  \n"
            output += f"→ Versorgt: {rooms}\n\n"
        
        output += "### Komplett-Abschaltung:\n"
        output += "1. **Hauptsicherung** (Diazed 63A) ausschalten\n"
        output += "2. Bei FI-Auslösung: Ursache finden vor Wiedereinschalten\n"
        output += "3. Niemals FI überbrücken!\n\n"
        
        output += "## Fehlerbehebung\n\n"
        output += "### FI löst aus:\n"
        output += "1. Alle Sicherungen ausschalten\n"
        output += "2. FI wieder einschalten\n"
        output += "3. Sicherungen einzeln wieder einschalten\n"
        output += "4. Bei erneutem Auslösen: Fehler auf diesem Stromkreis\n\n"
        
        output += "### Shelly \"Phase Sequence Error\":\n"
        output += "- **Ursache:** Phasenfolge nicht L1-L2-L3\n"
        output += "- **Behebung:** Phasen am Shelly umklemmen\n"
        output += "- **Hinweis:** Bei nur einphasigen Verbrauchern elektrisch unkritisch\n\n"
        
        output += "## Kontakte\n\n"
        output += "- **Elektriker:** [TBD]\n"
        output += "- **Energieversorger:** [TBD]\n"
        output += "- **Notdienst Elektro:** [TBD]\n"
        
        output_file = self.docs_dir / 'maintenance.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"  ✓ Wartung: {output_file}")

if __name__ == '__main__':
    generator = ElectricalDocGenerator()
    generator.generate_all()
