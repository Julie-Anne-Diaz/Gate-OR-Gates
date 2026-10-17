// Abhiram Pinnity
// Description: TB to test structurally combined 8-input gate logic

module ALL_GATES_8in_tb #(
    parameter WIDTH = 4
);
    logic [WIDTH-1:0] in1, in2, in3, in4;
    logic [WIDTH-1:0] in5, in6, in7, in8;
    logic [WIDTH-1:0] out_AND, out_OR, out_NOT;
    logic [WIDTH-1:0] out_NAND, out_NOR, out_XOR, out_XNOR;
    integer errors = 0;

    ALL_GATES_8in #(.WIDTH(WIDTH)) dut (
        .in1(in1),
        .in2(in2),
        .in3(in3),
        .in4(in4),
        .in5(in5),
        .in6(in6),
        .in7(in7),
        .in8(in8),
        .out_AND(out_AND),
        .out_OR(out_OR),
        .out_NOT(out_NOT),
        .out_NAND(out_NAND),
        .out_NOR(out_NOR),
        .out_XOR(out_XOR),
        .out_XNOR(out_XNOR)
    );

    initial begin
        // Initialize all inputs
        in1 = '0;
        in2 = '0;
        in3 = '0;
        in4 = '0;
        in5 = '0;
        in6 = '0;
        in7 = '0;
        in8 = '0;

        // Test 1: All inputs are 0000
        #1;

        assert (out_AND === (in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("AND failed: expected 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("OR failed: expected 0000");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT failed: expected 1111");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("NAND failed: expected 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("NOR failed: expected 1111");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XOR failed: expected 0000");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XNOR failed: expected 1111");
                errors++;
            end

        // Test 2: Only in1 is 0001
        #1;
        in1 = 4'b0001;

        #1;
        assert (out_AND === (in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("AND failed: expected 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("OR failed: expected 0001");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT failed: expected 1110");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("NAND failed: expected 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("NOR failed: expected 1110");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XOR failed: expected 0001");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XNOR failed: expected 1110");
                errors++;
            end

        // Test 3: Only in2 is 0001
        #1;
        in1 = 4'b0000;
        in2 = 4'b0001;

        #1;
        assert (out_AND === (in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("AND failed: expected 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("OR failed: expected 0001");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT failed: expected 1111");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("NAND failed: expected 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("NOR failed: expected 1110");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XOR failed: expected 0001");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XNOR failed: expected 1110");
                errors++;
            end

        // Test 4: in1 and in2 are 0001; remaining inputs are 0000
        #1;
        in1 = 4'b0001;
        in2 = 4'b0001;

        #1;
        assert (out_AND === (in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("AND failed: expected 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("OR failed: expected 0001");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT failed: expected 1110");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("NAND failed: expected 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("NOR failed: expected 1110");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XOR failed: expected 0000");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XNOR failed: expected 1111");
                errors++;
            end

        // Test 5: in1 = 1001; all other inputs = 1111
        #1;
        in1 = 4'b1001;
        in2 = 4'b1111;
        in3 = 4'b1111;
        in4 = 4'b1111;
        in5 = 4'b1111;
        in6 = 4'b1111;
        in7 = 4'b1111;
        in8 = 4'b1111;

        #1;
        assert (out_AND === (in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("AND failed: expected 1001");
                errors++;
            end
        assert (out_OR === (in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("OR failed: expected 1111");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT failed: expected 0110");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8))
            else begin
                $error("NAND failed: expected 0110");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2 | in3 | in4 | in5 | in6 | in7 | in8))
            else begin
                $error("NOR failed: expected 0000");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XOR failed: expected 0110");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8))
            else begin
                $error("XNOR failed: expected 1001");
                errors++;
            end

        #1;

        // Print final test result
        if (errors == 0)
            $display("ALL TESTS PASSED!");
        else
            $display("TESTS FAILED! Total failures: %0d", errors);

        $finish;
    end

    // Safety timeout
    initial begin
        #1000;
        $fatal(1, "Testbench timeout");
    end

endmodule