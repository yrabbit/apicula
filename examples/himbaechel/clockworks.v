 /*
 * Copyright (c) 2020, Bruno Levy
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
`default_nettype none

module Clockworks (
	input  wire CLK,
	input  wire RESET,
	output wire clk,
	output wire resetn,
	output lock
);
	parameter SLOW = 0;

	assign resetn = RESET ^ `INV_BTN;
	generate
		if (SLOW != 0) begin
		 rPLL #(
            .FCLKIN("50.0"),
            .IDIV_SEL(12), // -> PFD = 3.8461538461538463 MHz (range: 3-400 MHz)
            .FBDIV_SEL(6), // -> CLKOUT = 26.923076923076923 MHz (range: 400-600 MHz)
            .ODIV_SEL(16) // -> VCO = 430.7692307692308 MHz (range: 600-1200 MHz)
        ) pll (.CLKOUTP(), .CLKOUTD(), .CLKOUTD3(), .RESET(1'b0), .RESET_P(1'b0), .CLKFB(1'b0), .FBDSEL(6'b0), .IDSEL(6'b0), .ODSEL(6'b0), .PSDA(4'b0), .DUTYDA(4'b0), .FDLY(4'b0),
            .CLKIN(CLK), // 50.0 MHz
            .CLKOUT(clk), // 26.923076923076923 MHz
            .LOCK(lock)
        );
			/*
			localparam slow_bits = SLOW;

			reg [SLOW:0] slow_CLK = 0;
			always @(posedge CLK) begin
				slow_CLK <= slow_CLK + 1;
			end
			assign clk = slow_CLK[slow_bits];
			*/

		end else begin
			assign clk = CLK;
		end
	endgenerate
endmodule

