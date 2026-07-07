
This dataset simulates real-world medical/RWD data for Python, Pandas, and SQL practice.

## Files

- patients.csv
- visits.csv
- diagnoses.csv
- labs.csv
- medications.csv
- icd10_reference.csv
- lab_reference.csv
- briya_practice.db

## Intentional data-quality issues

Use these for validation practice:

- Duplicate patient_id with conflicting gender: P003
- Future birth date: P007
- Missing gender: P009
- Missing birth_date: P010
- Visits/labs after death: P008
- Rows referencing patients not in patients table: P011, P012
- Suspicious HbA1c unit/value: 250 mg/dL
- Invalid HbA1c value: -1
- Invalid lab date: bad_date
- Male patient with pregnancy-related ICD10 code: P006 with O80

## Recommended practice tasks

1. Load all CSVs using Pandas.
2. Parse all dates safely with errors="coerce".
3. Count patients by site.
4. Find diabetic patients using ICD10 E11.
5. Find latest HbA1c per patient.
6. Find diabetic patients without HbA1c.
7. Validate missing patients across tables.
8. Detect duplicate patients.
9. Detect visits/labs after death.
10. Write equivalent SQL queries using the SQLite database.
# pandassql
