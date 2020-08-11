
package pll_fsm_define;

 typedef enum logic [3:0] {PLL_INIT,			// 0
                          PLL_FREQ_TRACK,     		// 1 
                          PLL_PHASE_TRACK 		// 2
                          } pll_fsm;

endpackage // ip740adpll_pkg
  
