database -open tb_pll_top -shm -event
##probe -create  tb_top -all -dynamic -memories -depth all -tasks -shm -database tb_top
probe -create  tb_pll_top -all -dynamic -memories -depth all -tasks -functions -shm -database tb_pll_top
run
#exit
