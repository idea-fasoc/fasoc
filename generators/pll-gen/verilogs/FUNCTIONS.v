// Functions

	function automatic integer func_clog2;
//	task automatic func_clog2;
		// calculate how many bits are needed to express the input value N

		input integer func_clog2_N;
		integer func_clog2_ii;

		// keep going until 2^ii is larger than N
		for (func_clog2_ii=0;2**func_clog2_ii<func_clog2_N;func_clog2_ii=func_clog2_ii+1)
			func_clog2 = func_clog2_ii+1;

	endfunction
	//endtask;

	function automatic integer func_MAX;
		// return the max of A or B
		
		input integer func_MAX_A;
		input integer func_MAX_B;
		
		if (func_MAX_A >= func_MAX_B)
			func_MAX = func_MAX_A;
		else
			func_MAX = func_MAX_B;

	endfunction


	function automatic integer func_MIN;
		// return the max of A or B
		
		input integer func_MIN_A;
		input integer func_MIN_B;
		
		if (func_MIN_A >= func_MIN_B)
			func_MIN = func_MIN_A;
		else
			func_MIN = func_MIN_B;

	endfunction

