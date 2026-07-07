## 30 Questions with Pandas + SQL Answers

Dataset files/tables: `patients`, `visits`, `diagnoses`, `labs`, `medications`, `icd10_reference`, `lab_reference`.

Assume in Pandas:

```python
import pandas as pd

patients = pd.read_csv("patients.csv")
visits = pd.read_csv("visits.csv")
diagnoses = pd.read_csv("diagnoses.csv")
labs = pd.read_csv("labs.csv")
medications = pd.read_csv("medications.csv")
icd10_reference = pd.read_csv("icd10_reference.csv")
lab_reference = pd.read_csv("lab_reference.csv")
```

Assume in SQL the table names are the same.

---

# Normal Questions

## 1. Count unique patients by site

### What exactly you need to do

The `patients` table may contain duplicate IDs. Group by `site` and count distinct `patient_id` values. Return one result row per site.

**Question:** How many unique patients are there in each site?

**Pandas**
```python
answer = (
    patients.groupby("site")["patient_id"]
    .nunique()
    .reset_index(name="unique_patients")
)
```

**SQL**
```sql
SELECT site, COUNT(DISTINCT patient_id) AS unique_patients
FROM patients
GROUP BY site;
```

**Explanation:** Use unique counts because the patients table may contain duplicate patient IDs.

---

## 2. Return female patients

### What exactly you need to do

Gender is not standardized. Return patient rows where gender is either `F` or `Female`; exclude `M`, `Male`, `Unknown`, and missing values.

**Question:** Return patients whose gender is `F` or `Female`.

**Pandas**
```python
answer = patients[patients["gender"].isin(["F", "Female"])]
```

**SQL**
```sql
SELECT *
FROM patients
WHERE gender IN ('F', 'Female');
```

**Explanation:** Use `isin()` / `IN` for multiple accepted values.

---

## 3. Find patients with missing gender

### What exactly you need to do

Return patient records where the gender field is truly missing (`NULL` in SQL or `NaN` in Pandas). Do not treat the text value `Unknown` as missing.

**Pandas**
```python
answer = patients[patients["gender"].isna()]
```

**SQL**
```sql
SELECT *
FROM patients
WHERE gender IS NULL;
```

**Explanation:** Missing values require `isna()` in Pandas and `IS NULL` in SQL.

---

## 4. Standardize gender

### What exactly you need to do

Create a new standardized field: `F` and `Female` → `F`; `M` and `Male` → `M`; every other value, including missing values, → `Unknown`.

**Question:** Create a standardized gender field with only `F`, `M`, or `Unknown`.

**Pandas**
```python
gender_map = {"Female": "F", "Male": "M", "F": "F", "M": "M"}
patients["gender_standardized"] = patients["gender"].map(gender_map).fillna("Unknown")
```

**SQL**
```sql
SELECT *,
       CASE
           WHEN gender IN ('F', 'Female') THEN 'F'
           WHEN gender IN ('M', 'Male') THEN 'M'
           ELSE 'Unknown'
       END AS gender_standardized
FROM patients;
```

**Explanation:** This is a simple harmonization task across sites.

---

## 5. Extract birth year

### What exactly you need to do

Parse `birth_date` as a date and create `birth_year`, containing only the year. In Pandas, invalid dates should become missing dates rather than raising an error.

**Pandas**
```python
patients["birth_date"] = pd.to_datetime(patients["birth_date"], errors="coerce")
answer = patients.assign(birth_year=patients["birth_date"].dt.year)
```

**SQL**
```sql
SELECT *, STRFTIME('%Y', birth_date) AS birth_year
FROM patients;
```

**Explanation:** Dates must be parsed before extracting year/month/day.

---

## 6. Count visits by department

### What exactly you need to do

Count visit rows per department. This is a count of visits, not distinct patients. Return one row per department.

**Pandas**
```python
answer = visits.groupby("department").size().reset_index(name="visit_count")
```

**SQL**
```sql
SELECT department, COUNT(*) AS visit_count
FROM visits
GROUP BY department;
```

**Explanation:** This is a basic row count by category.

---

## 7. Return all HbA1c labs

### What exactly you need to do

Filter `labs` to rows where `test_name` is exactly `HbA1c`. Keep all columns from those matching rows.

**Pandas**
```python
answer = labs[labs["test_name"] == "HbA1c"]
```

**SQL**
```sql
SELECT *
FROM labs
WHERE test_name = 'HbA1c';
```

**Explanation:** This filters the labs table to one lab test.

---

## 8. Count diagnoses by ICD10 code

### What exactly you need to do

Count diagnosis records per ICD10 code. Count rows, not unique patients, because this question asks about diagnosis-record volume.

**Pandas**
```python
answer = diagnoses.groupby("icd10").size().reset_index(name="diagnosis_rows")
```

**SQL**
```sql
SELECT icd10, COUNT(*) AS diagnosis_rows
FROM diagnoses
GROUP BY icd10;
```

**Explanation:** This counts diagnosis records, not unique patients.

---

## 9. Count patients with medication records

### What exactly you need to do

Count distinct patients with at least one medication record. Multiple medication rows for the same patient must count as one patient.

**Pandas**
```python
answer = medications["patient_id"].nunique()
```

**SQL**
```sql
SELECT COUNT(DISTINCT patient_id) AS patients_with_medications
FROM medications;
```

**Explanation:** A patient may have multiple medication rows, so use distinct counts.

---

## 10. Join visits with patient data

### What exactly you need to do

Add patient gender and patient site to every visit. Keep all visit rows even when a visit references a patient ID missing from the patient master table.

**Question:** Return visits with patient gender and site.

**Pandas**
```python
answer = visits.merge(
    patients[["patient_id", "gender", "site"]],
    on="patient_id",
    how="left"
)
```

**SQL**
```sql
SELECT v.*, p.gender, p.site AS patient_site
FROM visits v
LEFT JOIN patients p
ON v.patient_id = p.patient_id;
```

**Explanation:** Use a left join to keep all visits, even those with missing patients.

---

# Medium Questions

## 11. Calculate patient age

### What exactly you need to do

Calculate approximate current age from `birth_date` for each patient. Missing or invalid birth dates should produce a missing age.

**Pandas**
```python
patients["birth_date"] = pd.to_datetime(patients["birth_date"], errors="coerce")
today = pd.Timestamp.today()
answer = patients.assign(age=((today - patients["birth_date"]).dt.days // 365))
```

**SQL**
```sql
SELECT *,
       CAST((JULIANDAY('now') - JULIANDAY(birth_date)) / 365.25 AS INTEGER) AS age
FROM patients;
```

**Explanation:** Age is date arithmetic. Invalid birth dates will produce missing results.

---

## 12. Find future birth dates

### What exactly you need to do

Return complete patient rows where `birth_date` is later than today. These records violate a basic demographic validation rule.

**Pandas**
```python
patients["birth_date"] = pd.to_datetime(patients["birth_date"], errors="coerce")
answer = patients[patients["birth_date"] > pd.Timestamp.today()]
```

**SQL**
```sql
SELECT *
FROM patients
WHERE DATE(birth_date) > DATE('now');
```

**Explanation:** Future birth dates are invalid for existing patients.

---

## 13. Find duplicate patient IDs

### What exactly you need to do

Return every patient row whose `patient_id` appears more than once. Keep all copies so conflicting values across duplicate rows can be inspected.

**Pandas**
```python
answer = patients[patients.duplicated("patient_id", keep=False)]
```

**SQL**
```sql
SELECT *
FROM patients
WHERE patient_id IN (
    SELECT patient_id
    FROM patients
    GROUP BY patient_id
    HAVING COUNT(*) > 1
);
```

**Explanation:** `keep=False` returns all duplicated rows.

---

## 14. Find visits with unknown patients

### What exactly you need to do

Check referential integrity between `visits` and `patients`. Return visit rows whose patient ID has no matching patient-master record.

**Pandas**
```python
answer = visits[~visits["patient_id"].isin(patients["patient_id"])]
```

**SQL**
```sql
SELECT v.*
FROM visits v
LEFT JOIN patients p
ON v.patient_id = p.patient_id
WHERE p.patient_id IS NULL;
```

**Explanation:** This checks referential integrity between visits and patients.

---

## 15. Average valid HbA1c by site

### What exactly you need to do

Calculate mean HbA1c by patient site. Use only HbA1c rows with unit `%` and a non-missing result, then join to patients to obtain site.

**Question:** Use only HbA1c rows with unit `%` and non-null result.

**Pandas**
```python
valid_hba1c = labs[
    (labs["test_name"] == "HbA1c") &
    (labs["unit"] == "%") &
    (labs["result_value"].notna())
]

answer = (
    valid_hba1c.merge(patients[["patient_id", "site"]], on="patient_id", how="inner")
    .groupby("site")["result_value"]
    .mean()
    .reset_index(name="avg_hba1c")
)
```

**SQL**
```sql
SELECT p.site, AVG(l.result_value) AS avg_hba1c
FROM labs l
JOIN patients p
ON l.patient_id = p.patient_id
WHERE l.test_name = 'HbA1c'
  AND l.unit = '%'
  AND l.result_value IS NOT NULL
GROUP BY p.site;
```

**Explanation:** Filter by unit before calculating clinical metrics.

---

## 16. Latest HbA1c per patient

### What exactly you need to do

A patient can have multiple HbA1c tests. Return exactly one HbA1c row per patient: the row with the most recent parsed test date.

**Pandas**
```python
hba1c = labs[labs["test_name"] == "HbA1c"].copy()
hba1c["test_date"] = pd.to_datetime(hba1c["test_date"], errors="coerce")
answer = hba1c.sort_values("test_date", ascending=False).drop_duplicates("patient_id")
```

**SQL**
```sql
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY patient_id
               ORDER BY DATE(test_date) DESC
           ) AS rn
    FROM labs
    WHERE test_name = 'HbA1c'
)
SELECT *
FROM ranked
WHERE rn = 1;
```

**Explanation:** Sort first, then keep one row per patient. In SQL, use `ROW_NUMBER()`.

---

## 17. Return diabetic patients

### What exactly you need to do

Build a diabetes cohort using ICD10 code `E11`. Return patient-master records for IDs with at least one E11 diagnosis, without duplicate output rows.

**Question:** Diabetes is ICD10 code `E11`.

**Pandas**
```python
diabetic_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()
answer = patients[patients["patient_id"].isin(diabetic_ids)]
```

**SQL**
```sql
SELECT DISTINCT p.*
FROM patients p
JOIN diagnoses d
ON p.patient_id = d.patient_id
WHERE d.icd10 = 'E11';
```

**Explanation:** Use standardized diagnosis codes rather than free-text descriptions.

---

## 18. Patients with both diabetes and hypertension

### What exactly you need to do

Return patients who have both `E11` and `I10`. A patient with only one of these codes does not qualify.

**Question:** Diabetes = `E11`; hypertension = `I10`.

**Pandas**
```python
dx_counts = (
    diagnoses[diagnoses["icd10"].isin(["E11", "I10"])]
    .groupby("patient_id")["icd10"]
    .nunique()
)
patient_ids = dx_counts[dx_counts == 2].index
answer = patients[patients["patient_id"].isin(patient_ids)]
```

**SQL**
```sql
SELECT p.*
FROM patients p
JOIN (
    SELECT patient_id
    FROM diagnoses
    WHERE icd10 IN ('E11', 'I10')
    GROUP BY patient_id
    HAVING COUNT(DISTINCT icd10) = 2
) both_dx
ON p.patient_id = both_dx.patient_id;
```

**Explanation:** The patient must have both distinct codes, not just one of them.

---

## 19. Diabetic patients with latest HbA1c

### What exactly you need to do

Start with all E11 patients and attach each patient's latest HbA1c measured in `%`. Keep diabetic patients even if they have no qualifying HbA1c.

**Pandas**
```python
diabetic_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()

hba1c = labs[(labs["test_name"] == "HbA1c") & (labs["unit"] == "%")].copy()
hba1c["test_date"] = pd.to_datetime(hba1c["test_date"], errors="coerce")
latest_hba1c = hba1c.sort_values("test_date", ascending=False).drop_duplicates("patient_id")

answer = (
    patients[patients["patient_id"].isin(diabetic_ids)]
    .merge(latest_hba1c[["patient_id", "test_date", "result_value"]], on="patient_id", how="left")
)
```

**SQL**
```sql
WITH diabetic AS (
    SELECT DISTINCT patient_id
    FROM diagnoses
    WHERE icd10 = 'E11'
),
ranked_hba1c AS (
    SELECT patient_id, test_date, result_value,
           ROW_NUMBER() OVER (
               PARTITION BY patient_id
               ORDER BY DATE(test_date) DESC
           ) AS rn
    FROM labs
    WHERE test_name = 'HbA1c'
      AND unit = '%'
)
SELECT p.patient_id, p.gender, p.site, h.test_date, h.result_value
FROM diabetic d
JOIN patients p ON d.patient_id = p.patient_id
LEFT JOIN ranked_hba1c h ON d.patient_id = h.patient_id AND h.rn = 1;
```

**Explanation:** This combines cohort building with latest-lab logic.

---

## 20. Count active-medication patients by site

### What exactly you need to do

Filter medication records to `status = active`, join patients to obtain site, and count distinct treated patients per site.

**Pandas**
```python
active_meds = medications[medications["status"] == "active"]
answer = (
    active_meds.merge(patients[["patient_id", "site"]], on="patient_id", how="left")
    .groupby("site")["patient_id"]
    .nunique()
    .reset_index(name="active_med_patients")
)
```

**SQL**
```sql
SELECT p.site, COUNT(DISTINCT m.patient_id) AS active_med_patients
FROM medications m
LEFT JOIN patients p
ON m.patient_id = p.patient_id
WHERE m.status = 'active'
GROUP BY p.site;
```

**Explanation:** Filter to active medication records before grouping.

---

# Hard Questions

## 21. Visits after death

### What exactly you need to do

Join visits to patients and compare `visit_date` with `death_date`. Return only visits strictly after death; patients without a death date are not flagged.

**Pandas**
```python
p = patients.copy()
v = visits.copy()
p["death_date"] = pd.to_datetime(p["death_date"], errors="coerce")
v["visit_date"] = pd.to_datetime(v["visit_date"], errors="coerce")

merged = v.merge(p[["patient_id", "death_date"]], on="patient_id", how="left")
answer = merged[merged["death_date"].notna() & (merged["visit_date"] > merged["death_date"])]
```

**SQL**
```sql
SELECT v.*
FROM visits v
JOIN patients p
ON v.patient_id = p.patient_id
WHERE p.death_date IS NOT NULL
  AND DATE(v.visit_date) > DATE(p.death_date);
```

**Explanation:** Clinical events after death should be flagged.

---

## 22. Labs after death

### What exactly you need to do

Join labs to patients and compare `test_date` with `death_date`. Return lab rows recorded strictly after death.

**Pandas**
```python
p = patients.copy()
l = labs.copy()
p["death_date"] = pd.to_datetime(p["death_date"], errors="coerce")
l["test_date"] = pd.to_datetime(l["test_date"], errors="coerce")

merged = l.merge(p[["patient_id", "death_date"]], on="patient_id", how="left")
answer = merged[merged["death_date"].notna() & (merged["test_date"] > merged["death_date"])]
```

**SQL**
```sql
SELECT l.*
FROM labs l
JOIN patients p
ON l.patient_id = p.patient_id
WHERE p.death_date IS NOT NULL
  AND DATE(l.test_date) > DATE(p.death_date);
```

**Explanation:** This is another clinical timeline validation check.

---

## 23. Invalid HbA1c rows

### What exactly you need to do

Flag HbA1c rows if the value is negative, a percentage result is above 20, or the unit is not `%`. Return the suspicious rows.

**Question:** Find HbA1c rows where value is negative, value > 20 with unit `%`, or unit is not `%`.

**Pandas**
```python
answer = labs[
    (labs["test_name"] == "HbA1c") &
    (
        (labs["result_value"] < 0) |
        ((labs["unit"] == "%") & (labs["result_value"] > 20)) |
        (labs["unit"] != "%")
    )
]
```

**SQL**
```sql
SELECT *
FROM labs
WHERE test_name = 'HbA1c'
  AND (
      result_value < 0
      OR (unit = '%' AND result_value > 20)
      OR unit <> '%'
  );
```

**Explanation:** This validates both units and clinical ranges.

---

## 24. Missing patient references across tables

### What exactly you need to do

Across visits, labs, diagnoses, and medications, find patient IDs absent from the patients master table. Preserve the source-table name in the output.

**Question:** Find patient IDs in visits, labs, diagnoses, or medications that do not exist in patients.

**Pandas**
```python
patient_ids = set(patients["patient_id"])
answer = {
    "visits": sorted(set(visits["patient_id"]) - patient_ids),
    "labs": sorted(set(labs["patient_id"]) - patient_ids),
    "diagnoses": sorted(set(diagnoses["patient_id"]) - patient_ids),
    "medications": sorted(set(medications["patient_id"]) - patient_ids),
}
```

**SQL**
```sql
SELECT 'visits' AS source_table, v.patient_id
FROM visits v
LEFT JOIN patients p ON v.patient_id = p.patient_id
WHERE p.patient_id IS NULL
UNION ALL
SELECT 'labs', l.patient_id
FROM labs l
LEFT JOIN patients p ON l.patient_id = p.patient_id
WHERE p.patient_id IS NULL
UNION ALL
SELECT 'diagnoses', d.patient_id
FROM diagnoses d
LEFT JOIN patients p ON d.patient_id = p.patient_id
WHERE p.patient_id IS NULL
UNION ALL
SELECT 'medications', m.patient_id
FROM medications m
LEFT JOIN patients p ON m.patient_id = p.patient_id
WHERE p.patient_id IS NULL;
```

**Explanation:** This is a multi-table referential-integrity report.

---

## 25. Adult diabetes cohort with latest HbA1c

### What exactly you need to do

Build an adult diabetes cohort. Inclusion requires age ≥18, an E11 diagnosis, and at least one non-missing HbA1c in `%`. Return patient ID, age, site, latest HbA1c value, and latest HbA1c date.

**Question:** Include patients age >= 18 with E11 and at least one valid HbA1c in `%`. Return patient_id, age, site, latest HbA1c, latest HbA1c date.

**Pandas**
```python
p = patients.copy()
p["birth_date"] = pd.to_datetime(p["birth_date"], errors="coerce")
p["age"] = ((pd.Timestamp.today() - p["birth_date"]).dt.days // 365)
adult = p[p["age"] >= 18]

diabetic_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()

valid_hba1c = labs[(labs["test_name"] == "HbA1c") & (labs["unit"] == "%") & (labs["result_value"].notna())].copy()
valid_hba1c["test_date"] = pd.to_datetime(valid_hba1c["test_date"], errors="coerce")
latest_hba1c = valid_hba1c.sort_values("test_date", ascending=False).drop_duplicates("patient_id")

answer = (
    adult[adult["patient_id"].isin(diabetic_ids)]
    .merge(latest_hba1c[["patient_id", "test_date", "result_value"]], on="patient_id", how="inner")
    [["patient_id", "age", "site", "result_value", "test_date"]]
)
```

**SQL**
```sql
WITH adults AS (
    SELECT *, CAST((JULIANDAY('now') - JULIANDAY(birth_date)) / 365.25 AS INTEGER) AS age
    FROM patients
    WHERE birth_date IS NOT NULL
),
diabetic AS (
    SELECT DISTINCT patient_id
    FROM diagnoses
    WHERE icd10 = 'E11'
),
ranked_hba1c AS (
    SELECT patient_id, test_date, result_value,
           ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY DATE(test_date) DESC) AS rn
    FROM labs
    WHERE test_name = 'HbA1c'
      AND unit = '%'
      AND result_value IS NOT NULL
)
SELECT a.patient_id, a.age, a.site, h.result_value AS latest_hba1c, h.test_date AS latest_hba1c_date
FROM adults a
JOIN diabetic d ON a.patient_id = d.patient_id
JOIN ranked_hba1c h ON a.patient_id = h.patient_id AND h.rn = 1
WHERE a.age >= 18;
```

**Explanation:** This is a cohort-building query combining demographics, diagnoses, and labs.

---

## 26. Diabetes diagnosis but no active medication

### What exactly you need to do

Find E11 patients with no medication record whose status is `active`. This compares diagnosis evidence against active-treatment evidence.

**Pandas**
```python
diabetic_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()
active_med_ids = medications.loc[medications["status"] == "active", "patient_id"].drop_duplicates()
answer = diabetic_ids[~diabetic_ids.isin(active_med_ids)]
```

**SQL**
```sql
WITH diabetic AS (
    SELECT DISTINCT patient_id FROM diagnoses WHERE icd10 = 'E11'
),
active_med AS (
    SELECT DISTINCT patient_id FROM medications WHERE status = 'active'
)
SELECT d.patient_id
FROM diabetic d
LEFT JOIN active_med m ON d.patient_id = m.patient_id
WHERE m.patient_id IS NULL;
```

**Explanation:** This identifies diagnosed patients without active medication evidence.

---

## 27. Active diabetes medication without diabetes diagnosis

### What exactly you need to do

For this exercise, Metformin and Insulin are diabetes medications. Find IDs with an active record for either drug but no E11 diagnosis.

**Question:** Use Metformin and Insulin as diabetes medications.

**Pandas**
```python
diabetes_meds = ["Metformin", "Insulin"]
active_diabetes_med_ids = medications.loc[
    (medications["drug_name"].isin(diabetes_meds)) &
    (medications["status"] == "active"),
    "patient_id"
].drop_duplicates()

diabetic_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()
answer = active_diabetes_med_ids[~active_diabetes_med_ids.isin(diabetic_ids)]
```

**SQL**
```sql
WITH active_diabetes_meds AS (
    SELECT DISTINCT patient_id
    FROM medications
    WHERE drug_name IN ('Metformin', 'Insulin')
      AND status = 'active'
),
diabetic AS (
    SELECT DISTINCT patient_id
    FROM diagnoses
    WHERE icd10 = 'E11'
)
SELECT m.patient_id
FROM active_diabetes_meds m
LEFT JOIN diabetic d ON m.patient_id = d.patient_id
WHERE d.patient_id IS NULL;
```

**Explanation:** This may identify missing diagnosis coding or non-diabetes use cases.

---

## 28. Days from first diabetes diagnosis to first HbA1c

### What exactly you need to do

For each E11 patient, find the earliest E11 diagnosis and earliest valid HbA1c in `%`, then calculate days between them. Keep diagnosed patients even if HbA1c is missing.

**Pandas**
```python
dx = diagnoses[diagnoses["icd10"] == "E11"].copy()
dx["diagnosis_date"] = pd.to_datetime(dx["diagnosis_date"], errors="coerce")
first_dx = dx.sort_values("diagnosis_date").drop_duplicates("patient_id")[["patient_id", "diagnosis_date"]]

hba1c = labs[(labs["test_name"] == "HbA1c") & (labs["unit"] == "%")].copy()
hba1c["test_date"] = pd.to_datetime(hba1c["test_date"], errors="coerce")
first_hba1c = hba1c.sort_values("test_date").drop_duplicates("patient_id")[["patient_id", "test_date"]]

answer = first_dx.merge(first_hba1c, on="patient_id", how="left")
answer["days_to_first_hba1c"] = (answer["test_date"] - answer["diagnosis_date"]).dt.days
```

**SQL**
```sql
WITH first_dx AS (
    SELECT patient_id, MIN(DATE(diagnosis_date)) AS first_diagnosis_date
    FROM diagnoses
    WHERE icd10 = 'E11'
    GROUP BY patient_id
),
first_hba1c AS (
    SELECT patient_id, MIN(DATE(test_date)) AS first_hba1c_date
    FROM labs
    WHERE test_name = 'HbA1c'
      AND unit = '%'
    GROUP BY patient_id
)
SELECT d.patient_id,
       d.first_diagnosis_date,
       h.first_hba1c_date,
       JULIANDAY(h.first_hba1c_date) - JULIANDAY(d.first_diagnosis_date) AS days_to_first_hba1c
FROM first_dx d
LEFT JOIN first_hba1c h ON d.patient_id = h.patient_id;
```

**Explanation:** This measures time between two clinical events.

---

## 29. Data quality report

### What exactly you need to do

Create a two-column quality report: validation check name and affected-row count. Include all nine checks listed in the question.

**Question:** Create a summary table with counts for duplicate IDs, missing gender, missing birth date, future birth date, invalid HbA1c, visits after death, labs after death, unknown patients in visits, and unknown patients in labs.

**Pandas**
```python
p = patients.copy(); v = visits.copy(); l = labs.copy()
p["birth_date"] = pd.to_datetime(p["birth_date"], errors="coerce")
p["death_date"] = pd.to_datetime(p["death_date"], errors="coerce")
v["visit_date"] = pd.to_datetime(v["visit_date"], errors="coerce")
l["test_date"] = pd.to_datetime(l["test_date"], errors="coerce")
visits_death = v.merge(p[["patient_id", "death_date"]], on="patient_id", how="left")
labs_death = l.merge(p[["patient_id", "death_date"]], on="patient_id", how="left")

report = {
    "duplicate_patient_ids": p.duplicated("patient_id", keep=False).sum(),
    "missing_gender": p["gender"].isna().sum(),
    "missing_birth_date": p["birth_date"].isna().sum(),
    "future_birth_date": (p["birth_date"] > pd.Timestamp.today()).sum(),
    "invalid_hba1c_rows": ((l["test_name"] == "HbA1c") & ((l["result_value"] < 0) | ((l["unit"] == "%") & (l["result_value"] > 20)) | (l["unit"] != "%"))).sum(),
    "visits_after_death": (visits_death["death_date"].notna() & (visits_death["visit_date"] > visits_death["death_date"])).sum(),
    "labs_after_death": (labs_death["death_date"].notna() & (labs_death["test_date"] > labs_death["death_date"])).sum(),
    "unknown_patients_in_visits": (~v["patient_id"].isin(p["patient_id"])).sum(),
    "unknown_patients_in_labs": (~l["patient_id"].isin(p["patient_id"])).sum(),
}
answer = pd.DataFrame(report.items(), columns=["check", "count"])
```

**SQL**
```sql
SELECT 'duplicate_patient_ids' AS check_name, COUNT(*) AS issue_count
FROM patients
WHERE patient_id IN (SELECT patient_id FROM patients GROUP BY patient_id HAVING COUNT(*) > 1)
UNION ALL
SELECT 'missing_gender', COUNT(*) FROM patients WHERE gender IS NULL
UNION ALL
SELECT 'missing_birth_date', COUNT(*) FROM patients WHERE birth_date IS NULL
UNION ALL
SELECT 'future_birth_date', COUNT(*) FROM patients WHERE DATE(birth_date) > DATE('now')
UNION ALL
SELECT 'invalid_hba1c_rows', COUNT(*) FROM labs
WHERE test_name = 'HbA1c' AND (result_value < 0 OR (unit = '%' AND result_value > 20) OR unit <> '%')
UNION ALL
SELECT 'visits_after_death', COUNT(*) FROM visits v JOIN patients p ON v.patient_id = p.patient_id
WHERE p.death_date IS NOT NULL AND DATE(v.visit_date) > DATE(p.death_date)
UNION ALL
SELECT 'labs_after_death', COUNT(*) FROM labs l JOIN patients p ON l.patient_id = p.patient_id
WHERE p.death_date IS NOT NULL AND DATE(l.test_date) > DATE(p.death_date)
UNION ALL
SELECT 'unknown_patients_in_visits', COUNT(*) FROM visits v LEFT JOIN patients p ON v.patient_id = p.patient_id WHERE p.patient_id IS NULL
UNION ALL
SELECT 'unknown_patients_in_labs', COUNT(*) FROM labs l LEFT JOIN patients p ON l.patient_id = p.patient_id WHERE p.patient_id IS NULL;
```

**Explanation:** This summarizes several validation checks in a compact report.

---

## 30. Feasibility query

### What exactly you need to do

Build a customer feasibility cohort requiring all criteria simultaneously: age ≥18, E11 diagnosis, valid HbA1c in `%`, active Metformin or Insulin, and at least one 2025 visit. Report cohort size, IDs, average age, average latest HbA1c, and count by site.

**Question:** How many adult diabetic patients have E11, at least one valid HbA1c, at least one active diabetes medication, and at least one visit during 2025? Return total, IDs, average age, average latest HbA1c, and patients by site.

**Pandas**
```python
p = patients.copy()
p["birth_date"] = pd.to_datetime(p["birth_date"], errors="coerce")
p["age"] = ((pd.Timestamp.today() - p["birth_date"]).dt.days // 365)
adult = p[p["age"] >= 18]

diabetic_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()

valid_hba1c = labs[(labs["test_name"] == "HbA1c") & (labs["unit"] == "%") & (labs["result_value"].notna())].copy()
valid_hba1c["test_date"] = pd.to_datetime(valid_hba1c["test_date"], errors="coerce")
latest_hba1c = valid_hba1c.sort_values("test_date", ascending=False).drop_duplicates("patient_id")

active_diabetes_meds = medications.loc[
    (medications["drug_name"].isin(["Metformin", "Insulin"])) &
    (medications["status"] == "active"),
    "patient_id"
].drop_duplicates()

v = visits.copy()
v["visit_date"] = pd.to_datetime(v["visit_date"], errors="coerce")
visit_2025_ids = v.loc[v["visit_date"].dt.year == 2025, "patient_id"].drop_duplicates()

eligible = (
    adult[
        adult["patient_id"].isin(diabetic_ids) &
        adult["patient_id"].isin(active_diabetes_meds) &
        adult["patient_id"].isin(visit_2025_ids)
    ]
    .merge(latest_hba1c[["patient_id", "result_value"]], on="patient_id", how="inner")
)

answer = {
    "total_eligible": eligible["patient_id"].nunique(),
    "eligible_patient_ids": sorted(eligible["patient_id"].unique()),
    "average_age": eligible["age"].mean(),
    "average_latest_hba1c": eligible["result_value"].mean(),
    "eligible_by_site": eligible.groupby("site")["patient_id"].nunique()
}
```

**SQL**
```sql
WITH adults AS (
    SELECT *, CAST((JULIANDAY('now') - JULIANDAY(birth_date)) / 365.25 AS INTEGER) AS age
    FROM patients
    WHERE birth_date IS NOT NULL
),
diabetic AS (
    SELECT DISTINCT patient_id FROM diagnoses WHERE icd10 = 'E11'
),
ranked_hba1c AS (
    SELECT patient_id, result_value,
           ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY DATE(test_date) DESC) AS rn
    FROM labs
    WHERE test_name = 'HbA1c' AND unit = '%' AND result_value IS NOT NULL
),
active_diabetes_meds AS (
    SELECT DISTINCT patient_id
    FROM medications
    WHERE drug_name IN ('Metformin', 'Insulin') AND status = 'active'
),
visits_2025 AS (
    SELECT DISTINCT patient_id
    FROM visits
    WHERE STRFTIME('%Y', visit_date) = '2025'
),
eligible AS (
    SELECT a.patient_id, a.site, a.age, h.result_value AS latest_hba1c
    FROM adults a
    JOIN diabetic d ON a.patient_id = d.patient_id
    JOIN ranked_hba1c h ON a.patient_id = h.patient_id AND h.rn = 1
    JOIN active_diabetes_meds m ON a.patient_id = m.patient_id
    JOIN visits_2025 v ON a.patient_id = v.patient_id
    WHERE a.age >= 18
)
SELECT COUNT(DISTINCT patient_id) AS total_eligible,
       AVG(age) AS average_age,
       AVG(latest_hba1c) AS average_latest_hba1c
FROM eligible;
```

Patients by site:
```sql
SELECT site, COUNT(DISTINCT patient_id) AS eligible_patients
FROM eligible
GROUP BY site;
```

**Explanation:** This is a realistic feasibility query combining demographics, diagnoses, labs, medications, and visits.
