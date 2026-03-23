from Data_Processing.querries.querry_calibration import query_calibration_input
from Data_Processing.querries.querry_armington import query_armington
from Input.Dictionaries.hscodes import timba_commodity_list

qc = query_calibration_input()
qc.main_process()

# qa = query_armington(commodity_list=timba_commodity_list)
# qa.main_process()