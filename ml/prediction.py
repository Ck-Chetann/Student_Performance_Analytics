import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


# --------------------------------
# 1. Load Dataset
# --------------------------------

data = pd.read_csv("ml/training_data.csv")

print("===== TRAINING DATA =====")
print(data)


# --------------------------------
# 2. Input Features
# --------------------------------

X = data[[
    "attendance",
    "average_marks"
]]


# --------------------------------
# 3. Target
# --------------------------------

y = data["result"]


# --------------------------------
# 4. Split Dataset
# --------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# --------------------------------
# 5. Create Decision Tree
# --------------------------------

model = DecisionTreeClassifier(
    random_state=42,
    max_depth=4
)


# --------------------------------
# 6. Train Model
# --------------------------------

model.fit(X_train, y_train)


# --------------------------------
# 7. Test Model
# --------------------------------

y_pred = model.predict(X_test)


# --------------------------------
# 8. Accuracy
# --------------------------------

accuracy = accuracy_score(y_test, y_pred)

print("\n===== MODEL RESULT =====")

print(
    "Model Accuracy:",
    round(accuracy * 100, 2),
    "%"
)


# --------------------------------
# 9. New Student Prediction
# --------------------------------

attendance = 75
average_marks = 65

new_student = pd.DataFrame({
    "attendance": [attendance],
    "average_marks": [average_marks]
})


prediction = model.predict(new_student)


print("\n===== NEW STUDENT PREDICTION =====")

print("Attendance:", attendance)
print("Average Marks:", average_marks)


if prediction[0] == 1:
    print("Predicted Result: PASS")
else:
    print("Predicted Result: FAIL")