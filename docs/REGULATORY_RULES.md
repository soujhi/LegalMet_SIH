# Regulatory Rule Engine & Maximum Permissible Error (MPE)

## 1. Statutory Mandate
The Rule Engine executes deterministically under **Section 24 of the Legal Metrology Act, 2009** and the **Legal Metrology (General) Rules, 2011 (Seventh Schedule, Part-II)** aligned with **OIML R 76-1**.

## 2. Non-Automatic Weighing Instruments (NAWI) Rules

### Accuracy Class III (Medium Accuracy Scales — Retail, Trade, Mandis)
Verification scale interval $e = 5\,\text{g}$ (e.g. 30 kg digital counter scale):
| Load Range in Intervals ($m = \text{Load}/e$) | Initial Verification MPE | In-Service / Re-Verification MPE | Rule Code |
| :--- | :--- | :--- | :--- |
| $0 \le m \le 500\,e$ (0 to 2.5 kg) | $\pm 0.5\,e$ ($\pm 2.5\,\text{g}$) | $\pm 1.0\,e$ ($\pm 5.0\,\text{g}$) | `LM-NAWI-CL3-R1` |
| $500\,e < m \le 2000\,e$ (2.5 to 10 kg) | $\pm 1.0\,e$ ($\pm 5.0\,\text{g}$) | $\pm 2.0\,e$ ($\pm 10.0\,\text{g}$) | `LM-NAWI-CL3-R2` |
| $2000\,e < m \le 10000\,e$ (10 to 30 kg) | $\pm 1.5\,e$ ($\pm 7.5\,\text{g}$) | $\pm 3.0\,e$ ($\pm 15.0\,\text{g}$) | `LM-NAWI-CL3-R3` |

### Accuracy Class IIII (Ordinary Accuracy Scales — Mechanical Hanging, Spring)
Verification scale interval $e = 200\,\text{g}$ (e.g. 20 kg dial hanging scale):
| Load Range in Intervals ($m = \text{Load}/e$) | Initial Verification MPE | In-Service / Re-Verification MPE | Rule Code |
| :--- | :--- | :--- | :--- |
| $0 \le m \le 50\,e$ (0 to 10 kg) | $\pm 0.5\,e$ ($\pm 100\,\text{g}$) | $\pm 1.0\,e$ ($\pm 200\,\text{g}$) | `LM-NAWI-CL4-R1` |
| $50\,e < m \le 200\,e$ (10 to 20 kg) | $\pm 1.0\,e$ ($\pm 200\,\text{g}$) | $\pm 2.0\,e$ ($\pm 400\,\text{g}$) | `LM-NAWI-CL4-R2` |

## 3. Evaluation Algorithm
1. $\text{Error} = \text{Observed Reading} - \text{Standard Test Load}$.
2. Convert scale interval $e$ to load unit.
3. Compute number of verification intervals $m = \text{Test Load} / e$.
4. Determine applicable rule bracket from Accuracy Class and $m$.
5. Compute statutory $\text{MPE} = \text{Multiplier} \times e$.
6. Check condition:
   $$\text{Result} = \begin{cases} \text{PASS} & \text{if } |\text{Error}| \le \text{MPE} \\ \text{FAIL} & \text{if } |\text{Error}| > \text{MPE} \end{cases}$$
