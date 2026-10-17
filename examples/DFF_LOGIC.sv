// Data logic -> clocked storage -> output logic, using one integrated clock.
module DFF_LOGIC(
    input logic a, b, c,
    input logic CLK, RESET,
    output logic Y
);
    logic stored;
    always_ff @(posedge CLK or posedge RESET)
        if (RESET) stored <= 1'b0;
        else stored <= a & b;
    assign Y = stored | c;
endmodule
