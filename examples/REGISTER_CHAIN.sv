// Two registers share a clock: Y[1] receives the PREVIOUS Y[0].
module REGISTER_CHAIN(input logic A, CLK, RESET, output logic [1:0] Y);
    ASYNCDFF first (.A(A),    .CLK(CLK), .RESET(RESET), .Y(Y[0]));
    ASYNCDFF second(.A(Y[0]), .CLK(CLK), .RESET(RESET), .Y(Y[1]));
endmodule
