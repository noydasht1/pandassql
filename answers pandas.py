import pandas as pd
from datetime import date

patients = pd.read_csv("patients.csv")
visits = pd.read_csv("visits.csv")
diagnoses = pd.read_csv("diagnoses.csv")
labs = pd.read_csv("labs.csv")
medications = pd.read_csv("medications.csv")
icd10_reference = pd.read_csv("icd10_reference.csv")
lab_reference = pd.read_csv("lab_reference.csv")
#1. Count unique patients by site
print(patients.groupby("site")["patient_id"].nunique())
#2. Return patients whose gender is F or Female.
print(patients[patients["gender"].isin(['F','Female'])])
#3. Find patients with missing gender
print(patients[patients["gender"].isnull()])
#4
patients["gender_stand"] = patients["gender"].map({"Female":"F", "Male":"M","F":"F", "M":"M"}).fillna("Unknown")
print(patients)
#5. Extract birth year
print(patients.dtypes)
patients['year'] = pd.DatetimeIndex(patients['birth_date']).year
print(patients['year'])
#6. Count visits by department
print(visits.groupby("department")['visit_id'].count())
#7 
print(labs[labs["test_name"] == "HbA1c"])
#8. Count diagnoses by ICD10 code
print(diagnoses.groupby('icd10').count())
#9. Count patients with medication records
print(medications["patient_id"].nunique())
#10. Join visits with patient data
print(pd.merge(visits,patients, on="patient_id"))
#11. Calculate patient aged
patients["age"] = pd.Timestamp.now().year - patients["year"]
print(patients)
#13
print(patients[patients.duplicated(subset='patient_id')])
#14
visit_nan_id = visits["patient_id"].isnull()
print(visits[visit_nan_id])
print(visits[~visits["patient_id"].isin(patients["patient_id"])])
#15
avg_HbA1c_site = pd.merge(patients, labs, on='patient_id')
print(avg_HbA1c_site[(avg_HbA1c_site["test_name"].isin(["HbA1c"])) & (avg_HbA1c_site["unit"] == "%")].groupby("site")["result_value"].mean())
#16
labs['test_date'] = pd.to_datetime(labs['test_date'], errors="coerce")
print(labs.groupby("patient_id")["test_date"].max())
#17
e11_ids = diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"].drop_duplicates()
print(e11_ids)
print(patients[patients["patient_id"].isin(e11_ids)])
#18
e11_i10 = diagnoses[diagnoses["icd10"].isin(["E11","I10"])].groupby("patient_id")["icd10"].nunique()
print(e11_i10)
answer = e11_i10[e11_i10 == 2].index
print(answer)
#19
e11 = diagnoses[diagnoses["icd10"] == "E11"]
print(e11)
hba1c = labs[(labs["test_name"] == 'HbA1c') & (labs["unit"] == "%")]
print(hba1c)
result = hba1c[hba1c["patient_id"].isin(e11["patient_id"])].groupby("patient_id")["test_date"].max()
print(pd.merge(result, patients, on = "patient_id"))
#20
active_med = medications[medications["status"] == "active"]
print(active_med)
print(pd.merge(active_med,patients, on = "patient_id").groupby("site")["patient_id"].nunique())
#21
merge = pd.merge(patients, visits, on = "patient_id")
print(merge[(~merge["death_date"].isnull()) & (merge["visit_date"] > merge["death_date"])])
#22
merge2 = pd.merge(patients, labs, on = "patient_id")
print(merge2[(~merge2["death_date"].isnull()) & (merge2["test_date"] > merge2["death_date"])])
#23 
HbA1c2 = labs[labs["test_name"] == "HbA1c"]
invalid = HbA1c2[(HbA1c2["result_value"] < 0 ) | (~HbA1c2["unit"].isin(["%"])) | (HbA1c2["result_value"] > 20)]
print(invalid)
#24

#25
patients_18 = patients[patients["age"] >= 18 ]
print(patients_18)
e11_p = set(diagnoses.loc[diagnoses["icd10"] == "E11", "patient_id"])
print(e11_p)
hba1c_non_missing = set(labs.loc[(labs["test_name"] == "HbA1c") & ((labs["result_value"] < 0) | (labs["unit"].isin(["%"])) | (labs["result_value"] <= 20)), "patient_id"].unique())
print(hba1c_non_missing)
overlap = ((list((e11_p)&(hba1c_non_missing))))
df = patients_18[patients_18["patient_id"].isin(overlap)]
print(df)
print(df.loc[:, ["patient_id", "age", "site", "result_value", "test_date"]])
