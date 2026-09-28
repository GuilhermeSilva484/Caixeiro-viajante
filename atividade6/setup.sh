# Install Python API for AMPL:
python -m pip install amplpy --upgrade

# Install solver modules:
python -m amplpy.modules install highs gurobi xpress cplex

# Activate your license (e.g., free ampl.com/ce or ampl.com/courses licenses):
python -m amplpy.modules activate 21cd162c-aa90-497a-9fc6-f9ca9906d9ea