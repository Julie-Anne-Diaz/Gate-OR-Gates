// Abhiram Pinnity
// Description: Testbench for 4-bit Ripple Carry Adder

module Ripple_Carry_Adder_tb;

    logic in1, in2, in3, in4;
    logic in5, in6, in7, in8;
    logic C_in;
    logic C_out;
    logic [3:0] out1;

    integer errors = 0;

    // Instantiate the DUT
    Ripple_Carry_Adder dut (
        .in1(in1),
        .in2(in2),
        .in3(in3),
        .in4(in4),
        .in5(in5),
        .in6(in6),
        .in7(in7),
        .in8(in8),
        .C_in(C_in),
        .C_out(C_out),
        .out1(out1)
    );

    initial begin

        // Test 1: 3 + 2 = 5
        // First number: 0011
        // Second number: 0010
        {in7, in5, in3, in1} = 4'b0011;
        {in8, in6, in4, in2} = 4'b0010;
        C_in = 0;
        #1;
        assert ({C_out, out1} == 5'd5)
        else begin
            $error("Test 1 failed: 3 + 2");
            errors++;
        end

        // Test 2: 15 + 1 = 16 (carry out)
        {in7, in5, in3, in1} = 4'b1111;
        {in8, in6, in4, in2} = 4'b0001;
        C_in = 0;
        #1;
        assert ({C_out, out1} == 5'd16)
        else begin
            $error("Test 2 failed: 15 + 1");
            errors++;
        end

        // Test 3: 7 + 4 = 11
        {in7, in5, in3, in1} = 4'b0111;
        {in8, in6, in4, in2} = 4'b0100;
        C_in = 0;
        #1;
        assert ({C_out, out1} == 5'd11)
        else begin
            $error("Test 3 failed: 7 + 4");
            errors++;
        end

        // Test 4: 6 + 5 + carry-in = 12
        {in7, in5, in3, in1} = 4'b0110;
        {in8, in6, in4, in2} = 4'b0101;
        C_in = 1;
        #1;
        assert ({C_out, out1} == 5'd12)
        else begin
            $error("Test 4 failed: 6 + 5 + carry-in");
            errors++;
        end

        // Test 5: 0 + 0 = 0
        {in7, in5, in3, in1} = 4'b0000;
        {in8, in6, in4, in2} = 4'b0000;
        C_in = 0;
        #1;
        assert ({C_out, out1} == 5'd0)
        else begin
            $error("Test 5 failed: 0 + 0");
            errors++;
        end

        // Test 6: 15 + 15 = 30
        {in7, in5, in3, in1} = 4'b1111;
        {in8, in6, in4, in2} = 4'b1111;
        C_in = 0;
        #1;
        assert ({C_out, out1} == 5'd30)
        else begin
            $error("Test 6 failed: 15 + 15");
            errors++;
        end

        // Print final result
        if (errors == 0)
            $display("ALL TESTS PASSED!");
        else
            $display("TESTS FAILED! Total failures: %0d", errors);

        $finish;
    end

    // Timeout protection
    initial begin
        #100;
        $fatal(1, "Testbench timeout");
    end

endmodule