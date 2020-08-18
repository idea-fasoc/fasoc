database -open tb_dltdc_model -shm -event
##probe -create  tb_top -all -dynamic -memories -depth all -tasks -shm -database tb_top
probe -create  tb_dltdc_model -all -dynamic -memories -depth all -tasks -functions -shm -database tb_dltdc_model
run
#exit
