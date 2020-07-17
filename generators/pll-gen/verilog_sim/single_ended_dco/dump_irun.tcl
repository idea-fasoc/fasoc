database -open tb_pll_controller_tdc_counter -shm -event
##probe -create  tb_top -all -dynamic -memories -depth all -tasks -shm -database tb_top
probe -create  tb_pll_controller_tdc_counter -all -dynamic -memories -depth all -tasks -functions -shm -database tb_pll_controller_tdc_counter
run
#exit
