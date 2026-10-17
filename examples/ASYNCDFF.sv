// Rising-edge D flip-flop with asynchronous, active-high reset to zero.
// Port names match the supplied Minecraft template.
module ASYNCDFF(input logic A, CLK, RESET, output logic Y);
    always_ff @(posedge CLK or posedge RESET)
        if (RESET) Y <= 1'b0;
        else Y <= A;
endmodule
