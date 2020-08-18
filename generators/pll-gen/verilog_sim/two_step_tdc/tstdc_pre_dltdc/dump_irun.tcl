database -open tb_tstdc_counter -shm -event
##probe -create  tb_top -all -dynamic -memories -depth all -tasks -shm -database tb_top
probe -create  tb_tstdc_counter -all -dynamic -memories -depth all -tasks -functions -shm -database tb_tstdc_counter
run
#exit
