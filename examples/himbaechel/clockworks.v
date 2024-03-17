`default_nettype none

module Clockworks (
	input  wire CLK,
	input  wire RESET,
	output wire clk,
	output wire resetn
);
	parameter SLOW = 0;

	assign resetn = RESET ^ `INV_BTN;
	generate
		if (SLOW != 0) begin
			localparam slow_bits = SLOW;

			reg [SLOW:0] slow_CLK = 0;
			always @(posedge CLK) begin
				slow_CLK <= slow_CLK + 1;
			end
			assign clk = slow_CLK[slow_bits];
		end else begin
			assign clk = CLK;
		end
	endgenerate
endmodule

