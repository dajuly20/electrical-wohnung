# Elektrische Installation - Wohnungsdokumentation

Systematische Dokumentation der elektrischen Installation mit automatischer Generierung von Schaltplänen, Lastanalysen und Wartungschecklisten.

## Struktur

```
electrical-wohnung/
├── data/
│   └── wiring.yaml          # Zentrale Datendatei (hier eintragen!)
├── output/                  # Generierte Dateien
│   ├── schematic.svg        # SVG-Stromlaufplan
│   ├── homeassistant.yaml   # Home Assistant Config
│   ├── phase_distribution.csv
│   └── breakers.csv
├── docs/                    # Dokumentation
│   ├── installation.md      # Markdown-Tabelle
│   ├── schematic.mmd        # Mermaid-Diagramm
│   ├── load_balance.md      # Lastanalyse
│   └── maintenance.md       # Wartungscheckliste
├── generate.py              # Generator-Skript
└── README.md
```

## Verwendung

### 1. Daten eintragen

Bearbeite `data/wiring.yaml` und trage die Ergebnisse vom Wasserkocher-Test ein:

```yaml
breakers:
  F1:
    type: "B16"
    phase: "L1"  # ← hier eintragen
    rooms: ["Küche", "Bad"]  # ← hier eintragen
```

### 2. Dokumentation generieren

```bash
chmod +x generate.py
./generate.py
```

### 3. Ergebnisse prüfen

- **SVG-Plan:** `output/schematic.svg` (im Browser öffnen)
- **Markdown:** `docs/installation.md` (in Git anzeigen)
- **Home Assistant:** `output/homeassistant.yaml` (in HA einbinden)

## Features

### a) SVG-Stromlaufplan
Visualisierung: Zähler → Hauptsicherung → FI → Shelly → Phasen → Sicherungen

### b) Lastbalancierungs-Analyse
- Aktuelle Auslastung pro Phase
- Empfehlungen zur Optimierung
- Warnung bei Ungleichgewicht

### c) Home Assistant Config
- MQTT-Sensoren für jede Phase
- Gesamtverbrauch-Template
- Automatisierung bei hoher Last
- Kostenkalkulation

### d) Wartungs-Checkliste
- Regelmäßige Prüfintervalle
- Notfall-Abschaltung
- Fehlerbehebungs-Guide

## Wasserkocher-Test Anleitung

1. Wasserkocher in Steckdose stecken
2. Einschalten und 10 Sekunden warten
3. Shelly-Interface aufrufen: `http://10.0.0.77`
4. Nachschauen, welche Phase ~2000W anzeigt
5. In `wiring.yaml` eintragen:
   ```yaml
   breakers:
     FX:
       phase: "L2"  # die Phase mit 2000W
       rooms: ["Raum XYZ"]
   ```
6. Nächster Raum

## Git Workflow

```bash
# Nach Änderungen an wiring.yaml
./generate.py
git add .
git commit -m "Update: Raum XYZ zugeordnet"
git push
```

## Technische Details

### Hauptkomponenten
- **Hauptsicherung:** Diazed 63A
- **FI:** 30mA (Typ TBD)
- **Energiemonitor:** Shelly Pro3EM (Firmware 1.7.4)
- **Sicherungen:** alle B16

### Phasencodierung
- L1: Schwarz (10mm²)
- L2: Braun (10mm²)
- L3: Blau (10mm²)

### Bekannte Probleme
- **Phase Sequence Error** am Shelly: Phasenfolge nicht L1-L2-L3 (elektrisch unkritisch bei nur einphasigen Verbrauchern)

## Dependencies

- Python 3.x (nur stdlib, keine externen Packages!)
- PyYAML (für wiring.yaml)

Installation:
```bash
sudo apt install python3-yaml
```

## Lizenz

Privates Projekt - keine Lizenz erforderlich

## Kontakt

Julian - Ludwigshafen am Rhein
