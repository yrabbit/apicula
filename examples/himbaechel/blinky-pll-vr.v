(* top *)
module top (
	input key,
	input clk,
	output [`LEDS_NR-1:0] led
);

wire clk_w;

PLLVR pllvr_inst (
    .CLKOUT(clk_w),
	.CLKIN(clk),
	.CLKFB(GND),
	.RESET(GND),
	.RESET_P(GND),
	.FBDSEL({GND,GND,GND,GND,GND,GND}),
	.IDSEL({GND,GND,GND,GND,GND,GND}),
	.ODSEL({GND,GND,GND,GND,GND,GND}),
	.DUTYDA({GND,GND,GND,GND}),
	.PSDA({GND,GND,GND,GND}),
	.FDLY({GND,GND,GND,GND}),
	.VREN(gw_vcc)
);


reg [25:0] ctr_q;
wire [25:0] ctr_d;

// Sequential code (flip-flop)
always @(posedge clk_w) begin
	if (key) begin
		ctr_q <= ctr_d;
	end
end

// Combinational code (boolean logic)
assign ctr_d = ctr_q + 1'b1;
assign led = ctr_q[25:25-(`LEDS_NR - 1)];

endmodule
