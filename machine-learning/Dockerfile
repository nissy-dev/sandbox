From python:3.6

SHELL ["/bin/bash", "-c"]

# install dependecies
RUN pip install jupyter numpy scipy pandas scikit-learn matplotlib pep8
RUN pip install jupyterlab
RUN pip install pandas_profiling shap seaborn

# create directory for mounting local notebooks
RUN mkdir /opt/notebooks
