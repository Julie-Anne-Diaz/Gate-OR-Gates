// Two independent local clocks sample the inputs into separate DFFs.
// Hold A/B steady until both registers capture; the result then equals A+B.
// Read result as {result[1], result[0]} = {carry, sum}.
module REGISTERED_HALF_ADDER(
    input logic A, B,
    input logic CLK_A, CLK_B, RESET,
    output logic [1:0] result
);
    logic stored_a, stored_b;
    always_ff @(posedge CLK_A or posedge RESET)
        if (RESET) stored_a <= 1'b0;
        else stored_a <= A;
    always_ff @(posedge CLK_B or posedge RESET)
        if (RESET) stored_b <= 1'b0;
        else stored_b <= B;
    assign result = {stored_a & stored_b, stored_a ^ stored_b};
endmodule
