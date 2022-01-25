///////////////////////////////////////////////////////////////////////////////////////////
//  Synchronized SPI slave code
//  Last Modified		: 10/03/18
//  Date Created   		: 10/03/18   
//  Revision 			: 1
//  Last Modified By	: 
//  First Author		: Ningxi Liu,
//  Description 		: This code was based on http://fpga4fun.com/SPI2.html
///////////////////////////////////////////////////////////////////////////////////////////
 
 `define DATA_WIDTH 16
module ble_top_spi_slave 
(
	//inputs from Pads
	input reset, // active-low
	input SS, 
	input SCLK,
	input MOSI,
	//outputs to Pads
	output MISO,
	// input data from block
	input [`DATA_WIDTH-1:0] IN_DATA_SPI1 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI2 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI3 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI4 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI5 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI6 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI7 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI8 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI9 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI10 , // v 051221
	input [`DATA_WIDTH-1:0] IN_DATA_SPI11 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI12 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI13 ,
	input [`DATA_WIDTH-1:0] IN_DATA_SPI14 , // ^
	input [`DATA_WIDTH-1:0] IN_DATA_SPI15 , // 052321 
	input [`DATA_WIDTH-1:0] IN_DATA_SPI16 , // 053121 
	input [`DATA_WIDTH-1:0] IN_DATA_SPI17 , // 053121 
	//SPI slave receiving data (data in)
	output reg [`DATA_WIDTH-1:0] REG_DATA1  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA2   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA3   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA4   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA5   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA6   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA7   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA8   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA9   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA10  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA11  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA12   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA13   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA14   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA15   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA16   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA17   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA18   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA19   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA20  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA21  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA22   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA23   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA24   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA25   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA26   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA27   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA28   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA29   , 
	output reg [`DATA_WIDTH-1:0] REG_DATA30  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA31  , 
	output reg [`DATA_WIDTH-1:0] REG_DATA32   , 
	//SPI slave receiving CONFIGs (data in)
	output reg [`DATA_WIDTH-1:0] REG_CONFIG1   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG2   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG3   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG4   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG5   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG6   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG7   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG8   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG9   , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG10  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG11  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG12  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG13  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG14  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG15  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG16  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG17  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG18  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG19  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG20  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG21  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG22  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG23  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG24  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG25  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG26  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG27  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG28  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG29  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG30  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG31  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG32  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG33  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG34  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG35  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG36  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG37  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG38  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG39  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG40  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG41  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG42  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG43  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG44  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG45  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG46  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG47  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG48  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG49  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG50  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG51  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG52  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG53  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG54  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG55  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG56  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG57  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG58  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG59  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG60  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG61  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG62  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG63  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG64  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG65  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG66  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG67  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG68  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG69  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG70  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG71  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG72  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG73  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG74  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG75  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG76  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG77  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG78  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG79  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG80  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG81  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG82  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG83  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG84  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG85  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG86  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG87  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG88  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG89  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG90  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG91  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG92  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG93  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG94  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG95  , 
	output reg [`DATA_WIDTH-1:0] REG_CONFIG96  ,
	output reg [`DATA_WIDTH-1:0] REG_CONFIG97  );

reg [4:0] full_word; 
reg done; 
reg [`DATA_WIDTH-1:0] command; 
reg [`DATA_WIDTH-1:0] data_out;
reg [3:0] rcv_bit_count, prev_rcv_bit_count;
reg NEXT_WRT_STATE;
reg WRT_STATE;

wire first_edge = (rcv_bit_count == 4'b0000) && (prev_rcv_bit_count == 4'b1111);
wire byte_end   = (rcv_bit_count == 4'b1111) && (prev_rcv_bit_count != 4'b1111);

wire SSEL_active = ~SS;  //SSEL is active low
wire SSEL_endmessage = SS;  //message stops at rising edge

wire MOSI_data = MOSI;	//and for MOSI

//state machine variables
reg [7:0] state;
reg [7:0] nextstate;  // 1015 update: bit width changed

//Control states
localparam RCV_CMD		= 8'b00000000;
//SPI slave receiving BLE data (data in)
localparam RCV_DATA1    = 8'b00000001; //Send index and FSM en and reset
localparam RCV_DATA2    = 8'b00000010;
localparam RCV_DATA3    = 8'b00000011;
localparam RCV_DATA4    = 8'b00000100;
localparam RCV_DATA5    = 8'b00000101;
localparam RCV_DATA6    = 8'b00000110;
localparam RCV_DATA7    = 8'b00000111;
localparam RCV_DATA8    = 8'b00001000;
localparam RCV_DATA9    = 8'b00001001;
localparam RCV_DATA10   = 8'b00001010;
localparam RCV_DATA11   = 8'b00001011;
localparam RCV_DATA12   = 8'b00001100;
localparam RCV_DATA13   = 8'b00001101;
localparam RCV_DATA14   = 8'b00001110;
localparam RCV_DATA15   = 8'b00001111;
localparam RCV_DATA16   = 8'b00010000;
localparam RCV_DATA17   = 8'b00010001;
localparam RCV_DATA18   = 8'b00010010;
localparam RCV_DATA19   = 8'b00010011;
localparam RCV_DATA20   = 8'b00010100;
localparam RCV_DATA21   = 8'b00010101;
localparam RCV_DATA22   = 8'b00010110;
localparam RCV_DATA23   = 8'b00010111;
localparam RCV_DATA24   = 8'b00011000;
localparam RCV_DATA25   = 8'b00011001;
localparam RCV_DATA26   = 8'b00011010;
localparam RCV_DATA27   = 8'b00011011;
localparam RCV_DATA28   = 8'b00011100;
localparam RCV_DATA29   = 8'b00011101;
localparam RCV_DATA30   = 8'b00011110;
localparam RCV_DATA31   = 8'b00011111;
localparam RCV_DATA32   = 8'b00100000;

// configs
localparam RCV_CONFIG1  = 8'b00100001;
localparam RCV_CONFIG2  = 8'b00100010;
localparam RCV_CONFIG3  = 8'b00100011;
localparam RCV_CONFIG4  = 8'b00100100;
localparam RCV_CONFIG5  = 8'b00100101;
localparam RCV_CONFIG6  = 8'b00100110;
localparam RCV_CONFIG7  = 8'b00100111;
localparam RCV_CONFIG8  = 8'b00101000;
localparam RCV_CONFIG9  = 8'b00101001;
localparam RCV_CONFIG10 = 8'b00101010;
localparam RCV_CONFIG11 = 8'b00101011;
localparam RCV_CONFIG12 = 8'b00101100;
localparam RCV_CONFIG13 = 8'b00101101;
localparam RCV_CONFIG14 = 8'b00101110;
localparam RCV_CONFIG15 = 8'b00101111;
localparam RCV_CONFIG16 = 8'b00110000;
localparam RCV_CONFIG17 = 8'b00110001;
localparam RCV_CONFIG18 = 8'b00110010;
localparam RCV_CONFIG19 = 8'b00110011;
localparam RCV_CONFIG20 = 8'b00110100;
localparam RCV_CONFIG21 = 8'b00110101;
localparam RCV_CONFIG22 = 8'b00110110;
localparam RCV_CONFIG23 = 8'b00110111;
localparam RCV_CONFIG24 = 8'b00111000;
localparam RCV_CONFIG25 = 8'b00111001;
localparam RCV_CONFIG26 = 8'b00111010;
localparam RCV_CONFIG27 = 8'b00111011;
localparam RCV_CONFIG28 = 8'b00111100;
localparam RCV_CONFIG29 = 8'b00111101;
localparam RCV_CONFIG30 = 8'b00111110;
localparam RCV_CONFIG31 = 8'b00111111;
localparam RCV_CONFIG32 = 8'b01000000;
localparam RCV_CONFIG33 = 8'b01000001;
localparam RCV_CONFIG34 = 8'b01000010;
localparam RCV_CONFIG35 = 8'b01000011;
localparam RCV_CONFIG36 = 8'b01000100;
localparam RCV_CONFIG37 = 8'b01000101;
localparam RCV_CONFIG38 = 8'b01000110;
localparam RCV_CONFIG39 = 8'b01000111;
localparam RCV_CONFIG40 = 8'b01001000;
localparam RCV_CONFIG41 = 8'b01001001;
localparam RCV_CONFIG42 = 8'b01001010;
localparam RCV_CONFIG43 = 8'b01001011;
localparam RCV_CONFIG44 = 8'b01001100;
localparam RCV_CONFIG45 = 8'b01001101;
localparam RCV_CONFIG46 = 8'b01001110;
localparam RCV_CONFIG47 = 8'b01001111;
localparam RCV_CONFIG48 = 8'b01010000;
localparam RCV_CONFIG49 = 8'b01010001;
localparam RCV_CONFIG50 = 8'b01010010;
localparam RCV_CONFIG51 = 8'b01010011;
localparam RCV_CONFIG52 = 8'b01010100;
localparam RCV_CONFIG53 = 8'b01010101;
localparam RCV_CONFIG54 = 8'b01010110;
localparam RCV_CONFIG55 = 8'b01010111;
localparam RCV_CONFIG56 = 8'b01011000;
localparam RCV_CONFIG57 = 8'b01011001;
localparam RCV_CONFIG58 = 8'b01011010;
localparam RCV_CONFIG59 = 8'b01011011;
localparam RCV_CONFIG60 = 8'b01011100;
localparam RCV_CONFIG61 = 8'b01011101;
localparam RCV_CONFIG62 = 8'b01011110;
localparam RCV_CONFIG63 = 8'b01011111;
localparam RCV_CONFIG64 = 8'b01100000;
localparam RCV_CONFIG65 = 8'b01100001;
localparam RCV_CONFIG66 = 8'b01100010;
localparam RCV_CONFIG67 = 8'b01100011;
localparam RCV_CONFIG68 = 8'b01100100;
localparam RCV_CONFIG69 = 8'b01100101;
localparam RCV_CONFIG70 = 8'b01100110;
localparam RCV_CONFIG71 = 8'b01100111;
localparam RCV_CONFIG72 = 8'b01101000;
localparam RCV_CONFIG73 = 8'b01101001;
localparam RCV_CONFIG74 = 8'b01101010;
localparam RCV_CONFIG75 = 8'b01101011;
localparam RCV_CONFIG76 = 8'b01101100;
localparam RCV_CONFIG77 = 8'b01101101;
localparam RCV_CONFIG78 = 8'b01101110;
localparam RCV_CONFIG79 = 8'b01101111;
localparam RCV_CONFIG80 = 8'b01110000;
localparam RCV_CONFIG81 = 8'b01110001;
localparam RCV_CONFIG82 = 8'b01110010;
localparam RCV_CONFIG83 = 8'b01110011;
localparam RCV_CONFIG84 = 8'b01110100;
localparam RCV_CONFIG85 = 8'b01110101;
localparam RCV_CONFIG86 = 8'b01110110;
localparam RCV_CONFIG87 = 8'b01110111;
localparam RCV_CONFIG88 = 8'b01111000;
localparam RCV_CONFIG89 = 8'b01111001;
localparam RCV_CONFIG90 = 8'b01111010;
localparam RCV_CONFIG91 = 8'b01111011;
localparam RCV_CONFIG92 = 8'b01111100;
localparam RCV_CONFIG93 = 8'b01111101;
localparam RCV_CONFIG94 = 8'b01111110;
localparam RCV_CONFIG95 = 8'b01111111;
localparam RCV_CONFIG96 = 8'b10000000;
localparam RCV_CONFIG97 = 8'b10000001;

// WRT DATAs                
localparam WRT_DATA1  = 8'b10000010;
localparam WRT_DATA2  = 8'b10000011;
localparam WRT_DATA3  = 8'b10000100;
localparam WRT_DATA4  = 8'b10000101;
localparam WRT_DATA5  = 8'b10000110;
localparam WRT_DATA6  = 8'b10000111;
localparam WRT_DATA7  = 8'b10001000;
localparam WRT_DATA8  = 8'b10001001;
localparam WRT_DATA9  = 8'b10001010;
localparam WRT_DATA10 = 8'b10001011;
localparam WRT_DATA11 = 8'b10001100; // v 051221
localparam WRT_DATA12 = 8'b10001101;
localparam WRT_DATA13 = 8'b10001110;
localparam WRT_DATA14 = 8'b10001111;
localparam WRT_DATA15 = 8'b10010000; // ^
localparam WRT_DATA16 = 8'b10010001; // 052321 
localparam WRT_DATA17 = 8'b10010010; // 052321 
localparam WRT_DATA18 = 8'b10010011; // 052321 

// default data pattern
localparam DATA = 512'h1169A18B13C40337AA0EB847C5079B440E8BB68E72D0E5A29AE3DE15DF5EC3D7C360D86537E59B135F8E89BED6AA;

// MODULATION LUT
localparam MOD_0_0 = 9'h0;			
localparam MOD_0_1 = 9'h0;			
localparam MOD_0_2 = 9'h0;		
localparam MOD_0_3 = 9'h0;			
localparam MOD_0_4 = 9'h0;			
localparam MOD_0_5 = 9'h0;			
localparam MOD_0_6 = 9'h0;			
localparam MOD_0_7 = 9'h0;
localparam MOD_1_0 = 9'd0;		// 001	
localparam MOD_1_1 = 9'd0;			
localparam MOD_1_2 = 9'd0;		
localparam MOD_1_3 = 9'd0;			
localparam MOD_1_4 = 9'd0;			
localparam MOD_1_5 = 9'd1;			
localparam MOD_1_6 = 9'd1;			
localparam MOD_1_7 = 9'd3;			
localparam MOD_2_0 = 9'd4;	//9;	// 010		
localparam MOD_2_1 = 9'd5;	//12;			
localparam MOD_2_2 = 9'd6;	//13;		
localparam MOD_2_3 = 9'd6;	//14;			
localparam MOD_2_4 = 9'd6;	//14;			
localparam MOD_2_5 = 9'd6;	//13;			
localparam MOD_2_6 = 9'd5;	//12;			
localparam MOD_2_7 = 9'd4;	//9;		
localparam MOD_3_0 = 9'd4;	//9;	// 011	
localparam MOD_3_1 = 9'd5;	//12;	
localparam MOD_3_2 = 9'd6;	//13;
localparam MOD_3_3 = 9'd6;	//14;	
localparam MOD_3_4 = 9'd6;	//15;	
localparam MOD_3_5 = 9'd6;	//15;	
localparam MOD_3_6 = 9'd6;	//15;	
localparam MOD_3_7 = 9'd6;	//15;
localparam MOD_4_0 = 9'd3;	//6;	// 100	
localparam MOD_4_1 = 9'd1;	//3;		
localparam MOD_4_2 = 9'd1;	//2;	
localparam MOD_4_3 = 9'd0;	//1;		
localparam MOD_4_4 = 9'd0;	//0;		
localparam MOD_4_5 = 9'd0;	//0;		
localparam MOD_4_6 = 9'd0;	//0;		
localparam MOD_4_7 = 9'd0;	//0;	
localparam MOD_5_0 = 9'd3;	//6;	// 101	
localparam MOD_5_1 = 9'd1;	//3;		
localparam MOD_5_2 = 9'd1;	//2;	
localparam MOD_5_3 = 9'd0;	//1;		
localparam MOD_5_4 = 9'd0;	//1;		
localparam MOD_5_5 = 9'd1;	//2;		
localparam MOD_5_6 = 9'd1;	//3;		
localparam MOD_5_7 = 9'd3;	//6;	
localparam MOD_6_0 = 9'd6;	//15;// 110	
localparam MOD_6_1 = 9'd6;	//15;	
localparam MOD_6_2 = 9'd6;	//15;
localparam MOD_6_3 = 9'd6;	//15;	
localparam MOD_6_4 = 9'd6;	//14;	
localparam MOD_6_5 = 9'd6;	//13;	
localparam MOD_6_6 = 9'd5;	//12;	
localparam MOD_6_7 = 9'd4;	//9;	
localparam MOD_7_0 = 9'd6;	//15;// 110	
localparam MOD_7_1 = 9'd6;	//15;	
localparam MOD_7_2 = 9'd6;	//15;
localparam MOD_7_3 = 9'd6;	//15;	
localparam MOD_7_4 = 9'd6;	//15;	
localparam MOD_7_5 = 9'd6;	//15;	
localparam MOD_7_6 = 9'd6;	//15;	
localparam MOD_7_7 = 9'd6;	//15;


always @ (*) begin
	nextstate = state;//default value
	if (~reset) begin
		nextstate = RCV_CMD;
	end 
	else begin
		case (state)
			RCV_CMD: begin
				if (SSEL_active) begin 
					if (byte_end) begin 
						if (command[7:0] == RCV_DATA1)  
							nextstate = RCV_DATA1;
						else if (command[7:0] == RCV_DATA2)  
							nextstate = RCV_DATA2; 
						else if (command[7:0] == RCV_DATA3)  
							nextstate = RCV_DATA3; 
						else if (command[7:0] == RCV_DATA4)  
							nextstate = RCV_DATA4; 
						else if (command[7:0] == RCV_DATA5)  
							nextstate = RCV_DATA5; 
						else if (command[7:0] == RCV_DATA6)  
							nextstate = RCV_DATA6; 
						else if (command[7:0] == RCV_DATA7)  
							nextstate = RCV_DATA7; 
						else if (command[7:0] == RCV_DATA8)  
							nextstate = RCV_DATA8; 
						else if (command[7:0] == RCV_DATA9)  
							nextstate = RCV_DATA9; 
						else if (command[7:0] == RCV_DATA10)  
							nextstate = RCV_DATA10; 
						else if (command[7:0] == RCV_DATA11)  
							nextstate = RCV_DATA11; 
						else if (command[7:0] == RCV_DATA12)  
							nextstate = RCV_DATA12; 
						else if (command[7:0] == RCV_DATA13)  
							nextstate = RCV_DATA13; 
						else if (command[7:0] == RCV_DATA14)  
							nextstate = RCV_DATA14; 
						else if (command[7:0] == RCV_DATA15)  
							nextstate = RCV_DATA15; 
						else if (command[7:0] == RCV_DATA16)  
							nextstate = RCV_DATA16; 
						else if (command[7:0] == RCV_DATA17)  
							nextstate = RCV_DATA17; 
						else if (command[7:0] == RCV_DATA18)  
							nextstate = RCV_DATA18; 
						else if (command[7:0] == RCV_DATA19)  
							nextstate = RCV_DATA19; 
						else if (command[7:0] == RCV_DATA20)  
							nextstate = RCV_DATA20; 
						else if (command[7:0] == RCV_DATA21)  
							nextstate = RCV_DATA21; 
						else if (command[7:0] == RCV_DATA22)  
							nextstate = RCV_DATA22; 
						else if (command[7:0] == RCV_DATA23)  
							nextstate = RCV_DATA23; 
						else if (command[7:0] == RCV_DATA24)  
							nextstate = RCV_DATA24; 
						else if (command[7:0] == RCV_DATA25)  
							nextstate = RCV_DATA25; 
						else if (command[7:0] == RCV_DATA26)  
							nextstate = RCV_DATA26; 
						else if (command[7:0] == RCV_DATA27)  
							nextstate = RCV_DATA27; 
						else if (command[7:0] == RCV_DATA28)  
							nextstate = RCV_DATA28; 
						else if (command[7:0] == RCV_DATA29)  
							nextstate = RCV_DATA29; 
						else if (command[7:0] == RCV_DATA30)  
							nextstate = RCV_DATA30; 
						else if (command[7:0] == RCV_DATA31)  
							nextstate = RCV_DATA31; 
						else if (command[7:0] == RCV_DATA32)  
							nextstate = RCV_DATA32; 
						else if (command[7:0] == RCV_CONFIG1)  
							nextstate = RCV_CONFIG1; 
						else if (command[7:0] == RCV_CONFIG2)  
							nextstate = RCV_CONFIG2; 
						else if (command[7:0] == RCV_CONFIG3)  
							nextstate = RCV_CONFIG3; 
						else if (command[7:0] == RCV_CONFIG4)  
							nextstate = RCV_CONFIG4; 
						else if (command[7:0] == RCV_CONFIG5)  
							nextstate = RCV_CONFIG5; 
						else if (command[7:0] == RCV_CONFIG6)  
							nextstate = RCV_CONFIG6; 
						else if (command[7:0] == RCV_CONFIG7)  
							nextstate = RCV_CONFIG7; 
						else if (command[7:0] == RCV_CONFIG8)  
							nextstate = RCV_CONFIG8; 
						else if (command[7:0] == RCV_CONFIG9)  
							nextstate = RCV_CONFIG9; 
						else if (command[7:0] == RCV_CONFIG10)  
							nextstate = RCV_CONFIG10; 
						else if (command[7:0] == RCV_CONFIG11)  
							nextstate = RCV_CONFIG11; 
						else if (command[7:0] == RCV_CONFIG12)  
							nextstate = RCV_CONFIG12; 
						else if (command[7:0] == RCV_CONFIG13)  
							nextstate = RCV_CONFIG13; 
						else if (command[7:0] == RCV_CONFIG14)  
							nextstate = RCV_CONFIG14; 
						else if (command[7:0] == RCV_CONFIG15)  
							nextstate = RCV_CONFIG15; 
						else if (command[7:0] == RCV_CONFIG16)  
							nextstate = RCV_CONFIG16; 
						else if (command[7:0] == RCV_CONFIG17)  
							nextstate = RCV_CONFIG17; 
						else if (command[7:0] == RCV_CONFIG18)  
							nextstate = RCV_CONFIG18; 
						else if (command[7:0] == RCV_CONFIG19)  
							nextstate = RCV_CONFIG19; 
						else if (command[7:0] == RCV_CONFIG20)  
							nextstate = RCV_CONFIG20; 
						else if (command[7:0] == RCV_CONFIG21)  
							nextstate = RCV_CONFIG21; 
						else if (command[7:0] == RCV_CONFIG22)  
							nextstate = RCV_CONFIG22; 
						else if (command[7:0] == RCV_CONFIG23)  
							nextstate = RCV_CONFIG23; 
						else if (command[7:0] == RCV_CONFIG24)  
							nextstate = RCV_CONFIG24; 
						else if (command[7:0] == RCV_CONFIG25)  
							nextstate = RCV_CONFIG25; 
						else if (command[7:0] == RCV_CONFIG26)  
							nextstate = RCV_CONFIG26; 
						else if (command[7:0] == RCV_CONFIG27)  
							nextstate = RCV_CONFIG27; 
						else if (command[7:0] == RCV_CONFIG28)  
							nextstate = RCV_CONFIG28; 
						else if (command[7:0] == RCV_CONFIG29)  
							nextstate = RCV_CONFIG29; 
						else if (command[7:0] == RCV_CONFIG30)  
							nextstate = RCV_CONFIG30; 
						else if (command[7:0] == RCV_CONFIG31)  
							nextstate = RCV_CONFIG31; 
						else if (command[7:0] == RCV_CONFIG32)  
							nextstate = RCV_CONFIG32; 
						else if (command[7:0] == RCV_CONFIG33)  
							nextstate = RCV_CONFIG33; 
						else if (command[7:0] == RCV_CONFIG34)  
							nextstate = RCV_CONFIG34; 
						else if (command[7:0] == RCV_CONFIG35)  
							nextstate = RCV_CONFIG35; 
						else if (command[7:0] == RCV_CONFIG36)  
							nextstate = RCV_CONFIG36; 
						else if (command[7:0] == RCV_CONFIG37)  
							nextstate = RCV_CONFIG37; 
						else if (command[7:0] == RCV_CONFIG38)  
							nextstate = RCV_CONFIG38; 
						else if (command[7:0] == RCV_CONFIG39)  
							nextstate = RCV_CONFIG39; 
						else if (command[7:0] == RCV_CONFIG40)  
							nextstate = RCV_CONFIG40; 
						else if (command[7:0] == RCV_CONFIG41)  
							nextstate = RCV_CONFIG41; 
						else if (command[7:0] == RCV_CONFIG42)  
							nextstate = RCV_CONFIG42; 
						else if (command[7:0] == RCV_CONFIG43)  
							nextstate = RCV_CONFIG43; 
						else if (command[7:0] == RCV_CONFIG44)  
							nextstate = RCV_CONFIG44; 
						else if (command[7:0] == RCV_CONFIG45)  
							nextstate = RCV_CONFIG45; 
						else if (command[7:0] == RCV_CONFIG46)  
							nextstate = RCV_CONFIG46; 
						else if (command[7:0] == RCV_CONFIG47)  
							nextstate = RCV_CONFIG47; 
						else if (command[7:0] == RCV_CONFIG48)  
							nextstate = RCV_CONFIG48; 
						else if (command[7:0] == RCV_CONFIG49)  
							nextstate = RCV_CONFIG49; 
						else if (command[7:0] == RCV_CONFIG50)  
							nextstate = RCV_CONFIG50; 
						else if (command[7:0] == RCV_CONFIG51)  
							nextstate = RCV_CONFIG51; 
						else if (command[7:0] == RCV_CONFIG52)  
							nextstate = RCV_CONFIG52; 
						else if (command[7:0] == RCV_CONFIG53)  
							nextstate = RCV_CONFIG53; 
						else if (command[7:0] == RCV_CONFIG54)  
							nextstate = RCV_CONFIG54; 
						else if (command[7:0] == RCV_CONFIG55)  
							nextstate = RCV_CONFIG55; 
						else if (command[7:0] == RCV_CONFIG56)  
							nextstate = RCV_CONFIG56; 
						else if (command[7:0] == RCV_CONFIG57)  
							nextstate = RCV_CONFIG57; 
						else if (command[7:0] == RCV_CONFIG58)  
							nextstate = RCV_CONFIG58; 
						else if (command[7:0] == RCV_CONFIG59)  
							nextstate = RCV_CONFIG59; 
						else if (command[7:0] == RCV_CONFIG60)  
							nextstate = RCV_CONFIG60; 
						else if (command[7:0] == RCV_CONFIG61)  
							nextstate = RCV_CONFIG61; 
						else if (command[7:0] == RCV_CONFIG62)  
							nextstate = RCV_CONFIG62; 
						else if (command[7:0] == RCV_CONFIG63)  
							nextstate = RCV_CONFIG63; 
						else if (command[7:0] == RCV_CONFIG64)  
							nextstate = RCV_CONFIG64; 
						else if (command[7:0] == RCV_CONFIG65)  
							nextstate = RCV_CONFIG65; 
						else if (command[7:0] == RCV_CONFIG66)  
							nextstate = RCV_CONFIG66; 
						else if (command[7:0] == RCV_CONFIG67)  
							nextstate = RCV_CONFIG67; 
						else if (command[7:0] == RCV_CONFIG68)  
							nextstate = RCV_CONFIG68; 
						else if (command[7:0] == RCV_CONFIG69)  
							nextstate = RCV_CONFIG69; 
						else if (command[7:0] == RCV_CONFIG70)  
							nextstate = RCV_CONFIG70; 
						else if (command[7:0] == RCV_CONFIG71)  
							nextstate = RCV_CONFIG71; 
						else if (command[7:0] == RCV_CONFIG72)  
							nextstate = RCV_CONFIG72; 
						else if (command[7:0] == RCV_CONFIG73)  
							nextstate = RCV_CONFIG73; 
						else if (command[7:0] == RCV_CONFIG74)  
							nextstate = RCV_CONFIG74; 
						else if (command[7:0] == RCV_CONFIG75)  
							nextstate = RCV_CONFIG75; 
						else if (command[7:0] == RCV_CONFIG76)  
							nextstate = RCV_CONFIG76; 
						else if (command[7:0] == RCV_CONFIG77)  
							nextstate = RCV_CONFIG77; 
						else if (command[7:0] == RCV_CONFIG78)  
							nextstate = RCV_CONFIG78; 
						else if (command[7:0] == RCV_CONFIG79)  
							nextstate = RCV_CONFIG79; 
						else if (command[7:0] == RCV_CONFIG80)  
							nextstate = RCV_CONFIG80; 
						else if (command[7:0] == RCV_CONFIG81)  
							nextstate = RCV_CONFIG81; 
						else if (command[7:0] == RCV_CONFIG82)  
							nextstate = RCV_CONFIG82; 
						else if (command[7:0] == RCV_CONFIG83)  
							nextstate = RCV_CONFIG83; 
						else if (command[7:0] == RCV_CONFIG84)  
							nextstate = RCV_CONFIG84; 
						else if (command[7:0] == RCV_CONFIG85)  
							nextstate = RCV_CONFIG85; 
						else if (command[7:0] == RCV_CONFIG86)  
							nextstate = RCV_CONFIG86; 
						else if (command[7:0] == RCV_CONFIG87)  
							nextstate = RCV_CONFIG87; 
						else if (command[7:0] == RCV_CONFIG88)  
							nextstate = RCV_CONFIG88; 
						else if (command[7:0] == RCV_CONFIG89)  
							nextstate = RCV_CONFIG89; 
						else if (command[7:0] == RCV_CONFIG90)  
							nextstate = RCV_CONFIG90; 
						else if (command[7:0] == RCV_CONFIG91)  
							nextstate = RCV_CONFIG91; 
						else if (command[7:0] == RCV_CONFIG92)  
							nextstate = RCV_CONFIG92; 
						else if (command[7:0] == RCV_CONFIG93)  
							nextstate = RCV_CONFIG93; 
						else if (command[7:0] == RCV_CONFIG94)  
							nextstate = RCV_CONFIG94; 
						else if (command[7:0] == RCV_CONFIG95)  
							nextstate = RCV_CONFIG95; 
						else if (command[7:0] == RCV_CONFIG96)  
							nextstate = RCV_CONFIG96; 
						else if (command[7:0] == RCV_CONFIG97)  
							nextstate = RCV_CONFIG97; 
						else if (command[7:0] == WRT_DATA1)  
							nextstate = WRT_DATA1; 
						else if (command[7:0] == WRT_DATA2)  
							nextstate = WRT_DATA2; 
						else if (command[7:0] == WRT_DATA2)  
							nextstate = WRT_DATA2; 
						else if (command[7:0] == WRT_DATA3)  
							nextstate = WRT_DATA3; 
						else if (command[7:0] == WRT_DATA4)  
							nextstate = WRT_DATA4; 
						else if (command[7:0] == WRT_DATA5)  
							nextstate = WRT_DATA5; 
						else if (command[7:0] == WRT_DATA6)  
							nextstate = WRT_DATA6; 
						else if (command[7:0] == WRT_DATA7)  
							nextstate = WRT_DATA7; 
						else if (command[7:0] == WRT_DATA8)  
							nextstate = WRT_DATA8; 
						else if (command[7:0] == WRT_DATA9)  
							nextstate = WRT_DATA9; 
						else if (command[7:0] == WRT_DATA10)  
							nextstate = WRT_DATA10; 
						else if (command[7:0] == WRT_DATA11)  
							nextstate = WRT_DATA11; 
						else if (command[7:0] == WRT_DATA12)  
							nextstate = WRT_DATA12; 
						else if (command[7:0] == WRT_DATA13)  
							nextstate = WRT_DATA13; 
						else if (command[7:0] == WRT_DATA14)  
							nextstate = WRT_DATA14; 
						else if (command[7:0] == WRT_DATA15)  
							nextstate = WRT_DATA15; 
						else if (command[7:0] == WRT_DATA16)  
							nextstate = WRT_DATA16; 
						else if (command[7:0] == WRT_DATA17)  
							nextstate = WRT_DATA17; 
						else if (command[7:0] == WRT_DATA18)  
							nextstate = WRT_DATA18; 
						else  
							nextstate = RCV_CMD; 
					end 
				end 
			end

			RCV_DATA1: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA2: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA3: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA4: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA5: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA6: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA7: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA8: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA9: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA10: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA11: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA12: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA13: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA14: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA15: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA16: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA17: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA18: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA19: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA20: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA21: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA22: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA23: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA24: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA25: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA26: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA27: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA28: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA29: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA30: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA31: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_DATA32: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG1: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG2: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG3: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG4: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG5: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG6: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG7: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG8: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG9: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG10: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG11: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG12: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG13: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG14: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG15: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG16: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG17: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG18: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG19: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG20: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG21: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG22: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG23: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG24: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG25: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG26: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG27: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG28: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG29: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG30: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG31: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG32: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG33: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG34: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG35: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG36: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG37: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG38: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG39: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG40: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG41: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG42: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG43: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG44: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG45: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG46: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG47: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG48: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			RCV_CONFIG49: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG50: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG51: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG52: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG53: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG54: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG55: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG56: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG57: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG58: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			RCV_CONFIG59: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end

			RCV_CONFIG60: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG61: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG62: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG63: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG64: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG65: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG66: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG67: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG68: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			RCV_CONFIG69: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end

			RCV_CONFIG70: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG71: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG72: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG73: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG74: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG75: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG76: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG77: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG78: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			RCV_CONFIG79: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end

			RCV_CONFIG80: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG81: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG82: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG83: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG84: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG85: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG86: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG87: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG88: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			RCV_CONFIG89: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end

			RCV_CONFIG90: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG91: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG92: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG93: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			RCV_CONFIG94: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			RCV_CONFIG95: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 

			RCV_CONFIG96: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			RCV_CONFIG97: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
				end 
			end 
			
			WRT_DATA1: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA2: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA3: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA4: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA5: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA6: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA7: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			
			WRT_DATA8: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 

			WRT_DATA9: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA10: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA11: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA12: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA13: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA14: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA15: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA16: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA17: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 
			WRT_DATA18: begin
					if (byte_end) begin 
						nextstate = RCV_CMD;
					end 
			end 

    default: begin
				if (SSEL_endmessage) begin 
					nextstate = RCV_CMD; 
				end 
    end
		endcase 
	end 
end

always @ (posedge SCLK or negedge reset) begin
	if (~reset) begin
		//state <= IDLE;
		state <= RCV_CMD;
	end
	else begin
		state <= nextstate;
	end
end

// shift register: read
always @(posedge SCLK or negedge reset) begin 
	if (~reset) begin 
		command <= 16'h0000;
		rcv_bit_count <= 4'b1111;
		prev_rcv_bit_count <= 4'b1111;
	end 
	else begin 
		prev_rcv_bit_count <= rcv_bit_count; 
		if (SSEL_active) begin 
			rcv_bit_count <= rcv_bit_count + 1'b1; 
			command <= {command [`DATA_WIDTH-2:0], MOSI_data};
		end
		else begin
		  	rcv_bit_count <= 4'b1111;
		  	prev_rcv_bit_count <= 4'b1111;
		  	command <= 16'h0000;
    		end
	end
end	

assign NEXT_WRT_STATE = (nextstate==WRT_DATA1) || (nextstate==WRT_DATA2) || (nextstate==WRT_DATA3) || (nextstate==WRT_DATA4) || (nextstate==WRT_DATA5) || (nextstate==WRT_DATA6) || (nextstate==WRT_DATA7) || (nextstate==WRT_DATA8) || (nextstate==WRT_DATA9)|| (nextstate==WRT_DATA10)|| (nextstate==WRT_DATA11)|| (nextstate==WRT_DATA12)|| (nextstate==WRT_DATA13)|| (nextstate==WRT_DATA14)|| (nextstate==WRT_DATA15) || (nextstate==WRT_DATA16) || (nextstate==WRT_DATA17) || (nextstate==WRT_DATA18);
assign WRT_STATE = (state==WRT_DATA1) || (state==WRT_DATA2) || (state==WRT_DATA3) || (state==WRT_DATA4) || (state==WRT_DATA5) || (state==WRT_DATA6) || (state==WRT_DATA7) || (state==WRT_DATA8) || (state==WRT_DATA9) || (state==WRT_DATA10)|| (state==WRT_DATA11) || (state==WRT_DATA12) || (state==WRT_DATA13) || (state==WRT_DATA14) || (state==WRT_DATA15) || (state==WRT_DATA16) || (state==WRT_DATA17) || (state==WRT_DATA18);
assign MISO = data_out[`DATA_WIDTH-1];

//Get done signal when read and write end (byte_end = 1)
always @(posedge SCLK or negedge reset) begin 
	if (~reset) begin 
	  	  data_out 	<= 0;
  end
  //else if(nextstate == WRT_DATA1) begin
  else if(NEXT_WRT_STATE) begin
    //if (state == WRT_DATA1) begin
    if (WRT_STATE) begin // shift register: write
			data_out <= {data_out [`DATA_WIDTH-2:0], 1'b0};
    end
    //else begin
    else if(nextstate==WRT_DATA1) begin
	  	  data_out 	<= REG_DATA1;
    end
    else if(nextstate==WRT_DATA2) begin
	  	  data_out 	<= IN_DATA_SPI1;
    end
    else if(nextstate==WRT_DATA3) begin
	  	  data_out 	<= IN_DATA_SPI2;
    end
    else if(nextstate==WRT_DATA4) begin
	  	  data_out 	<= IN_DATA_SPI3;
    end
    else if(nextstate==WRT_DATA5) begin
	  	  data_out 	<= IN_DATA_SPI4;
    end
    else if(nextstate==WRT_DATA6) begin
	  	  data_out 	<= IN_DATA_SPI5;
    end
    else if(nextstate==WRT_DATA7) begin
	  	  data_out 	<= IN_DATA_SPI6;
    end
    else if(nextstate==WRT_DATA8) begin
	  	  data_out 	<= IN_DATA_SPI7;
    end
    else if(nextstate==WRT_DATA9) begin
	  	  data_out 	<= IN_DATA_SPI8;
    end
    else if(nextstate==WRT_DATA10) begin
	  	  data_out 	<= IN_DATA_SPI9;
    end
    else if(nextstate==WRT_DATA11) begin
	  	  data_out 	<= IN_DATA_SPI10;
    end
    else if(nextstate==WRT_DATA12) begin
	  	  data_out 	<= IN_DATA_SPI11;
    end
    else if(nextstate==WRT_DATA13) begin
	  	  data_out 	<= IN_DATA_SPI12;
    end
    else if(nextstate==WRT_DATA14) begin
	  	  data_out 	<= IN_DATA_SPI13;
    end
    else if(nextstate==WRT_DATA15) begin
	  	  data_out 	<= IN_DATA_SPI14;
    end
    else if(nextstate==WRT_DATA16) begin
	  	  data_out 	<= IN_DATA_SPI15;
    end
    else if(nextstate==WRT_DATA17) begin
	  	  data_out 	<= IN_DATA_SPI16;
    end
    else if(nextstate==WRT_DATA18) begin
	  	  data_out 	<= IN_DATA_SPI17;
    end
  end
end

//Get done signal when read and write end (byte_end = 1)
always @(posedge SSEL_endmessage or negedge reset) begin 
	if (~reset) begin 
// default data 
    REG_DATA1 <= DATA[15:0];
    REG_DATA2 <= DATA[31:16];
    REG_DATA3 <= DATA[47:32];
    REG_DATA4 <= DATA[63:48];
    REG_DATA5 <= DATA[79:64];
    REG_DATA6 <= DATA[95:80];
    REG_DATA7 <= DATA[111:96];
    REG_DATA8 <= DATA[127:112];
    REG_DATA9 <= DATA[143:128];
    REG_DATA10 <= DATA[159:144];
    REG_DATA11 <= DATA[175:160];
    REG_DATA12 <= DATA[191:176];
    REG_DATA13 <= DATA[207:192];
    REG_DATA14 <= DATA[223:208];
    REG_DATA15 <= DATA[239:224];
    REG_DATA16 <= DATA[255:240];
    REG_DATA17 <= DATA[271:256];
    REG_DATA18 <= DATA[287:272];
    REG_DATA19 <= DATA[303:288];
    REG_DATA20 <= DATA[319:304];
    REG_DATA21 <= DATA[335:320];
    REG_DATA22 <= DATA[351:336];
    REG_DATA23 <= DATA[367:352];
    REG_DATA24 <= DATA[383:368];
    REG_DATA25 <= DATA[399:384];
    REG_DATA26 <= DATA[415:400];
    REG_DATA27 <= DATA[431:416];
    REG_DATA28 <= DATA[447:432];
    REG_DATA29 <= DATA[463:448];
    REG_DATA30 <= DATA[479:464];
    REG_DATA31 <= DATA[495:480];
    REG_DATA32 <= DATA[511:496];

// modulation lut
    REG_CONFIG1 <= {MOD_0_1[6:0],MOD_0_0};
    REG_CONFIG2 <= {MOD_0_3[4:0],MOD_0_2,MOD_0_1[8:7]};
    REG_CONFIG3 <= {MOD_0_5[2:0],MOD_0_4,MOD_0_3[8:5]};
    REG_CONFIG4 <= {MOD_0_7[0],MOD_0_6,MOD_0_5[8:3]};
    REG_CONFIG5 <= {MOD_1_0[7:0],MOD_0_7[8:1]};
    REG_CONFIG6 <= {MOD_1_2[5:0],MOD_1_1,MOD_1_0[8]};
    REG_CONFIG7 <= {MOD_1_4[3:0],MOD_1_3,MOD_1_2[8:6]};
    REG_CONFIG8 <= {MOD_1_6[1:0],MOD_1_5,MOD_1_4[8:4]};
    REG_CONFIG9 <= {MOD_1_7,MOD_1_6[8:2]};
    REG_CONFIG10 <= {MOD_2_1[6:0],MOD_2_0};
    REG_CONFIG11 <= {MOD_2_3[4:0],MOD_2_2,MOD_2_1[8:7]};
    REG_CONFIG12 <= {MOD_2_5[2:0],MOD_2_4,MOD_2_3[8:5]};
    REG_CONFIG13 <= {MOD_2_7[0],MOD_2_6,MOD_2_5[8:3]};
    REG_CONFIG14 <= {MOD_3_0[7:0],MOD_2_7[8:1]};
    REG_CONFIG15 <= {MOD_3_2[5:0],MOD_3_1,MOD_3_0[8]};
    REG_CONFIG16 <= {MOD_3_4[3:0],MOD_3_3,MOD_3_2[8:6]};
    REG_CONFIG17 <= {MOD_3_6[1:0],MOD_3_5,MOD_3_4[8:4]};
    REG_CONFIG18 <= {MOD_3_7,MOD_3_6[8:2]};
    REG_CONFIG19 <= {MOD_4_1[6:0],MOD_4_0};
    REG_CONFIG20 <= {MOD_4_3[4:0],MOD_4_2,MOD_4_1[8:7]};
    REG_CONFIG21 <= {MOD_4_5[2:0],MOD_4_4,MOD_4_3[8:5]};
    REG_CONFIG22 <= {MOD_4_7[0],MOD_4_6,MOD_4_5[8:3]};
    REG_CONFIG23 <= {MOD_5_0[7:0],MOD_4_7[8:1]};
    REG_CONFIG24 <= {MOD_5_2[5:0],MOD_5_1,MOD_5_0[8]};
    REG_CONFIG25 <= {MOD_5_4[3:0],MOD_5_3,MOD_5_2[8:6]};
    REG_CONFIG26 <= {MOD_5_6[1:0],MOD_5_5,MOD_5_4[8:4]};
    REG_CONFIG27 <= {MOD_5_7,MOD_5_6[8:2]};
    REG_CONFIG28 <= {MOD_6_1[6:0],MOD_6_0};
    REG_CONFIG29 <= {MOD_6_3[4:0],MOD_6_2,MOD_6_1[8:7]};
    REG_CONFIG30 <= {MOD_6_5[2:0],MOD_6_4,MOD_6_3[8:5]};
    REG_CONFIG31 <= {MOD_6_7[0],MOD_6_6,MOD_6_5[8:3]};
    REG_CONFIG32 <= {MOD_7_0[7:0],MOD_6_7[8:1]};
    REG_CONFIG33 <= {MOD_7_2[5:0],MOD_7_1,MOD_7_0[8]};
    REG_CONFIG34 <= {MOD_7_4[3:0],MOD_7_3,MOD_7_2[8:6]};
    REG_CONFIG35 <= {MOD_7_6[1:0],MOD_7_5,MOD_7_4[8:4]};
    REG_CONFIG36 <= {MOD_7_7,MOD_7_6[8:2]};

// ble/pll configs
  // reg 37 - default values: {0000_0000_0000_0011} 
    REG_CONFIG37   <= {16'b0000_0000_0000_0011}; 
  // reg 38 - def: {1110, 001, 0000_00, 011} 
    REG_CONFIG38   <= {4'b1110, 3'b001, 6'b0000_00, 3'b011};
  // reg 39 - def: {0110_1101_1011_01, 01}
  // reg 39 - def: {1101_1011_0111_00, 01} - version 2 (0602)
    REG_CONFIG39   <= {14'b1101_1011_0111_00, 2'b01};	
  // reg 40 - def: {000_110000_110000, 1}
  // reg 40 - def: {000_110000_100111, 0} - version 2 (0602)
    REG_CONFIG40   <= {15'b000_110000_100111, 1'b0};
  // reg 41 - def: {1, 110000_110000_110}
  // reg 41 - def: {1, 110000_110000_110} - version 2 (0602)
    REG_CONFIG41   <= {1'b1, 15'b110000_110000_110};	
  // reg 42 - def: {100, 01010, 111111, 01}
  // reg 42 - def: {100, 01010, 000000, 10} - version 2 (0602)
    REG_CONFIG42   <= {3'b100, 5'b01010, 6'b000000, 2'b10};	
  // reg 43 - def: {00,101000, 000000, 10}
    REG_CONFIG43   <= {2'b00,6'b101000, 6'b000000, 2'b10}; // 0513 bookmark	
  // reg 44 - def: {0_0000_1010, 010_0000} - version 0
  // reg 44 - def: {0_0010_0000, 001_0100} - version 1
    REG_CONFIG44   <= {9'b0_0010_0000, 7'b001_0100};	
  // reg 45 - def: {7'b0000_000, 9'b0_1000_0000} - version 0 
  // reg 45 - def: {7'b0000_000, 9'b0_0001_0100} - version 1 
    REG_CONFIG45   <= {7'b0000_000, 9'b0_0001_0100};	
  // reg 46(053121) - def: {4'b1000,7'b0000_001,1'b1,3'b000,1'b0}
    REG_CONFIG46   <= {4'b1000,7'b0000_001,1'b1,3'b000,1'b0}; // 053121	
  // reg 47(060221) - def: {16'b0} (0602)
    REG_CONFIG47   <= 16'b0000_0000_0000_0000;	
  // reg 48 - def(1): {8'b0, 8'b1111_1111}
  // reg 48 - def(2): {8'b0001_1110, 8'b1111_1111}
  // reg 48 - def(3): {8'b0001_1110, 8'b0100_0000}
    REG_CONFIG48   <= {8'b0001_1110, 8'b0100_0000};
  // reg 49 - def(1): 16'b0110_0101__0011_0011
  // reg 49 - def(2): {8'b1000_0011, 8'b0101_0001} 
    REG_CONFIG49   <= {8'b1000_0011, 8'b0101_0001};	
  // reg 50 - def(1):  16'b1100_1010__1001_1000
  // reg 50 - def(2): {8'b1110_1000, 8'b1011_0110}
    REG_CONFIG50   <=  {8'b1110_1000, 8'b1011_0110};	
    REG_CONFIG51   <= 16'b0000_0111__0000_0000;	
    REG_CONFIG52   <= 16'b0001_0111__0000_1111;	
    REG_CONFIG53   <= {8'b0001_1111, 8'b0001_1111};	
    REG_CONFIG54   <= 0; // v DLTDC_LUT_USER 	
    REG_CONFIG55   <= 0;	
    REG_CONFIG56   <= 0;	
    REG_CONFIG57   <= 0;	
    REG_CONFIG58   <= 0;
    REG_CONFIG59   <= 0;	
    REG_CONFIG60   <= 0;	
    REG_CONFIG61   <= 0;	
    REG_CONFIG62   <= 0;	
    REG_CONFIG63   <= 0;	
    REG_CONFIG64   <= 0;	
    REG_CONFIG65   <= 0;	
    REG_CONFIG66   <= 0;	
    REG_CONFIG67   <= 0;	
    REG_CONFIG68   <= 0;
    REG_CONFIG69   <= 0;	
    REG_CONFIG70   <= 0;	
    REG_CONFIG71   <= 0;	
    REG_CONFIG72   <= 0;	
    REG_CONFIG73   <= 0;	
    REG_CONFIG74   <= 0;	
    REG_CONFIG75   <= 0;	
    REG_CONFIG76   <= 0;	
    REG_CONFIG77   <= 0;	
    REG_CONFIG78   <= 0; // ^ DLTDC_LUT_USER 
  // reg 79 - def: {7'b0000_000, 9'b0_1100_1000} - version 1 
    REG_CONFIG79   <= {7'b0000_000, 9'b0_1100_1000}  ;	
    REG_CONFIG80   <= {7'b011_1100,9'b0};	
    REG_CONFIG81   <= {7'b011_1100  ,9'b0_0100_0000};	
  // reg 82 - def(1): kp_real=2.2: {4'b1100, 12'b0000_1000_1100}
  // reg 82 - def(2): kp_real=6.2: {4'b1100, 12'b0100_0000_1100}
    //REG_CONFIG82   <= {4'b1100, 12'b0000_1000_1100};	
    REG_CONFIG82   <= {4'b1100, 12'b0010_0000_1100};	
  // reg 83 - def(1): {8'b0, 8'b0000_1000}
  // reg 83 - def(2): {8'b0, 8'b0100_0000}
  // reg 83 - def(3): ki_real
    //REG_CONFIG83   <= {8'b0, 8'b0100_0000};
    REG_CONFIG83   <= {8'b0, 8'b0010_0000};
  // reg 84 - def(1): {11'b001_0100_0000,1'b0,1'b1,1'b0,1'b1,1'b0} 
  // reg 84 - def(2): {11'b001_0100_0000,1'b0,1'b1,1'b0,1'b1,1'b1} 
    REG_CONFIG84   <= {11'b001_0100_0000,1'b0,1'b1,1'b0,1'b1,1'b1} ;	
    REG_CONFIG85   <= 16'b0000_0000_1111_0000 ;	
    //REG_CONFIG86   <= {8'b0000_0000, 8'b0001_0000}; // 0930	
    REG_CONFIG86   <= {8'b0000_0000, 8'b1111_0000}; // 0930	
    REG_CONFIG87   <= {4'b1010, 12'b1000_0000_0000};	
    REG_CONFIG88   <= {4'b0, 8'b0001_0000, 4'b0101}; // 0930
    REG_CONFIG89   <= 16'b1111_1111_1111_1111;	
    REG_CONFIG90   <= 16'b1111_1111_1111_1111;	
    REG_CONFIG91   <= {2'b0, 7'b010_0011, 1'b0, 6'b00_0110};	
    REG_CONFIG92   <= {1'b1,9'b0_1000_1100,1'b0,5'b011_11};	
    REG_CONFIG93   <= {4'b0, 1'b1, 11'b0} ;	
    REG_CONFIG94   <= {2'b11, 9'b1_0010_1100, 5'b0};	
    REG_CONFIG95   <= {10'b11_1111_1111,1'b0,1'b1,1'b0,1'b1,1'b0,1'b0};	
    REG_CONFIG96   <= {2'b0, 10'b00_0000_0100, 4'b1111};	
    REG_CONFIG97   <= {7'b0, 9'b1_1100_0111} ;
	
	done 		<= 0; 
	full_word 	<= 0;
	end 

	else begin 
		//SPI slave receiving 
		if (state == RCV_DATA1 && byte_end) begin 
			REG_DATA1 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA2 && byte_end) begin 
			REG_DATA2 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA3 && byte_end) begin 
			REG_DATA3 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA4 && byte_end) begin 
			REG_DATA4 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA5 && byte_end) begin 
			REG_DATA5 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA6 && byte_end) begin 
			REG_DATA6 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA7 && byte_end) begin 
			REG_DATA7 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA8 && byte_end) begin 
			REG_DATA8 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA9 && byte_end) begin 
			REG_DATA9 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA10 && byte_end) begin 
			REG_DATA10 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA11 && byte_end) begin 
			REG_DATA11 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA12 && byte_end) begin 
			REG_DATA12 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA13 && byte_end) begin 
			REG_DATA13 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA14 && byte_end) begin 
			REG_DATA14 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA15 && byte_end) begin 
			REG_DATA15 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA16 && byte_end) begin 
			REG_DATA16 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA17 && byte_end) begin 
			REG_DATA17 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA18 && byte_end) begin 
			REG_DATA18 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA19 && byte_end) begin 
			REG_DATA19 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA20 && byte_end) begin 
			REG_DATA20 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA21 && byte_end) begin 
			REG_DATA21 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA22 && byte_end) begin 
			REG_DATA22 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA23 && byte_end) begin 
			REG_DATA23 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA24 && byte_end) begin 
			REG_DATA24 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA25 && byte_end) begin 
			REG_DATA25 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA26 && byte_end) begin 
			REG_DATA26 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA27 && byte_end) begin 
			REG_DATA27 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA28 && byte_end) begin 
			REG_DATA28 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA29 && byte_end) begin 
			REG_DATA29 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA30 && byte_end) begin 
			REG_DATA30 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA31 && byte_end) begin 
			REG_DATA31 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_DATA32 && byte_end) begin 
			REG_DATA32 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG1 && byte_end) begin 
			REG_CONFIG1 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG2 && byte_end) begin 
			REG_CONFIG2 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG3 && byte_end) begin 
			REG_CONFIG3 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG4 && byte_end) begin 
			REG_CONFIG4 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG5 && byte_end) begin 
			REG_CONFIG5 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG6 && byte_end) begin 
			REG_CONFIG6 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG7 && byte_end) begin 
			REG_CONFIG7 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG8 && byte_end) begin 
			REG_CONFIG8 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG9 && byte_end) begin 
			REG_CONFIG9 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG10 && byte_end) begin 
			REG_CONFIG10 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG11 && byte_end) begin 
			REG_CONFIG11 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG12 && byte_end) begin 
			REG_CONFIG12 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG13 && byte_end) begin 
			REG_CONFIG13 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG14 && byte_end) begin 
			REG_CONFIG14 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG15 && byte_end) begin 
			REG_CONFIG15 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG16 && byte_end) begin 
			REG_CONFIG16 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG17 && byte_end) begin 
			REG_CONFIG17 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG18 && byte_end) begin 
			REG_CONFIG18 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG19 && byte_end) begin 
			REG_CONFIG19 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG20 && byte_end) begin 
			REG_CONFIG20 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG21 && byte_end) begin 
			REG_CONFIG21 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG22 && byte_end) begin 
			REG_CONFIG22 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG23 && byte_end) begin 
			REG_CONFIG23 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG24 && byte_end) begin 
			REG_CONFIG24 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG25 && byte_end) begin 
			REG_CONFIG25 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG26 && byte_end) begin 
			REG_CONFIG26 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG27 && byte_end) begin 
			REG_CONFIG27 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG28 && byte_end) begin 
			REG_CONFIG28 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG29 && byte_end) begin 
			REG_CONFIG29 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG30 && byte_end) begin 
			REG_CONFIG30 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG31 && byte_end) begin 
			REG_CONFIG31 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG32 && byte_end) begin 
			REG_CONFIG32 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG33 && byte_end) begin 
			REG_CONFIG33 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG34 && byte_end) begin 
			REG_CONFIG34 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG35 && byte_end) begin 
			REG_CONFIG35 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG36 && byte_end) begin 
			REG_CONFIG36 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG37 && byte_end) begin 
			REG_CONFIG37 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG38 && byte_end) begin 
			REG_CONFIG38 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG39 && byte_end) begin 
			REG_CONFIG39 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG40 && byte_end) begin 
			REG_CONFIG40 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG41 && byte_end) begin 
			REG_CONFIG41 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG42 && byte_end) begin 
			REG_CONFIG42 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG43 && byte_end) begin 
			REG_CONFIG43 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG44 && byte_end) begin 
			REG_CONFIG44 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG45 && byte_end) begin 
			REG_CONFIG45 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG46 && byte_end) begin 
			REG_CONFIG46 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG47 && byte_end) begin 
			REG_CONFIG47 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG48 && byte_end) begin 
			REG_CONFIG48 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG49 && byte_end) begin 
			REG_CONFIG49 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG50 && byte_end) begin 
			REG_CONFIG50 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG51 && byte_end) begin 
			REG_CONFIG51 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG52 && byte_end) begin 
			REG_CONFIG52 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG53 && byte_end) begin 
			REG_CONFIG53 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG54 && byte_end) begin 
			REG_CONFIG54 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG55 && byte_end) begin 
			REG_CONFIG55 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG56 && byte_end) begin 
			REG_CONFIG56 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG57 && byte_end) begin 
			REG_CONFIG57 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG58 && byte_end) begin 
			REG_CONFIG58 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG59 && byte_end) begin 
			REG_CONFIG59 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG60 && byte_end) begin 
			REG_CONFIG60 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG61 && byte_end) begin 
			REG_CONFIG61 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG62 && byte_end) begin 
			REG_CONFIG62 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG63 && byte_end) begin 
			REG_CONFIG63 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG64 && byte_end) begin 
			REG_CONFIG64 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG65 && byte_end) begin 
			REG_CONFIG65 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG66 && byte_end) begin 
			REG_CONFIG66 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG67 && byte_end) begin 
			REG_CONFIG67 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG68 && byte_end) begin 
			REG_CONFIG68 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG69 && byte_end) begin 
			REG_CONFIG69 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG70 && byte_end) begin 
			REG_CONFIG70 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG71 && byte_end) begin 
			REG_CONFIG71 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG72 && byte_end) begin 
			REG_CONFIG72 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG73 && byte_end) begin 
			REG_CONFIG73 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG74 && byte_end) begin 
			REG_CONFIG74 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG75 && byte_end) begin 
			REG_CONFIG75 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG76 && byte_end) begin 
			REG_CONFIG76 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG77 && byte_end) begin 
			REG_CONFIG77 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG78 && byte_end) begin 
			REG_CONFIG78 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG79 && byte_end) begin 
			REG_CONFIG79 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG80 && byte_end) begin 
			REG_CONFIG80 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG81 && byte_end) begin 
			REG_CONFIG81 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG82 && byte_end) begin 
			REG_CONFIG82 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG83 && byte_end) begin 
			REG_CONFIG83 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG84 && byte_end) begin 
			REG_CONFIG84 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG85 && byte_end) begin 
			REG_CONFIG85 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG86 && byte_end) begin 
			REG_CONFIG86 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG87 && byte_end) begin 
			REG_CONFIG87 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG88 && byte_end) begin 
			REG_CONFIG88 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG89 && byte_end) begin 
			REG_CONFIG89 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG90 && byte_end) begin 
			REG_CONFIG90 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG91 && byte_end) begin 
			REG_CONFIG91 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG92 && byte_end) begin 
			REG_CONFIG92 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG93 && byte_end) begin 
			REG_CONFIG93 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG94 && byte_end) begin 
			REG_CONFIG94 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG95 && byte_end) begin 
			REG_CONFIG95 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG96 && byte_end) begin 
			REG_CONFIG96 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end
		else if (state == RCV_CONFIG97 && byte_end) begin 
			REG_CONFIG97 <= command;
			done <= 1'b1;
			full_word <= 5'b000;
		end

	end
end	

endmodule
