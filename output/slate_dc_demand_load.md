# Slate 2026 RV – DC Demand Load Calculation

WAC 296-150R (Washington State RV standards, which adopt NFPA 1192 and
reference NEC Article 551) requires a demand-load calculation that
justifies the sizing of the DC charging source vs. the connected DC loads.

The calculation below uses:

- **Fuse rating** – branch-circuit over-current device (conductor-sizing
  reference only, *not* a demand value).
- **Running current** – nominal DC current the device draws while
  operating, from manufacturer data or typical industry values @12.8 V.
- **Duty factor** – estimated fraction of time the load is *actively*
  drawing current during the worst hour of operation. Diversity is
  applied because not every circuit runs at maximum simultaneously.
- **Demand (A)** = *Running current × Duty factor*.

## DC Branch-Circuit Demand Load

| Branch Circuit                         |  Fuse | Running (A) | Duty | Demand (A) |
| -------------------------------------- | ----: | ----------: | ---: | ---------: |
| Refrigerator (Indel B 65L compressor)  |   10A |         5.0 |  40% |       2.00 |
| Diesel Heater (Espar D2L, running)     |   15A |         1.5 |  50% |       0.75 |
| USB-C 100W charging port               |   15A |         8.3 |  20% |       1.66 |
| USB-A 1 (3.4 A dual-port)              |   10A |         3.4 |  15% |       0.51 |
| USB-A 2 (3.4 A dual-port)              |   10A |         3.4 |  15% |       0.51 |
| 12V Power Socket 1                     |   15A |         5.0 |  20% |       1.00 |
| 12V Power Socket 2                     |   15A |         5.0 |  20% |       1.00 |
| Reading Lights (LED)                   |  7.5A |         1.5 |  50% |       0.75 |
| Ceiling Puck Lights (6× LED, dimmable) |   10A |         3.0 |  60% |       1.80 |
| Water Pump                             |   15A |         5.0 |  15% |       0.75 |
| Fan 1 (roof vent fan)                  |  7.5A |         2.0 |  30% |       0.60 |
| Fan 2 (roof vent fan)                  |  7.5A |         2.0 |  30% |       0.60 |
| **Total DC Demand Load**               |       |             |      |  **11.93** |

## Charging Capacity vs. Demand

| Source                                        |   Rated | Notes                                                 |
| --------------------------------------------- | ------: | ----------------------------------------------------- |
| DC-DC + MPPT Charger (Renogy RBC50D1S-G7-US)  | **50 A** | Main charge source to House Battery                   |
| Calculated DC Demand Load (above)             | 11.93 A | **≈ 24 % of charger capacity**                        |
| Headroom available for battery recharge       | 38.07 A | Excess capacity while loads operate at demand factor  |

Result: the 50 A DC-DC charger exceeds the calculated DC demand load by a
factor of ≈ 4.2×, leaving sufficient headroom to simultaneously supply
connected loads and recharge the 200 Ah LiFePO4 house battery.

## Connected (Nameplate) Load – Reference Only

Used for conductor-sizing and protection, *not* for demand sizing:

| Metric                                        |   Value |
| --------------------------------------------- | ------: |
| Sum of all DC branch fuses                    | 137.5 A |
| Largest single DC branch fuse                 |    15 A |
| Main DC Breaker (battery to distribution)     |   200 A |
| 60A Main Charge Protection (DC-DC → battery)  |    60 A |
| 80A Alternator Protection (chassis → DC-DC)   |    80 A |
| 25A Solar Input Protection (solar → DC-DC)    |    25 A |
| House Battery (12 V, 200 Ah LiFePO4)          | 2.4 kWh |

## Assumptions

1. Duty factors are engineering estimates for a typical "worst hour" of
   simultaneous use and should be ratified by the RVIA-compliant engineer
   of record before certification.
2. All DC-side marine conductors are tinned copper rated at 125 °C
   insulation per the BOM; the 4 AWG alternator-path and battery-path
   conductors are verified in the schematic wire labels.
3. AC loads (GFCI 1, GFCI 2, Optional Air Conditioner) are evaluated on a
   separate AC demand-load calculation and are **not** included in this
   DC total.
4. Inverter/charger DC input is not a load on the DC distribution panel
   — it is on the main positive rail upstream of the panel — and is
   therefore excluded from this demand calculation.
5. Running currents assume nominal 12.8 V bus voltage; worst-case
   low-voltage cut-off (11.0 V) would raise individual currents by
   ≈ 16 %, still leaving the charger adequately sized.

## Conclusion

The Slate 2026 DC system has ~38 A of charger headroom above calculated
DC demand, and the alternator-side (4 AWG, 80 A breaker) and
charger-output-side (4 AWG, 60 A breaker) conductors match the detail
image. The system as drafted satisfies the WAC 296-150R demand-sizing
justification requirement.
