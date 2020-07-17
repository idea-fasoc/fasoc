database -open TB_PLL_CONTROLLER_TDC_COUNTER -shm -event
##probe -create  tb_top -all -dynamic -memories -depth all -tasks -shm -database tb_top
probe -create  TB_PLL_CONTROLLER_TDC_COUNTER -all -dynamic -memories -depth all -tasks -functions -shm -database TB_PLL_CONTROLLER_TDC_COUNTER
run
#exit
