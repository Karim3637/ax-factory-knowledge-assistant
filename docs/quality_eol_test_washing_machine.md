# QA-WI-021: End-of-Line (EOL) Test – Washing Machine Assembly Line
(Fictional sample document created for demo purposes – not an official company document)

## 1. Purpose
Ensure every finished washing machine passes functional and safety checks before packing.

## 2. EOL Test Procedure
Step 1 – Visual inspection: Check the cabinet for scratches, dents, and correct label placement (rating label, energy label, serial number).
Step 2 – Electrical safety test: Perform hi-pot test at 1,250 V AC for 1 second and earth continuity test (resistance must be below 0.1 ohm).
Step 3 – Water inlet test: Connect to the test water supply and confirm fill to the programmed level within 90 seconds with no leaks.
Step 4 – Drum rotation test: Run the "Test Mode" program; drum must reach the rated spin speed and vibration must stay below the threshold shown on the tester.
Step 5 – Drain test: Pump must fully drain the drum within 60 seconds.
Step 6 – Door lock test: Confirm the door locks at program start and unlocks within 2 minutes after the cycle ends.
Step 7 – Record result: Scan the serial barcode; the tester uploads PASS/FAIL automatically to the MES.

## 3. Failure Handling
Any FAIL unit must be moved to the red repair area with a red tag stating the failed step.
If the same failure occurs on 3 consecutive units, stop the line and inform the line leader and the QA engineer immediately.
Repaired units must repeat the full EOL test, not only the failed step.

## 4. Common Failure Codes
F-21 Leak detected during water inlet test – check inlet hose clamp and detergent drawer seal.
F-34 Door lock failure – check door lock wiring harness connector.
F-47 Excessive vibration – check shipping bolt removal and suspension springs.

## 5. Contacts
QA engineer on shift: ext. 2450. Line leader: radio channel 3.
