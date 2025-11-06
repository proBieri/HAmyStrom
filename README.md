# myStrom Switch Integration for Home Assistant

Eine HACS Integration für myStrom WiFi-Schaltsteckdosen mit voller Unterstützung für das Home Assistant Energy Monitoring.

## Features

- ✅ Schalten der myStrom WiFi-Steckdosen
- ✅ Echtzeit-Leistungsmessung (Watt)
- ✅ Energieverbrauch-Tracking (kWh)
- ✅ Temperaturüberwachung
- ✅ Integration mit Home Assistant Energy Dashboard
- ✅ Auto-Discovery Unterstützung
- ✅ Manuelle Konfiguration per IP-Adresse
- ✅ Lokale Kommunikation (kein Cloud-Dienst erforderlich)

## Unterstützte Geräte

- myStrom WiFi Switch (CH)
- myStrom WiFi Switch EU

## Installation

### HACS (Empfohlen)

1. Öffnen Sie HACS in Ihrer Home Assistant Installation
2. Klicken Sie auf "Integrationen"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Custom repositories"
4. Fügen Sie die Repository-URL hinzu: `https://github.com/proBieri/HAmyStrom`
5. Wählen Sie die Kategorie "Integration"
6. Klicken Sie auf "Hinzufügen"
7. Suchen Sie nach "myStrom Switch" und klicken Sie auf "Herunterladen"
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie den neuesten Release herunter
2. Kopieren Sie den Ordner `custom_components/mystrom_switch` in Ihr Home Assistant `config/custom_components/` Verzeichnis
3. Starten Sie Home Assistant neu

## Konfiguration

### UI Konfiguration (Empfohlen)

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **+ Integration hinzufügen**
3. Suchen Sie nach **myStrom Switch**
4. Geben Sie die IP-Adresse Ihrer myStrom-Steckdose ein
5. Fertig!

### Auto-Discovery

Die Integration unterstützt automatische Erkennung von myStrom-Geräten im Netzwerk. Neu erkannte Geräte erscheinen automatisch in den Benachrichtigungen.

## Verwendung

### Entities

Nach der Einrichtung werden folgende Entities erstellt:

#### Switch
- `switch.mystrom_switch_xxx` - Hauptschalter zum Ein-/Ausschalten der Steckdose

#### Sensoren
- `sensor.mystrom_switch_xxx_power` - Aktuelle Leistungsaufnahme in Watt
- `sensor.mystrom_switch_xxx_energy` - Kumulierter Energieverbrauch in kWh
- `sensor.mystrom_switch_xxx_temperature` - Gerätetemperatur in °C

### Energy Dashboard Integration

1. Gehen Sie zu **Einstellungen** → **Dashboards** → **Energie**
2. Klicken Sie auf **Verbrauch hinzufügen**
3. Wählen Sie den Energy Sensor Ihrer myStrom-Steckdose
4. Optional: Ordnen Sie das Gerät einem Raum oder Gerät zu

Der Energieverbrauch wird nun automatisch im Energy Dashboard erfasst und visualisiert.

### Automatisierungsbeispiel

```yaml
automation:
  - alias: "Kaffeemaschine ausschalten nach 2 Stunden"
    trigger:
      - platform: state
        entity_id: switch.mystrom_switch_kaffeemaschine
        to: "on"
        for:
          hours: 2
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.mystrom_switch_kaffeemaschine
      - service: notify.mobile_app
        data:
          message: "Kaffeemaschine wurde automatisch ausgeschaltet"

  - alias: "Benachrichtigung bei hohem Energieverbrauch"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mystrom_switch_heizung_power
        above: 1500
    action:
      - service: notify.mobile_app
        data:
          message: "Achtung: Hoher Energieverbrauch bei {{ trigger.to_state.attributes.friendly_name }}: {{ trigger.to_state.state }} W"
```

## API Endpunkte

Die Integration nutzt die lokale REST API der myStrom-Geräte:

- `GET /report` - Status und Messwerte abrufen
- `GET /relay?state=1` - Einschalten
- `GET /relay?state=0` - Ausschalten
- `GET /toggle` - Umschalten
- `GET /info` - Geräteinformationen

## Troubleshooting

### Gerät wird nicht gefunden
- Stellen Sie sicher, dass das Gerät mit dem gleichen Netzwerk verbunden ist
- Überprüfen Sie die IP-Adresse des Geräts (z.B. in der myStrom App oder im Router)
- Stellen Sie sicher, dass keine Firewall die Kommunikation blockiert

### Sensoren zeigen keine Werte
- Überprüfen Sie, ob das Gerät erreichbar ist
- Prüfen Sie die Home Assistant Logs unter **Einstellungen** → **System** → **Protokolle**
- Das Update-Intervall beträgt 30 Sekunden

### Energy Sensor zeigt falsche Werte
Der Energy Sensor berechnet den Verbrauch basierend auf den Leistungsmessungen. Die Genauigkeit hängt vom Update-Intervall ab. Für genaueste Messungen sollte das Gerät kontinuierlich erreichbar sein.

## Entwicklung

### Voraussetzungen
- Home Assistant Core >= 2024.1.0
- Python >= 3.11

### Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/proBieri/HAmyStrom.git
cd HAmyStrom

# In Home Assistant custom_components Ordner verlinken
ln -s $(pwd)/custom_components/mystrom_switch /path/to/homeassistant/config/custom_components/

# Home Assistant neu starten
```

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details

## Credits

Entwickelt für die Home Assistant Community

## Support

Bei Problemen oder Fragen erstellen Sie bitte ein [Issue auf GitHub](https://github.com/proBieri/HAmyStrom/issues).
