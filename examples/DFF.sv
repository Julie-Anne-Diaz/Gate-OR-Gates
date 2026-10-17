// Rising-edge D flip-flop. No reset: initial Q is unspecified.
module DFF(input logic D, CLK, output logic Q);
    always_ff @(posedge CLK)
        Q <= D;
endmodule
