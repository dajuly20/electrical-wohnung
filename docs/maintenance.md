# Wartungs- und Notfall-Checkliste

**Installation:** Ludwigshafen am Rhein  
**Dokumentiert:** 2026-02-16

## Regelmäßige Wartung

### Monatlich
- [ ] FI-Schutzschalter testen (Prüftaste)
- [ ] Shelly Pro3EM auf Fehlermeldungen prüfen
- [ ] Lastbalance checken

### Halbjährlich
- [ ] Alle Sicherungen auf festen Sitz prüfen
- [ ] Verteiler-Klemmen nachziehen
- [ ] Shelly Firmware-Update prüfen

## Notfall-Abschaltung

### Bei Problemen in Räumen/Bereichen:

**F1** (B16) - Phase TBD  
→ Versorgt: 

**F2** (B16) - Phase TBD  
→ Versorgt: 

**F3** (B16) - Phase TBD  
→ Versorgt: 

**F4** (B16) - Phase TBD  
→ Versorgt: 

**F5** (B16) - Phase TBD  
→ Versorgt: 

**F6** (B16) - Phase TBD  
→ Versorgt: 

**F7** (B16) - Phase L2  
→ Versorgt: Julians Zimmer, Balkon groß

### Komplett-Abschaltung:
1. **Hauptsicherung** (Diazed 63A) ausschalten
2. Bei FI-Auslösung: Ursache finden vor Wiedereinschalten
3. Niemals FI überbrücken!

## Fehlerbehebung

### FI löst aus:
1. Alle Sicherungen ausschalten
2. FI wieder einschalten
3. Sicherungen einzeln wieder einschalten
4. Bei erneutem Auslösen: Fehler auf diesem Stromkreis

### Shelly "Phase Sequence Error":
- **Ursache:** Phasenfolge nicht L1-L2-L3
- **Behebung:** Phasen am Shelly umklemmen
- **Hinweis:** Bei nur einphasigen Verbrauchern elektrisch unkritisch

## Kontakte

- **Elektriker:** [TBD]
- **Energieversorger:** [TBD]
- **Notdienst Elektro:** [TBD]
