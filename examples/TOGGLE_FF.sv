// Register feedback is legal; combinational feedback is still rejected.
module TOGGLE_FF(input logic CLK, RESET, output logic Q);
    always_ff @(posedge CLK or posedge RESET)
        if (RESET) Q <= 1'b0;
        else Q <= ~Q;
endmodule
