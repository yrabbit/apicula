module top (
	input clk,
	output [`LEDS_NR-1:0] led
);

reg [25:0] ctr_q;
wire [25:0] ctr_d;
wire [`LEDS_NR-1:0]w_out;

// Sequential code (flip-flop)
always @(posedge clk)
	ctr_q <= ctr_d;

// Combinational code (boolean logic)
assign ctr_d = ctr_q + 1'b1;
assign w_out = ~ctr_q[25:25-(`LEDS_NR - 1)];
assign led = w_out;

endmodule
